"""GDELT provider tests — no network calls (the _fetch_raw seam is patched)."""
import json

import pytest

from app.providers.dashboard_base import DashboardNewsProvider, DashboardProviderError
from app.providers.dashboard_gdelt_provider import DashboardGdeltProvider, _parse_seendate
from app.providers.dashboard_registry import get_dashboard_provider
from app.services.dashboard_service import DashboardService

_MOCK_JSON = json.dumps(
    {
        "articles": [
            {
                "url": "https://www.reuters.com/world/story-1",
                "title": "Central bank holds rates amid inflation concerns",
                "domain": "reuters.com",
                "sourcecommonname": "Reuters",
                "seendate": "20260603T140000Z",
            },
            {
                "url": "https://example-news.com/story-2",
                "title": "Lawmakers debate annual budget",
                "domain": "example-news.com",
                "seendate": "20260603T120000Z",
            },
            {
                # No title — must be skipped.
                "url": "https://example-news.com/story-3",
                "title": "",
                "domain": "example-news.com",
                "seendate": "20260603T100000Z",
            },
        ]
    }
)


def _provider_with_mock(mock_json: str = _MOCK_JSON) -> DashboardGdeltProvider:
    p = DashboardGdeltProvider()
    p._fetch_raw = lambda query: mock_json  # type: ignore[method-assign]
    return p


def test_gdelt_is_provider_subclass():
    assert issubclass(DashboardGdeltProvider, DashboardNewsProvider)


def test_gdelt_registry_lookup():
    class _S:
        dashboard_news_provider = "gdelt"

    assert isinstance(get_dashboard_provider(_S()), DashboardGdeltProvider)


def test_gdelt_fetch_normalizes_and_skips_titleless():
    articles = _provider_with_mock().fetch("breaking")
    assert len(articles) == 2  # titleless skipped
    required = [
        "id", "headline", "source", "category", "published_at", "neutral_summary",
        "importance_score", "credibility_score", "relevance_score", "freshness_score",
        "source_diversity_score", "framing_label", "key_claims", "support_summary",
        "contradiction_warnings", "why_selected",
    ]
    for a in articles:
        for f in required:
            assert f in a, f"missing {f}"
        assert a["category"] == "breaking"
        assert a["id"].startswith("gdelt_")


def test_gdelt_domain_credibility_applied():
    a = _provider_with_mock().fetch("breaking")[0]
    assert a["source"] == "Reuters"
    assert a["credibility_score"] >= 0.9  # known reputable domain prior


def test_gdelt_unknown_domain_uses_default_credibility():
    a = _provider_with_mock().fetch("breaking")[1]
    assert a["credibility_score"] == 0.70


def test_gdelt_raises_on_bad_json():
    p = _provider_with_mock("not-json{")
    with pytest.raises(DashboardProviderError):
        p.fetch("breaking")


def test_gdelt_raises_for_unconfigured_category():
    with pytest.raises(DashboardProviderError, match="No GDELT query"):
        _provider_with_mock().fetch("other")


def test_gdelt_fetch_error_raises_provider_error():
    p = DashboardGdeltProvider()

    def _boom(query):
        raise DashboardProviderError("network down")

    p._fetch_raw = _boom  # type: ignore[method-assign]
    with pytest.raises(DashboardProviderError):
        p.fetch("breaking")


def test_service_falls_back_to_fixtures_with_failing_gdelt():
    p = DashboardGdeltProvider()
    p._fetch_raw = lambda q: (_ for _ in ()).throw(DashboardProviderError("down"))  # type: ignore
    service = DashboardService(provider=p)
    result = service.get_top_articles("breaking")
    assert len(result.articles) == 5  # fixtures fallback


def test_parse_seendate_valid_and_invalid():
    assert _parse_seendate("20260603T140000Z").startswith("2026-06-03T14:00:00")
    # invalid → current time iso (just assert it parses to a string with 'T')
    assert "T" in _parse_seendate("garbage")
