import hashlib
import logging
import re
from datetime import datetime, timezone
from typing import Optional

import feedparser
import httpx

from app.providers.dashboard_base import DashboardNewsProvider, DashboardProviderError

logger = logging.getLogger(__name__)

# One public RSS feed per supported category. No API key required.
_FEED_URLS: dict[str, str] = {
    "breaking": "https://feeds.bbci.co.uk/news/rss.xml",
    "domestic_us": "https://feeds.npr.org/1001/rss.xml",
    "foreign_world": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "markets_stocks": "https://feeds.reuters.com/reuters/businessNews",
    "tech_ai": "https://techcrunch.com/feed/",
}

_FEED_SOURCE_NAMES: dict[str, str] = {
    "breaking": "BBC News",
    "domestic_us": "NPR",
    "foreign_world": "BBC World",
    "markets_stocks": "Reuters Business",
    "tech_ai": "TechCrunch",
}

# Baseline credibility per RSS source used above.
_SOURCE_CREDIBILITY: dict[str, float] = {
    "BBC News": 0.92,
    "BBC World": 0.92,
    "NPR": 0.90,
    "Reuters Business": 0.93,
    "TechCrunch": 0.80,
}

_DEFAULT_FETCH_LIMIT = 10
_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    return _TAG_RE.sub("", text).strip()


def _parse_published(entry) -> str:
    for attr in ("published_parsed", "updated_parsed"):
        pt = getattr(entry, attr, None)
        if pt:
            try:
                dt = datetime(*pt[:6], tzinfo=timezone.utc)
                return dt.isoformat()
            except Exception:
                pass
    return datetime.now(timezone.utc).isoformat()


def _freshness_score(published_at: str) -> float:
    try:
        ts = published_at.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age_hours = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    except Exception:
        return 0.50
    if age_hours < 1:
        return 0.99
    if age_hours < 6:
        return 0.90
    if age_hours < 24:
        return 0.75
    if age_hours < 72:
        return 0.55
    return 0.35


class DashboardLiveProvider(DashboardNewsProvider):
    """
    Live news provider that reads public RSS feeds — no API key required.

    Feed map (DASHBOARD_NEWS_PROVIDER=live):
        breaking       → BBC News top news
        domestic_us    → NPR All Things Considered
        foreign_world  → BBC World News
        markets_stocks → Reuters Business News
        tech_ai        → TechCrunch

    Scores are estimated heuristically (credibility from source, freshness from
    publication date). importance / relevance / source_diversity use fixed
    reasonable defaults until a scoring model is integrated.

    On any network or parse failure DashboardProviderError is raised; DashboardService
    will log a warning and fall back to DashboardFixturesProvider automatically.
    """

    def __init__(self, timeout: float = 8.0) -> None:
        self._timeout = timeout

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def fetch(self, category: str) -> list[dict]:
        url = _FEED_URLS.get(category)
        if not url:
            raise DashboardProviderError(
                f"No RSS feed configured for category '{category}'. "
                f"Supported: {sorted(_FEED_URLS)}"
            )
        source_name = _FEED_SOURCE_NAMES.get(category, "Unknown Source")

        raw_xml = self._fetch_raw(url)

        try:
            feed = feedparser.parse(raw_xml)
        except Exception as exc:
            raise DashboardProviderError(
                f"Failed to parse RSS feed for '{category}': {exc}"
            ) from exc

        articles: list[dict] = []
        for entry in feed.entries[:_DEFAULT_FETCH_LIMIT]:
            article = self._entry_to_article(entry, category, source_name)
            if article is not None:
                articles.append(article)

        logger.info(
            "DashboardLiveProvider: fetched %d articles for category '%s'.",
            len(articles),
            category,
        )
        return articles

    # ------------------------------------------------------------------
    # Internal helpers — _fetch_raw is the seam for unit tests
    # ------------------------------------------------------------------

    def _fetch_raw(self, url: str) -> str:
        """Fetch RSS XML with timeout. Patch this method in tests to avoid network calls."""
        try:
            response = httpx.get(
                url,
                timeout=self._timeout,
                follow_redirects=True,
                headers={"User-Agent": "TheGiver/1.0"},
            )
            response.raise_for_status()
            return response.text
        except Exception as exc:
            raise DashboardProviderError(
                f"Failed to fetch RSS feed from {url!r}: {exc}"
            ) from exc

    def _entry_to_article(
        self,
        entry,
        category: str,
        source_name: str,
    ) -> Optional[dict]:
        title = _strip_html(getattr(entry, "title", "") or "")
        if not title:
            return None

        raw_summary = (
            getattr(entry, "summary", "")
            or getattr(entry, "description", "")
            or ""
        )
        summary = _strip_html(raw_summary)[:600]
        if not summary:
            summary = f"Live article from {source_name}."

        link = getattr(entry, "link", "") or ""
        guid = getattr(entry, "id", link) or link
        article_id = "live_" + hashlib.md5(guid.encode()).hexdigest()[:12]

        published_at = _parse_published(entry)
        freshness = _freshness_score(published_at)
        credibility = _SOURCE_CREDIBILITY.get(source_name, 0.70)

        return {
            "id": article_id,
            "headline": title,
            "source": source_name,
            "category": category,
            "published_at": published_at,
            "neutral_summary": summary,
            "importance_score": 0.75,
            "credibility_score": credibility,
            "relevance_score": 0.80,
            "freshness_score": freshness,
            "source_diversity_score": 0.65,
            "framing_label": "mostly_neutral",
            "key_claims": [],
            "support_summary": f"Live article sourced from {source_name} RSS feed.",
            "contradiction_warnings": [],
            "why_selected": (
                f"Selected from live {source_name} RSS feed for '{category}' category."
            ),
        }
