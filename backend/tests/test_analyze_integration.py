from fastapi.testclient import TestClient

from app.core.rate_limit import get_rate_limiter
from app.db.session import init_db
from app.main import app

client = TestClient(app)


SAMPLE_NEWS = """
The Federal Reserve left interest rates unchanged on Wednesday, according to officials,
as policymakers cited persistent inflation pressures. The Labor Department reported the
unemployment rate edged lower while employers added jobs in healthcare and technology sectors.
Stock indexes rose after several large companies reported earnings that exceeded expectations.
"""


def setup_function():
    init_db()
    get_rate_limiter().reset()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_analyze_news_content():
    r = client.post(
        "/v1/analyze",
        json={
            "text": SAMPLE_NEWS,
            "content_type": "article",
            "user_selected_category": "domestic_us",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "analysis_id" in data
    assert data["summary"]
    assert isinstance(data["key_takeaways"], list)
    assert data["eligibility"]["bias_framing_eligible"] is True
    assert len(data["claims"]) >= 1


def test_analyze_cooking_ineligible():
    r = client.post(
        "/v1/analyze",
        json={
            "text": "Today we make pasta. Ingredients: 2 cups flour, 1 egg. Preheat oven to 350 and mix tablespoon of salt into the recipe for best results at home cooking tutorial.",
            "content_type": "article",
            "user_selected_category": "domestic_us",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["eligibility"]["bias_framing_eligible"] is False
    assert data["eligibility"]["detected_category"] == "other"


def test_get_analysis_by_id():
    create = client.post(
        "/v1/analyze",
        json={
            "text": SAMPLE_NEWS,
            "content_type": "article",
            "user_selected_category": "markets_stocks",
        },
    )
    aid = create.json()["analysis_id"]
    r = client.get(f"/v1/analysis/{aid}")
    assert r.status_code == 200
    assert r.json()["analysis_id"] == aid
