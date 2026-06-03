import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.providers.dashboard_base import DashboardNewsProvider
from app.providers.dashboard_fixtures_provider import DashboardFixturesProvider
from app.providers.dashboard_live_provider import DashboardLiveProvider
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
# Provider architecture tests
# ---------------------------------------------------------------------------

class _MockSettings:
    """Minimal settings stand-in for registry tests."""
    def __init__(self, provider: str):
        self.dashboard_news_provider = provider


def test_fixtures_provider_returns_articles_for_each_category():
    provider = DashboardFixturesProvider()
    for cat in SUPPORTED_CATEGORIES:
        articles = provider.fetch(cat)
        assert len(articles) >= 1, f"No fixture articles for category '{cat}'"
        assert all(a["category"] == cat for a in articles)


def test_fixtures_provider_returns_empty_for_unknown_category():
    provider = DashboardFixturesProvider()
    assert provider.fetch("nonexistent") == []


def test_live_provider_raises_not_implemented():
    provider = DashboardLiveProvider()
    with pytest.raises(NotImplementedError):
        provider.fetch("breaking")


def test_registry_returns_fixtures_provider():
    provider = get_dashboard_provider(_MockSettings("fixtures"))
    assert isinstance(provider, DashboardFixturesProvider)


def test_registry_returns_live_provider():
    provider = get_dashboard_provider(_MockSettings("live"))
    assert isinstance(provider, DashboardLiveProvider)


def test_registry_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown DASHBOARD_NEWS_PROVIDER"):
        get_dashboard_provider(_MockSettings("newsapi"))


def test_service_accepts_injected_provider():
    service = DashboardService(provider=DashboardFixturesProvider())
    result = service.get_top_articles("breaking")
    assert result.category == "breaking"
    assert len(result.articles) == 5


def test_service_falls_back_to_fixtures_when_live_provider_raises():
    """DashboardService must degrade gracefully when live provider is not implemented."""
    service = DashboardService(provider=DashboardLiveProvider())
    result = service.get_top_articles("tech_ai")
    assert result.category == "tech_ai"
    assert len(result.articles) == 5


def test_service_provider_is_abc_subclass():
    assert issubclass(DashboardFixturesProvider, DashboardNewsProvider)
    assert issubclass(DashboardLiveProvider, DashboardNewsProvider)
