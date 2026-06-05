"""Optional open news provider backed by the GDELT 2.0 DOC API.

GDELT is a free, open, key-free global news index. We use its DOC 2.0 article
search (``mode=ArtList&format=json``) to pull recent articles per category.

Enable with ``DASHBOARD_NEWS_PROVIDER=gdelt``. No API key is required. On any
network or parse failure this provider raises ``DashboardProviderError`` and
``DashboardService`` falls back to the fixtures provider automatically — so a
missing network or a GDELT outage never crashes the app.

Like the RSS live provider, GDELT supplies headline / source / time but not
integrity scores. importance / relevance / source_diversity use conservative
fixed defaults; credibility is estimated from the publishing domain and
freshness from the article's seen-date, until a real scoring model is added.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlencode

import httpx

from app.providers.dashboard_base import DashboardNewsProvider, DashboardProviderError

logger = logging.getLogger(__name__)

_GDELT_DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

# A focused search query per supported category. GDELT searches article text.
_CATEGORY_QUERIES: dict[str, str] = {
    "breaking": "(breaking OR developing) sourcelang:english",
    "domestic_us": "(United States OR Congress OR White House) sourcecountry:US sourcelang:english",
    "foreign_world": "(world OR international OR global) sourcelang:english",
    "markets_stocks": "(stocks OR markets OR economy OR inflation) sourcelang:english",
    "tech_ai": "(artificial intelligence OR technology OR software) sourcelang:english",
}

# Rough per-domain credibility priors. Unknown domains get a neutral default so
# we never imply a verdict about an unfamiliar outlet.
_DOMAIN_CREDIBILITY: dict[str, float] = {
    "reuters.com": 0.93,
    "apnews.com": 0.93,
    "bbc.com": 0.92,
    "bbc.co.uk": 0.92,
    "npr.org": 0.90,
    "theguardian.com": 0.88,
    "nytimes.com": 0.88,
    "washingtonpost.com": 0.87,
    "bloomberg.com": 0.88,
    "wsj.com": 0.88,
    "cnbc.com": 0.82,
    "techcrunch.com": 0.80,
    "theverge.com": 0.80,
}
_DEFAULT_CREDIBILITY = 0.70

_DEFAULT_FETCH_LIMIT = 15
_DEFAULT_TIMEOUT = 8.0


def _parse_seendate(seendate: str) -> str:
    """GDELT seendate format: 'YYYYMMDDTHHMMSSZ' → ISO 8601."""
    try:
        dt = datetime.strptime(seendate, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except (ValueError, TypeError):
        return datetime.now(timezone.utc).isoformat()


def _freshness_score(published_at: str) -> float:
    try:
        dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
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


class DashboardGdeltProvider(DashboardNewsProvider):
    def __init__(self, timeout: float = _DEFAULT_TIMEOUT, limit: int = _DEFAULT_FETCH_LIMIT) -> None:
        self._timeout = timeout
        self._limit = limit

    def fetch(self, category: str) -> list[dict]:
        query = _CATEGORY_QUERIES.get(category)
        if not query:
            raise DashboardProviderError(
                f"No GDELT query configured for category '{category}'. "
                f"Supported: {sorted(_CATEGORY_QUERIES)}"
            )

        raw = self._fetch_raw(query)
        try:
            payload = json.loads(raw) if isinstance(raw, str) else raw
        except (ValueError, TypeError) as exc:
            raise DashboardProviderError(f"Failed to parse GDELT response: {exc}") from exc

        entries = (payload or {}).get("articles", [])
        articles: list[dict] = []
        for entry in entries[: self._limit]:
            article = self._entry_to_article(entry, category)
            if article is not None:
                articles.append(article)

        logger.info("DashboardGdeltProvider: %d articles for '%s'.", len(articles), category)
        return articles

    # ------------------------------------------------------------------
    # Network seam — patch in tests to avoid live calls.
    # ------------------------------------------------------------------

    def _fetch_raw(self, query: str) -> str:
        params = {
            "query": query,
            "mode": "ArtList",
            "format": "json",
            "maxrecords": str(self._limit),
            "sort": "DateDesc",
        }
        url = f"{_GDELT_DOC_URL}?{urlencode(params)}"
        try:
            response = httpx.get(
                url,
                timeout=self._timeout,
                follow_redirects=True,
                headers={"User-Agent": "Verity/1.0"},
            )
            response.raise_for_status()
            return response.text
        except Exception as exc:
            raise DashboardProviderError(f"Failed to fetch GDELT feed: {exc}") from exc

    def _entry_to_article(self, entry: dict, category: str) -> Optional[dict]:
        title = (entry.get("title") or "").strip()
        if not title:
            return None

        domain = (entry.get("domain") or "").strip().lower()
        source_name = entry.get("sourcecommonname") or domain or "Unknown Source"
        url = entry.get("url") or ""
        published_at = _parse_seendate(entry.get("seendate") or "")

        guid = url or title
        article_id = "gdelt_" + hashlib.md5(guid.encode()).hexdigest()[:12]

        credibility = _DOMAIN_CREDIBILITY.get(domain, _DEFAULT_CREDIBILITY)
        freshness = _freshness_score(published_at)

        return {
            "id": article_id,
            "headline": title,
            "source": source_name,
            "category": category,
            "published_at": published_at,
            "neutral_summary": f"Indexed by GDELT from {source_name}. Open the source for full text.",
            "importance_score": 0.70,
            "credibility_score": credibility,
            "relevance_score": 0.78,
            "freshness_score": freshness,
            "source_diversity_score": 0.60,
            "framing_label": "mostly_neutral",
            "key_claims": [],
            "support_summary": (
                f"Surfaced from the open GDELT index via {source_name}; "
                "corroboration not independently scored."
            ),
            "contradiction_warnings": [],
            "why_selected": (
                f"Selected from the open GDELT global news index for '{category}'."
            ),
        }
