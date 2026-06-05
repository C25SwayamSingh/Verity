"""News Integrity Feed + corroboration-engine tests."""

from fastapi.testclient import TestClient

from app.core import news_scoring
from app.core.config import Settings
from app.main import app
from app.providers.dashboard_base import DashboardNewsProvider, DashboardProviderError
from app.services.dashboard_service import SUPPORTED_CATEGORIES
from app.services.news_feed_service import NewsFeedService

client = TestClient(app)


class _FailingProvider(DashboardNewsProvider):
    def fetch(self, category: str) -> list[dict]:
        raise DashboardProviderError("simulated outage")


def test_feed_default_category():
    r = client.get("/v1/news/feed")
    assert r.status_code == 200
    data = r.json()
    assert data["category"] == "breaking"
    assert len(data["items"]) >= 1


def test_feed_all_supported_categories():
    for cat in SUPPORTED_CATEGORIES:
        r = client.get(f"/v1/news/feed?category={cat}")
        assert r.status_code == 200, f"failed for {cat}"
        data = r.json()
        assert data["category"] == cat
        for item in data["items"]:
            assert item["category"] == cat


def test_feed_invalid_category_422():
    assert client.get("/v1/news/feed?category=other").status_code == 422
    assert client.get("/v1/news/feed?category=nope").status_code == 422


def test_feed_item_has_cluster_backed_fields():
    item = client.get("/v1/news/feed?category=markets_stocks").json()["items"][0]
    required_fields = [
        "id",
        "cluster_id",
        "headline",
        "source",
        "publishers",
        "source_count",
        "independent_source_count",
        "category",
        "published_at",
        "earliest_published_at",
        "latest_published_at",
        "neutral_summary",
        "commonly_reported_details",
        "differing_details",
        "articles",
        "final_score",
        "importance_score",
        "credibility_score",
        "relevance_score",
        "freshness_score",
        "source_diversity_score",
        "corroboration",
        "source_diversity",
        "contradiction",
        "framing",
        "confidence",
        "why_selected",
        "score_explanations",
    ]
    for field in required_fields:
        assert field in item, f"missing field {field}"
    assert set(item["corroboration"]) >= {"level", "label", "strength", "detail"}
    assert set(item["source_diversity"]) >= {"level", "label", "score", "detail"}
    assert set(item["contradiction"]) >= {"present", "label", "detail"}
    assert set(item["framing"]) >= {"level", "label"}
    assert set(item["confidence"]) >= {"level", "label", "score"}
    assert item["source_count"] >= item["independent_source_count"] >= 1


def test_feed_signals_use_approved_language():
    item = client.get("/v1/news/feed?category=breaking").json()["items"][0]
    blob = (
        item["corroboration"]["label"]
        + item["source_diversity"]["label"]
        + item["framing"]["label"]
        + item["confidence"]["label"]
    ).lower()
    for banned in ("truth score", "fake news", "guaranteed", "unbiased truth"):
        assert banned not in blob


def test_feed_score_ranges_valid():
    for item in client.get("/v1/news/feed?category=tech_ai").json()["items"]:
        for f in (
            "final_score",
            "importance_score",
            "credibility_score",
            "relevance_score",
            "freshness_score",
            "source_diversity_score",
        ):
            assert 0.0 <= item[f] <= 1.0
        assert 0.0 <= item["confidence"]["score"] <= 1.0
        assert 0.0 <= item["source_diversity"]["score"] <= 1.0


def test_feed_includes_score_explanations_and_disclaimer():
    data = client.get("/v1/news/feed?category=breaking").json()
    assert len(data["score_explanations"]) == len(news_scoring.SCORE_DEFINITIONS)
    assert data["disclaimer"]
    assert "truth score" in data["disclaimer"].lower()


def test_feed_score_explanations_mention_overlap():
    data = client.get("/v1/news/feed?category=breaking").json()
    text = " ".join(item["description"] for item in data["score_explanations"]).lower()
    assert "source-overlap" in text or "overlap" in text


def test_scoring_endpoint_fields_present_and_explained():
    data = client.get("/v1/news/scoring").json()
    assert data["formula"]
    assert data["weights"]["importance_score"] == 0.35
    keys = {e["key"] for e in data["score_explanations"]}
    for required in (
        "importance_score",
        "credibility_score",
        "relevance_score",
        "freshness_score",
        "source_diversity_score",
    ):
        assert required in keys
    for e in data["score_explanations"]:
        assert e["description"], f"{e['key']} has no explanation"


def test_weighted_components_sum_to_one():
    total = sum(news_scoring.SCORE_WEIGHTS.values())
    assert abs(total - 1.0) < 1e-9


def test_feed_fallback_works_if_all_stack_providers_fail():
    service = NewsFeedService(providers=[("broken", _FailingProvider())])
    feed = service.get_feed("breaking")
    assert len(feed.items) >= 1
    assert "fixtures_fallback" in feed.provider_mode


def test_settings_default_with_no_api_keys():
    s = Settings(_env_file=None)
    assert s.newsapi_api_key == ""
    assert s.gnews_api_key == ""
    assert s.google_factcheck_api_key == ""
    assert s.dashboard_news_provider == "fixtures"
    assert s.news_feed_provider_stack


def test_app_health_ok_without_keys():
    assert client.get("/health").json()["status"] == "ok"


def test_corroboration_signal_cluster_single_source():
    signal = news_scoring.corroboration_signal(
        {
            "source_count": 1,
            "independent_source_count": 1,
            "source_overlap_score": 0.0,
            "credibility_score": 0.8,
            "source_diversity_score": 0.2,
        }
    )
    assert signal["level"] == "single_source"


def test_contradiction_signal_detects_warnings():
    present = news_scoring.contradiction_signal(
        {"contradiction_warnings": ["sources disagree on the death toll"]}
    )
    assert present["present"] is True
    absent = news_scoring.contradiction_signal({"contradiction_warnings": []})
    assert absent["present"] is False


def test_confidence_signal_drops_with_contradiction():
    base = {
        "final_score": 0.8,
        "credibility_score": 0.8,
        "source_diversity_score": 0.8,
        "source_overlap_score": 0.4,
        "independent_source_count": 3,
    }
    high = news_scoring.confidence_signal(base)
    flagged = news_scoring.confidence_signal({**base, "contradiction_warnings": ["x"]})
    assert flagged["score"] < high["score"]
