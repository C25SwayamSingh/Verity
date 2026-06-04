"""News Integrity Feed + scoring tests.

Covers:
  - /v1/news/feed endpoint and normalized item schema
  - integrity signals present (corroboration, contradiction, framing, confidence)
  - /v1/news/scoring fields present + explained
  - provider fallback into the feed
  - missing API keys do not crash settings/app
"""
from fastapi.testclient import TestClient

from app.core import news_scoring
from app.core.config import Settings
from app.main import app
from app.providers.dashboard_base import DashboardNewsProvider, DashboardProviderError
from app.services.dashboard_service import SUPPORTED_CATEGORIES, DashboardService
from app.services.news_feed_service import NewsFeedService

client = TestClient(app)

ITEM_FIELDS = [
    "id", "headline", "source", "category", "published_at", "neutral_summary",
    "final_score", "importance_score", "credibility_score", "relevance_score",
    "freshness_score", "source_diversity_score",
    "corroboration", "contradiction", "framing", "confidence",
    "key_claims", "why_selected", "detail_path",
]


# ---------------------------------------------------------------------------
# Endpoint: /v1/news/feed
# ---------------------------------------------------------------------------

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


def test_feed_item_has_normalized_schema():
    item = client.get("/v1/news/feed?category=markets_stocks").json()["items"][0]
    for field in ITEM_FIELDS:
        assert field in item, f"missing field {field}"
    # nested signal shapes
    assert set(item["corroboration"]) >= {"level", "label", "strength", "detail"}
    assert set(item["contradiction"]) >= {"present", "label", "detail"}
    assert set(item["framing"]) >= {"level", "label"}
    assert set(item["confidence"]) >= {"level", "label", "score"}


def test_feed_signals_use_approved_language():
    item = client.get("/v1/news/feed?category=breaking").json()["items"][0]
    corr = item["corroboration"]["label"].lower()
    assert "corroboration" in corr or "single-source" in corr
    # never claims absolute truth
    blob = (item["corroboration"]["label"] + item["framing"]["label"]
            + item["confidence"]["label"]).lower()
    for banned in ("truth score", "fake news", "guaranteed", "unbiased truth"):
        assert banned not in blob


def test_feed_score_ranges_valid():
    for item in client.get("/v1/news/feed?category=tech_ai").json()["items"]:
        for f in ("final_score", "importance_score", "credibility_score",
                  "relevance_score", "freshness_score", "source_diversity_score"):
            assert 0.0 <= item[f] <= 1.0
        assert 0.0 <= item["confidence"]["score"] <= 1.0


def test_feed_detail_path_points_to_dashboard():
    item = client.get("/v1/news/feed?category=breaking").json()["items"][0]
    assert item["detail_path"] == f"/dashboard/{item['id']}"


def test_feed_includes_score_explanations_and_disclaimer():
    data = client.get("/v1/news/feed?category=breaking").json()
    assert len(data["score_explanations"]) == len(news_scoring.SCORE_DEFINITIONS)
    assert data["disclaimer"]
    assert "truth score" in data["disclaimer"].lower()  # explicitly disclaims it


# ---------------------------------------------------------------------------
# Endpoint: /v1/news/scoring — fields present + explained
# ---------------------------------------------------------------------------

def test_scoring_endpoint_fields_present_and_explained():
    data = client.get("/v1/news/scoring").json()
    assert data["formula"]
    assert data["weights"]["importance_score"] == 0.35
    keys = {e["key"] for e in data["score_explanations"]}
    for required in ("importance_score", "credibility_score", "relevance_score",
                     "freshness_score", "source_diversity_score"):
        assert required in keys
    for e in data["score_explanations"]:
        assert e["description"], f"{e['key']} has no explanation"
        assert "label" in e and "weight" in e and "weighted" in e


def test_weighted_components_sum_to_one():
    total = sum(news_scoring.SCORE_WEIGHTS.values())
    assert abs(total - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# Provider fallback into the feed
# ---------------------------------------------------------------------------

def test_feed_falls_back_to_fixtures_when_provider_fails():
    class _Failing(DashboardNewsProvider):
        def fetch(self, category: str) -> list[dict]:
            raise DashboardProviderError("simulated outage")

    service = NewsFeedService(DashboardService(provider=_Failing()))
    feed = service.get_feed("breaking")
    assert len(feed.items) >= 1  # fixtures fallback supplied items


# ---------------------------------------------------------------------------
# Missing API keys do not crash settings/app
# ---------------------------------------------------------------------------

def test_settings_default_with_no_api_keys():
    s = Settings(_env_file=None)
    assert s.newsapi_api_key == ""
    assert s.gnews_api_key == ""
    assert s.google_factcheck_api_key == ""
    assert s.dashboard_news_provider == "fixtures"


def test_app_health_ok_without_keys():
    assert client.get("/health").json()["status"] == "ok"


# ---------------------------------------------------------------------------
# Scoring helpers — derived signals
# ---------------------------------------------------------------------------

def test_corroboration_signal_levels():
    strong = news_scoring.corroboration_signal(
        {"credibility_score": 0.95, "source_diversity_score": 0.9}
    )
    assert strong["level"] == "strong"
    weak = news_scoring.corroboration_signal(
        {"credibility_score": 0.3, "source_diversity_score": 0.2}
    )
    assert weak["level"] == "single_source"


def test_contradiction_signal_detects_warnings():
    present = news_scoring.contradiction_signal(
        {"contradiction_warnings": ["sources disagree on the death toll"]}
    )
    assert present["present"] is True
    absent = news_scoring.contradiction_signal({"contradiction_warnings": []})
    assert absent["present"] is False


def test_confidence_signal_drops_with_contradiction():
    base = {"final_score": 0.8, "credibility_score": 0.8, "source_diversity_score": 0.8}
    high = news_scoring.confidence_signal(base)
    flagged = news_scoring.confidence_signal({**base, "contradiction_warnings": ["x"]})
    assert flagged["score"] < high["score"]
