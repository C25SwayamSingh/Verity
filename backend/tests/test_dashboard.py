"""
Dashboard tests — three layers:
  1. HTTP endpoint tests (via FastAPI TestClient)
  2. Provider unit tests (DashboardFixturesProvider, DashboardLiveProvider)
  3. Registry + service tests (injection, fallback behaviour)
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.providers.dashboard_base import DashboardNewsProvider, DashboardProviderError
from app.providers.dashboard_fixtures_provider import DashboardFixturesProvider
from app.providers.dashboard_live_provider import (
    DashboardLiveProvider,
    _freshness_score,
    _parse_published,
    _strip_html,
)
from app.providers.dashboard_registry import get_dashboard_provider
from app.services.dashboard_service import SUPPORTED_CATEGORIES, DashboardService, _compute_final_score

client = TestClient(app)

SCORE_FIELDS = [
    "importance_score",
    "credibility_score",
    "relevance_score",
    "freshness_score",
    "source_diversity_score",
]

# Minimal valid RSS XML returned by mock — contains 3 articles.
_MOCK_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Mock Feed</title>
    <item>
      <title>Story One: Central Bank Holds Rates</title>
      <link>https://example.com/story-1</link>
      <description>Officials left rates unchanged citing persistent inflation pressures.</description>
      <pubDate>Wed, 03 Jun 2026 14:00:00 GMT</pubDate>
      <guid>https://example.com/story-1</guid>
    </item>
    <item>
      <title>Story Two: Parliament Passes Budget</title>
      <link>https://example.com/story-2</link>
      <description>Lawmakers approved the annual budget after a lengthy debate.</description>
      <pubDate>Wed, 03 Jun 2026 12:00:00 GMT</pubDate>
      <guid>https://example.com/story-2</guid>
    </item>
    <item>
      <title>Story Three: Tech Conference Opens</title>
      <link>https://example.com/story-3</link>
      <description>Leading technology firms gathered at the annual summit.</description>
      <pubDate>Wed, 03 Jun 2026 10:00:00 GMT</pubDate>
      <guid>https://example.com/story-3</guid>
    </item>
  </channel>
</rss>"""


# ---------------------------------------------------------------------------
# 1. HTTP endpoint tests — unchanged behaviour
# ---------------------------------------------------------------------------

def test_dashboard_default_category():
    r = client.get("/v1/dashboard/articles")
    assert r.status_code == 200
    data = r.json()
    assert data["category"] == "breaking"
    assert len(data["articles"]) == 5


def test_dashboard_all_supported_categories():
    for cat in SUPPORTED_CATEGORIES:
        r = client.get(f"/v1/dashboard/articles?category={cat}")
        assert r.status_code == 200, f"Failed for category: {cat}"
        data = r.json()
        assert data["category"] == cat
        articles = data["articles"]
        assert 1 <= len(articles) <= 5
        for a in articles:
            assert a["category"] == cat


def test_dashboard_returns_at_most_five():
    r = client.get("/v1/dashboard/articles?category=tech_ai")
    assert r.status_code == 200
    assert len(r.json()["articles"]) <= 5


def test_dashboard_article_fields_present():
    r = client.get("/v1/dashboard/articles?category=markets_stocks")
    assert r.status_code == 200
    article = r.json()["articles"][0]
    required_fields = [
        "id", "headline", "source", "category", "published_at",
        "neutral_summary", "importance_score", "credibility_score",
        "relevance_score", "freshness_score", "source_diversity_score",
        "final_score", "framing_label", "key_claims",
        "support_summary", "contradiction_warnings", "why_selected",
    ]
    for field in required_fields:
        assert field in article, f"Missing field: {field}"


def test_dashboard_articles_sorted_by_final_score():
    for cat in SUPPORTED_CATEGORIES:
        r = client.get(f"/v1/dashboard/articles?category={cat}")
        assert r.status_code == 200
        articles = r.json()["articles"]
        scores = [a["final_score"] for a in articles]
        assert scores == sorted(scores, reverse=True), (
            f"Articles not sorted for category '{cat}': {scores}"
        )


def test_dashboard_final_score_formula():
    r = client.get("/v1/dashboard/articles?category=breaking")
    assert r.status_code == 200
    for article in r.json()["articles"]:
        expected = round(
            0.35 * article["importance_score"]
            + 0.30 * article["credibility_score"]
            + 0.20 * article["relevance_score"]
            + 0.10 * article["freshness_score"]
            + 0.05 * article["source_diversity_score"],
            4,
        )
        assert abs(article["final_score"] - expected) < 1e-3, (
            f"Score mismatch for {article['id']}: got {article['final_score']}, expected {expected}"
        )


def test_dashboard_score_range():
    for cat in SUPPORTED_CATEGORIES:
        r = client.get(f"/v1/dashboard/articles?category={cat}")
        for article in r.json()["articles"]:
            for field in SCORE_FIELDS + ["final_score"]:
                val = article[field]
                assert 0.0 <= val <= 1.0, (
                    f"Score out of range for {article['id']}.{field}: {val}"
                )


def test_dashboard_invalid_category():
    r = client.get("/v1/dashboard/articles?category=other")
    assert r.status_code == 422

    r2 = client.get("/v1/dashboard/articles?category=nonexistent")
    assert r2.status_code == 422


def test_compute_final_score_formula():
    sample = {
        "importance_score": 0.80,
        "credibility_score": 0.90,
        "relevance_score": 0.70,
        "freshness_score": 0.60,
        "source_diversity_score": 0.50,
    }
    expected = round(0.35 * 0.80 + 0.30 * 0.90 + 0.20 * 0.70 + 0.10 * 0.60 + 0.05 * 0.50, 4)
    assert _compute_final_score(sample) == expected


# ---------------------------------------------------------------------------
# 2. Fixtures provider unit tests
# ---------------------------------------------------------------------------

def test_fixtures_provider_returns_articles_for_each_category():
    provider = DashboardFixturesProvider()
    for cat in SUPPORTED_CATEGORIES:
        articles = provider.fetch(cat)
        assert len(articles) >= 1, f"No fixture articles for category '{cat}'"
        assert all(a["category"] == cat for a in articles)


def test_fixtures_provider_returns_empty_for_unknown_category():
    provider = DashboardFixturesProvider()
    assert provider.fetch("nonexistent") == []


# ---------------------------------------------------------------------------
# 3. Live provider unit tests — all network calls are mocked
# ---------------------------------------------------------------------------

def _make_live_provider_with_mock_feed(mock_xml: str = _MOCK_RSS) -> DashboardLiveProvider:
    """Return a DashboardLiveProvider whose _fetch_raw is patched to return mock_xml."""
    provider = DashboardLiveProvider()
    provider._fetch_raw = lambda url: mock_xml  # type: ignore[method-assign]
    return provider


def test_live_provider_returns_articles_from_mocked_feed():
    provider = _make_live_provider_with_mock_feed()
    articles = provider.fetch("breaking")
    assert len(articles) == 3
    assert all(a["category"] == "breaking" for a in articles)


def test_live_provider_article_has_all_required_fields():
    provider = _make_live_provider_with_mock_feed()
    article = provider.fetch("breaking")[0]
    required = [
        "id", "headline", "source", "category", "published_at",
        "neutral_summary", "importance_score", "credibility_score",
        "relevance_score", "freshness_score", "source_diversity_score",
        "framing_label", "key_claims", "support_summary",
        "contradiction_warnings", "why_selected",
    ]
    for field in required:
        assert field in article, f"Missing field: {field}"


def test_live_provider_article_score_ranges_valid():
    provider = _make_live_provider_with_mock_feed()
    for article in provider.fetch("breaking"):
        for field in SCORE_FIELDS:
            assert 0.0 <= article[field] <= 1.0, f"{field} out of range"


def test_live_provider_article_id_is_stable():
    """Same RSS entry must always produce the same article id (MD5 of guid)."""
    provider = _make_live_provider_with_mock_feed()
    articles_a = provider.fetch("breaking")
    articles_b = provider.fetch("breaking")
    assert [a["id"] for a in articles_a] == [a["id"] for a in articles_b]


def test_live_provider_article_id_has_live_prefix():
    provider = _make_live_provider_with_mock_feed()
    for article in provider.fetch("breaking"):
        assert article["id"].startswith("live_")


def test_live_provider_raises_on_fetch_error():
    provider = DashboardLiveProvider()

    def _fail(url: str) -> str:
        raise DashboardProviderError("Connection timed out")

    provider._fetch_raw = _fail  # type: ignore[method-assign]
    with pytest.raises(DashboardProviderError, match="Connection timed out"):
        provider.fetch("breaking")


def test_live_provider_raises_for_unconfigured_category():
    provider = _make_live_provider_with_mock_feed()
    with pytest.raises(DashboardProviderError, match="No RSS feed configured"):
        provider.fetch("other")


def test_live_provider_skips_entries_with_no_title():
    empty_title_rss = """<?xml version="1.0"?>
<rss version="2.0"><channel>
  <item><title></title><link>https://example.com/x</link><guid>x</guid></item>
  <item><title>Valid Title</title><link>https://example.com/y</link><guid>y</guid></item>
</channel></rss>"""
    provider = _make_live_provider_with_mock_feed(empty_title_rss)
    articles = provider.fetch("breaking")
    assert len(articles) == 1
    assert articles[0]["headline"] == "Valid Title"


# ---------------------------------------------------------------------------
# 4. Freshness / parse helpers
# ---------------------------------------------------------------------------

def test_strip_html():
    assert _strip_html("<p>Hello <b>World</b></p>") == "Hello World"
    assert _strip_html("No tags here") == "No tags here"


def test_freshness_score_very_recent():
    recent = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
    assert _freshness_score(recent) == 0.99


def test_freshness_score_old_article():
    old = "2020-01-01T00:00:00+00:00"
    assert _freshness_score(old) == 0.35


def test_freshness_score_bad_string_returns_default():
    assert _freshness_score("not-a-date") == 0.50


# ---------------------------------------------------------------------------
# 5. Registry tests
# ---------------------------------------------------------------------------

class _MockSettings:
    def __init__(self, provider: str):
        self.dashboard_news_provider = provider


def test_registry_returns_fixtures_provider():
    provider = get_dashboard_provider(_MockSettings("fixtures"))
    assert isinstance(provider, DashboardFixturesProvider)


def test_registry_returns_live_provider():
    provider = get_dashboard_provider(_MockSettings("live"))
    assert isinstance(provider, DashboardLiveProvider)


def test_registry_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown DASHBOARD_NEWS_PROVIDER"):
        get_dashboard_provider(_MockSettings("newsapi"))


# ---------------------------------------------------------------------------
# 6. Service injection + fallback tests
# ---------------------------------------------------------------------------

def test_service_accepts_injected_fixtures_provider():
    service = DashboardService(provider=DashboardFixturesProvider())
    result = service.get_top_articles("breaking")
    assert result.category == "breaking"
    assert len(result.articles) == 5


def test_service_falls_back_when_provider_raises_provider_error():
    """Service must return fixture results when live provider raises DashboardProviderError."""

    class _FailingProvider(DashboardNewsProvider):
        def fetch(self, category: str) -> list[dict]:
            raise DashboardProviderError("Simulated network failure")

    service = DashboardService(provider=_FailingProvider())
    result = service.get_top_articles("tech_ai")
    assert result.category == "tech_ai"
    assert len(result.articles) == 5


def test_service_with_mocked_live_provider_returns_live_articles():
    """End-to-end: service uses injected live provider with mocked RSS data."""
    provider = _make_live_provider_with_mock_feed()
    service = DashboardService(provider=provider)
    result = service.get_top_articles("breaking")
    assert result.category == "breaking"
    assert len(result.articles) == 3
    assert all(a.source == "BBC News" for a in result.articles)
    # final_score formula must still hold
    for a in result.articles:
        expected = round(
            0.35 * a.importance_score + 0.30 * a.credibility_score
            + 0.20 * a.relevance_score + 0.10 * a.freshness_score
            + 0.05 * a.source_diversity_score,
            4,
        )
        assert abs(a.final_score - expected) < 1e-3


def test_service_provider_is_abc_subclass():
    assert issubclass(DashboardFixturesProvider, DashboardNewsProvider)
    assert issubclass(DashboardLiveProvider, DashboardNewsProvider)


