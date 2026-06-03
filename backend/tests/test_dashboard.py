from fastapi.testclient import TestClient

from app.main import app
from app.services.dashboard_service import SUPPORTED_CATEGORIES, _compute_final_score

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
