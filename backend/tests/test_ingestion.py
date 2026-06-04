"""Core ingestion correction — URL-only inputs are not treated as content."""

from fastapi.testclient import TestClient

from app.core.ingestion import classify_ingestion, is_social_video_url
from app.core.rate_limit import get_rate_limiter
from app.db.session import init_db
from app.main import app

client = TestClient(app)

INSTAGRAM_URL = "https://www.instagram.com/reel/DXAOA0Wkj4I/?igsh=aWh6ZHc2MW1mbTA0"
TIKTOK_URL = "https://www.tiktok.com/@user/video/7300000000000000000"
YOUTUBE_URL = "https://youtu.be/dQw4w9WgXcQ"

NEWS_TEXT = (
    "The Federal Reserve left interest rates unchanged on Wednesday, according to officials, "
    "as policymakers cited persistent inflation pressures. The Labor Department reported the "
    "unemployment rate edged lower while employers added jobs in healthcare and technology."
)

COOKING_TEXT = (
    "Today we make pasta in this cooking tutorial. Ingredients: 2 cups flour and 1 egg. "
    "Preheat oven to 350 degrees and mix a tablespoon of salt into the recipe. "
    "Bring a large pot of salted water to a boil, add the pasta, and cook until tender."
)


def setup_function():
    init_db()
    get_rate_limiter().reset()


# --- unit: classifier -------------------------------------------------------

def test_social_video_url_detection():
    assert is_social_video_url(INSTAGRAM_URL)
    assert is_social_video_url(TIKTOK_URL)
    assert is_social_video_url(YOUTUBE_URL)
    assert not is_social_video_url("https://apnews.com/article/economy-123")


def test_classify_link_only_social_needs_more_input():
    c = classify_ingestion(INSTAGRAM_URL)
    assert c.needs_more_input is True
    assert c.analyzable is False
    assert c.ingestion_type == "social_video_url"
    assert INSTAGRAM_URL.rstrip("/") in c.source_links[0] or c.source_links


def test_classify_text_with_link_is_analyzable():
    c = classify_ingestion(NEWS_TEXT + "\n" + INSTAGRAM_URL)
    assert c.needs_more_input is False
    assert c.analyzable is True
    assert c.source_links  # link retained as metadata


# --- API: URL-only Instagram/TikTok submissions -----------------------------

def test_url_only_instagram_does_not_fabricate_content():
    r = client.post(
        "/v1/analyze",
        json={"text": INSTAGRAM_URL, "content_type": "article", "user_selected_category": "domestic_us"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ingestion"]["needs_more_input"] is True
    assert data["ingestion"]["ingestion_type"] == "social_video_url"
    # The URL must NOT appear as summary / takeaways / claims / rewrite.
    assert INSTAGRAM_URL not in data["summary"]
    assert data["key_takeaways"] == []
    assert data["claims"] == []
    assert data["neutral_rewrite"] == ""
    assert data["ingestion"]["guidance"]


def test_url_only_tiktok_returns_transcript_required_state():
    r = client.post(
        "/v1/analyze",
        json={"text": TIKTOK_URL, "content_type": "article", "user_selected_category": "domestic_us"},
    )
    data = r.json()
    assert data["ingestion"]["needs_more_input"] is True
    guidance = data["ingestion"]["guidance"].lower()
    assert "transcript" in guidance or "upload" in guidance


def test_url_only_persisted_state_loadable():
    aid = client.post(
        "/v1/analyze",
        json={"text": YOUTUBE_URL, "content_type": "article", "user_selected_category": "tech_ai"},
    ).json()["analysis_id"]
    got = client.get(f"/v1/analysis/{aid}").json()
    assert got["ingestion"]["needs_more_input"] is True


# --- API: real text still runs through the checker ---------------------------

def test_submitted_transcript_runs_through_pipeline():
    r = client.post(
        "/v1/analyze",
        json={"text": NEWS_TEXT, "content_type": "transcript", "user_selected_category": "domestic_us"},
    )
    data = r.json()
    assert data["summary"]
    assert data["eligibility"]["bias_framing_eligible"] is True
    assert len(data["claims"]) >= 1


def test_caption_text_with_link_runs_through_pipeline():
    r = client.post(
        "/v1/analyze",
        json={
            "text": NEWS_TEXT + "\nSource: " + INSTAGRAM_URL,
            "content_type": "article",
            "user_selected_category": "domestic_us",
        },
    )
    data = r.json()
    assert data["ingestion"]["needs_more_input"] is False
    assert data["summary"]
    assert data["ingestion"]["source_links"]


# --- API: non-news eligibility + neutral rewrite -----------------------------

def test_non_news_gets_no_full_bias_framing():
    r = client.post(
        "/v1/analyze",
        json={"text": COOKING_TEXT, "content_type": "article", "user_selected_category": "domestic_us"},
    )
    data = r.json()
    assert data["eligibility"]["bias_framing_eligible"] is False
    assert data["framing"]["indicators"] == []


def test_non_news_still_gets_summary_and_rewrite():
    r = client.post(
        "/v1/analyze",
        json={"text": COOKING_TEXT, "content_type": "article", "user_selected_category": "domestic_us"},
    )
    data = r.json()
    assert data["summary"]
    # Neutral / clearer rewrite is available even when not news-eligible.
    assert data["neutral_rewrite"]
    assert "not generated" not in data["neutral_rewrite"].lower()
