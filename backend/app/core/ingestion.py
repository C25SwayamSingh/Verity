"""Ingestion classification for the core checker.

The Giver analyzes *analyzable text* (pasted text, article text, transcripts,
source notes) — never a raw social/video URL string. This module decides what
kind of submission we received and whether real analyzable text is present.

It does NOT download, scrape, or fetch anything from a URL.
"""

import re
from dataclasses import dataclass, field
from typing import Optional

URL_RE = re.compile(r"https?://[^\s<>\"')]+", re.IGNORECASE)
BARE_DOMAIN_RE = re.compile(
    r"\b(?:www\.)?[a-z0-9-]+\.(?:com|org|net|io|gov|co|tv|watch|be)\b[^\s]*",
    re.IGNORECASE,
)

# Social / short-form video platforms whose links are metadata only — there is
# no analyzable text to extract without an uploaded recording or a transcript.
SOCIAL_VIDEO_DOMAINS = (
    "instagram.com",
    "tiktok.com",
    "youtube.com",
    "youtu.be",
    "facebook.com",
    "fb.watch",
    "twitter.com",
    "x.com",
    "reddit.com",
    "snapchat.com",
    "twitch.tv",
    "vimeo.com",
    "threads.net",
)

# Minimum residual text (after removing URLs) that counts as analyzable.
_MIN_ANALYZABLE_CHARS = 25
_MIN_ANALYZABLE_WORDS = 5

INGEST_PASTED_TEXT = "pasted_text"
INGEST_ARTICLE_URL = "article_url"
INGEST_SOCIAL_VIDEO_URL = "social_video_url"
INGEST_TRANSCRIPT_TEXT = "transcript_text"
INGEST_SOURCE_NOTES = "source_notes"


@dataclass
class IngestionClassification:
    ingestion_type: str
    analyzable: bool
    needs_more_input: bool
    analyzable_text: str
    source_links: list[str] = field(default_factory=list)
    guidance: Optional[str] = None
    transparency_note: Optional[str] = None


def extract_urls(text: str) -> list[str]:
    urls = URL_RE.findall(text or "")
    # Also catch bare domains (e.g. "instagram.com/reel/..") with no scheme.
    if not urls:
        urls = [m.group(0) for m in BARE_DOMAIN_RE.finditer(text or "")]
    # Trim common trailing punctuation.
    return [u.rstrip(".,);]") for u in urls]


def _host(url: str) -> str:
    cleaned = re.sub(r"^https?://", "", url.strip(), flags=re.IGNORECASE)
    cleaned = cleaned.split("/", 1)[0]
    return cleaned.lower().lstrip("www.")


def is_social_video_url(url: str) -> bool:
    host = _host(url)
    return any(host == d or host.endswith("." + d) or host == d.lstrip("www.") for d in SOCIAL_VIDEO_DOMAINS)


def _residual_text(text: str, urls: list[str]) -> str:
    residual = URL_RE.sub(" ", text or "")
    residual = BARE_DOMAIN_RE.sub(" ", residual)
    return re.sub(r"\s+", " ", residual).strip()


def has_analyzable_text(residual: str) -> bool:
    if len(residual) < _MIN_ANALYZABLE_CHARS:
        return False
    words = [w for w in re.split(r"\s+", residual) if any(ch.isalpha() for ch in w)]
    return len(words) >= _MIN_ANALYZABLE_WORDS


SOCIAL_LINK_ONLY_GUIDANCE = (
    "We found a video link, but no transcript or analyzable text was provided. "
    "Upload the video, screen recording, or audio, paste a transcript or captions, "
    "or add source notes so The Giver can analyze the actual content. "
    "The Giver does not download or scrape social videos."
)

ARTICLE_LINK_ONLY_GUIDANCE = (
    "We found a link, but no analyzable text was provided. "
    "Paste the article text, a transcript, or source notes so The Giver can analyze the content. "
    "The Giver does not fetch or scrape pages from a link alone."
)


def classify_ingestion(text: str) -> IngestionClassification:
    """Classify a checker submission and decide whether it is analyzable.

    Link-only submissions (no analyzable text besides a URL) return
    ``needs_more_input=True`` so the pipeline does not treat the URL as content.
    """
    raw = (text or "").strip()
    urls = extract_urls(raw)
    residual = _residual_text(raw, urls)
    analyzable = has_analyzable_text(residual)
    social_links = [u for u in urls if is_social_video_url(u)]

    if analyzable:
        # Real text present. Any links are kept as source metadata only.
        return IngestionClassification(
            ingestion_type=INGEST_PASTED_TEXT,
            analyzable=True,
            needs_more_input=False,
            analyzable_text=raw,
            source_links=urls,
        )

    if not urls:
        # No URL and not enough text — let normal validation/short text path run.
        return IngestionClassification(
            ingestion_type=INGEST_PASTED_TEXT,
            analyzable=True,
            needs_more_input=False,
            analyzable_text=raw,
            source_links=[],
        )

    # Link-only submission: do NOT analyze the URL string itself.
    if social_links:
        return IngestionClassification(
            ingestion_type=INGEST_SOCIAL_VIDEO_URL,
            analyzable=False,
            needs_more_input=True,
            analyzable_text="",
            source_links=urls,
            guidance=SOCIAL_LINK_ONLY_GUIDANCE,
            transparency_note=(
                "Link stored as source metadata only — The Giver did not download, "
                "scrape, or transcribe the linked video."
            ),
        )

    return IngestionClassification(
        ingestion_type=INGEST_ARTICLE_URL,
        analyzable=False,
        needs_more_input=True,
        analyzable_text="",
        source_links=urls,
        guidance=ARTICLE_LINK_ONLY_GUIDANCE,
        transparency_note=(
            "Link stored as source metadata only — The Giver did not fetch or scrape the page."
        ),
    )
