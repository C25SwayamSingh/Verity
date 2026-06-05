"""Extract readable article text from a normal article URL.

This is for *article* pages (news sites, blogs) shared as a link — it fetches
the page the user shared and pulls the main body text so the checker analyzes
real content instead of the URL string.

It does NOT apply to social/video platforms (Instagram/TikTok/YouTube): those
pages carry no analyzable article text and downloading their media is out of
scope. Social links continue to require an upload or transcript.
"""

import logging
from dataclasses import dataclass
from typing import Callable, Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

try:  # optional dependency — feature degrades gracefully if missing
    import trafilatura
    from trafilatura import extract_metadata
except ImportError:  # pragma: no cover
    trafilatura = None
    extract_metadata = None

_USER_AGENT = (
    "Mozilla/5.0 (compatible; Verity/1.0; +https://verity.app) "
    "article-text-extractor"
)


@dataclass
class FetchedPage:
    url: str
    html: str
    content_type: str = "text/html"


@dataclass
class ExtractedArticle:
    url: str
    title: str
    text: str


Fetcher = Callable[[str], Optional[FetchedPage]]


class ArticleExtractionService:
    """Fetch an article URL and extract its main text.

    The ``fetcher`` is injectable so tests never touch the network.
    """

    def __init__(self, fetcher: Optional[Fetcher] = None) -> None:
        self._settings = get_settings()
        self._fetcher = fetcher or self._default_fetch

    @property
    def available(self) -> bool:
        return bool(self._settings.article_extraction_enabled and trafilatura is not None)

    def extract(self, url: str) -> Optional[ExtractedArticle]:
        if not self.available:
            return None
        try:
            page = self._fetcher(url)
        except Exception as exc:  # noqa: BLE001 - network errors are expected/non-fatal
            logger.info("Article fetch failed for %s: %s", url, exc)
            return None
        if page is None or not page.html:
            return None
        return self._parse(page)

    def _parse(self, page: FetchedPage) -> Optional[ExtractedArticle]:
        try:
            text = trafilatura.extract(
                page.html,
                include_comments=False,
                include_tables=False,
                favor_recall=True,
                url=page.url,
            )
        except Exception as exc:  # noqa: BLE001
            logger.info("Article extraction failed for %s: %s", page.url, exc)
            return None

        if not text or len(text.strip()) < self._settings.article_extraction_min_chars:
            return None

        title = ""
        if extract_metadata is not None:
            try:
                meta = extract_metadata(page.html)
                if meta and getattr(meta, "title", None):
                    title = str(meta.title).strip()
            except Exception:  # noqa: BLE001 - title is best-effort
                title = ""

        return ExtractedArticle(url=page.url, title=title, text=text.strip())

    def _default_fetch(self, url: str) -> Optional[FetchedPage]:
        timeout = self._settings.article_extraction_timeout_seconds
        max_bytes = self._settings.article_extraction_max_bytes
        with httpx.Client(
            follow_redirects=True,
            timeout=timeout,
            headers={"User-Agent": _USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
        ) as client:
            with client.stream("GET", url) as resp:
                resp.raise_for_status()
                content_type = resp.headers.get("content-type", "")
                if "html" not in content_type.lower():
                    return None
                chunks: list[bytes] = []
                total = 0
                for chunk in resp.iter_bytes():
                    chunks.append(chunk)
                    total += len(chunk)
                    if total > max_bytes:
                        break
                raw = b"".join(chunks)
        try:
            html = raw.decode(resp.encoding or "utf-8", errors="replace")
        except (LookupError, TypeError):
            html = raw.decode("utf-8", errors="replace")
        return FetchedPage(url=str(resp.url), html=html, content_type=content_type)
