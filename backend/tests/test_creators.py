"""
Creator Integrity Dashboard tests — Phase 3 scaffold.

Covers:
  1. GET /v1/creators — list endpoint
  2. GET /v1/creators/{creator_id} — detail endpoint
  3. GET /v1/creators/{creator_id}/posts — posts endpoint
  4. 404 handling for unknown creator_id
  5. Metric field presence and valid ranges
  6. Service-level unit tests
"""
import pytest
from fastapi.testclient import TestClient

from sqlmodel import Session

from app.db.session import engine
from app.main import app
from app.services.creator_service import CreatorService

client = TestClient(app)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

METRIC_SCORE_FIELDS = [
    "source_alignment_score",
    "claim_support_rate",
    "contradiction_rate",
    "low_corroboration_rate",
    "source_diversity_score",
    "average_framing_score",
]

KNOWN_CREATOR_ID = "creator-001"
UNKNOWN_CREATOR_ID = "creator-does-not-exist-xyz"


def _first_creator_id() -> str:
    r = client.get("/v1/creators")
    assert r.status_code == 200
    creators = r.json()["creators"]
    assert len(creators) > 0
    return creators[0]["creator_id"]


# ---------------------------------------------------------------------------
# 1. List endpoint
# ---------------------------------------------------------------------------

def test_creators_list_returns_200():
    r = client.get("/v1/creators")
    assert r.status_code == 200


def test_creators_list_has_creators_key():
    r = client.get("/v1/creators")
    data = r.json()
    assert "creators" in data
    assert isinstance(data["creators"], list)


def test_creators_list_returns_at_least_one():
    r = client.get("/v1/creators")
    assert len(r.json()["creators"]) >= 1


def test_creators_list_item_has_required_fields():
    r = client.get("/v1/creators")
    item = r.json()["creators"][0]
    required = [
        "creator_id", "name", "platform", "handle", "category", "bio",
        "total_analyzed_posts", "source_alignment_score", "claim_support_rate",
        "contradiction_rate", "top_topics",
    ]
    for field in required:
        assert field in item, f"Missing field in list item: {field}"


def test_creators_list_scores_in_range():
    r = client.get("/v1/creators")
    for creator in r.json()["creators"]:
        for field in ["source_alignment_score", "claim_support_rate", "contradiction_rate"]:
            val = creator[field]
            assert 0.0 <= val <= 1.0, f"Score out of range: {field}={val}"


def test_creators_list_top_topics_is_list():
    r = client.get("/v1/creators")
    for creator in r.json()["creators"]:
        assert isinstance(creator["top_topics"], list)
        assert len(creator["top_topics"]) >= 1


def test_creators_list_total_analyzed_posts_is_non_negative():
    r = client.get("/v1/creators")
    for creator in r.json()["creators"]:
        assert creator["total_analyzed_posts"] >= 0


# ---------------------------------------------------------------------------
# 2. Creator detail endpoint
# ---------------------------------------------------------------------------

def test_creator_detail_returns_200():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}")
    assert r.status_code == 200


def test_creator_detail_has_all_required_fields():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}")
    data = r.json()
    required = [
        "creator_id", "name", "platform", "handle", "category", "bio",
        "total_analyzed_posts", "source_alignment_score", "claim_support_rate",
        "contradiction_rate", "low_corroboration_rate", "source_diversity_score",
        "average_framing_score", "top_topics", "most_used_sources",
        "most_reliable_posts", "weakest_claims", "transparency_summary",
    ]
    for field in required:
        assert field in data, f"Missing field in detail: {field}"


def test_creator_detail_all_metric_scores_in_range():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}")
    data = r.json()
    for field in METRIC_SCORE_FIELDS:
        val = data[field]
        assert 0.0 <= val <= 1.0, f"Score out of range: {field}={val}"


def test_creator_detail_weakest_claims_structure():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}")
    for claim in r.json()["weakest_claims"]:
        for key in ["claim_id", "post_id", "text", "corroboration_status", "note"]:
            assert key in claim, f"Missing key '{key}' in weakest_claim"


def test_creator_detail_transparency_summary_is_string():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}")
    summary = r.json()["transparency_summary"]
    assert isinstance(summary, str)
    assert len(summary) > 0


def test_creator_detail_top_topics_non_empty():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}")
    topics = r.json()["top_topics"]
    assert isinstance(topics, list)
    assert len(topics) >= 1


def test_creator_detail_most_used_sources_non_empty():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}")
    sources = r.json()["most_used_sources"]
    assert isinstance(sources, list)
    assert len(sources) >= 1


def test_all_fixture_creators_have_valid_detail():
    r = client.get("/v1/creators")
    for item in r.json()["creators"]:
        detail_r = client.get(f"/v1/creators/{item['creator_id']}")
        assert detail_r.status_code == 200, f"Detail failed for {item['creator_id']}"
        data = detail_r.json()
        assert data["creator_id"] == item["creator_id"]
        for field in METRIC_SCORE_FIELDS:
            assert 0.0 <= data[field] <= 1.0


# ---------------------------------------------------------------------------
# 3. Creator posts endpoint
# ---------------------------------------------------------------------------

def test_creator_posts_returns_200():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}/posts")
    assert r.status_code == 200


def test_creator_posts_has_required_keys():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}/posts")
    data = r.json()
    assert "creator_id" in data
    assert "posts" in data
    assert data["creator_id"] == KNOWN_CREATOR_ID


def test_creator_posts_returns_at_least_one_post():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}/posts")
    posts = r.json()["posts"]
    assert len(posts) >= 1


def test_creator_posts_each_post_has_required_fields():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}/posts")
    required = [
        "post_id", "creator_id", "title", "platform", "published_at",
        "source_url", "topic", "summary", "claims",
        "supported_claims_count", "contradicted_claims_count",
        "low_corroboration_claims_count", "source_alignment_score",
        "framing_label", "sources_used", "audience_signal_placeholder",
    ]
    for post in r.json()["posts"]:
        for field in required:
            assert field in post, f"Missing field '{field}' in post"


def test_creator_posts_source_alignment_score_in_range():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}/posts")
    for post in r.json()["posts"]:
        val = post["source_alignment_score"]
        assert 0.0 <= val <= 1.0, f"source_alignment_score out of range: {val}"


def test_creator_posts_claim_counts_non_negative():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}/posts")
    for post in r.json()["posts"]:
        assert post["supported_claims_count"] >= 0
        assert post["contradicted_claims_count"] >= 0
        assert post["low_corroboration_claims_count"] >= 0


def test_creator_posts_claims_have_required_fields():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}/posts")
    for post in r.json()["posts"]:
        for claim in post["claims"]:
            for key in ["claim_id", "text", "claim_type", "corroboration_status"]:
                assert key in claim, f"Missing key '{key}' in claim"


def test_creator_posts_creator_id_matches():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}/posts")
    for post in r.json()["posts"]:
        assert post["creator_id"] == KNOWN_CREATOR_ID


def test_all_fixture_creators_posts_accessible():
    r = client.get("/v1/creators")
    for item in r.json()["creators"]:
        posts_r = client.get(f"/v1/creators/{item['creator_id']}/posts")
        assert posts_r.status_code == 200, f"Posts endpoint failed for {item['creator_id']}"
        posts = posts_r.json()["posts"]
        assert len(posts) >= 1, f"No posts returned for {item['creator_id']}"


# ---------------------------------------------------------------------------
# 4. 404 handling
# ---------------------------------------------------------------------------

def test_creator_detail_unknown_id_returns_404():
    r = client.get(f"/v1/creators/{UNKNOWN_CREATOR_ID}")
    assert r.status_code == 404


def test_creator_posts_unknown_id_returns_404():
    r = client.get(f"/v1/creators/{UNKNOWN_CREATOR_ID}/posts")
    assert r.status_code == 404


def test_creator_detail_404_has_detail_message():
    r = client.get(f"/v1/creators/{UNKNOWN_CREATOR_ID}")
    body = r.json()
    assert "detail" in body


def test_creator_posts_404_has_detail_message():
    r = client.get(f"/v1/creators/{UNKNOWN_CREATOR_ID}/posts")
    body = r.json()
    assert "detail" in body


# ---------------------------------------------------------------------------
# 5. Service-level unit tests
# ---------------------------------------------------------------------------

def test_service_list_creators_returns_all():
    service = CreatorService()
    with Session(engine) as session:
        result = service.list_creators(session)
    assert len(result.creators) >= 1


def test_service_get_creator_returns_overview():
    service = CreatorService()
    with Session(engine) as session:
        result = service.get_creator(session, KNOWN_CREATOR_ID)
    assert result is not None
    assert result.creator_id == KNOWN_CREATOR_ID


def test_service_get_creator_unknown_returns_none():
    service = CreatorService()
    with Session(engine) as session:
        result = service.get_creator(session, UNKNOWN_CREATOR_ID)
    assert result is None


def test_service_get_creator_posts_returns_posts():
    service = CreatorService()
    with Session(engine) as session:
        result = service.get_creator_posts(session, KNOWN_CREATOR_ID)
    assert result is not None
    assert result.creator_id == KNOWN_CREATOR_ID
    assert len(result.posts) >= 1


def test_service_get_creator_posts_unknown_returns_none():
    service = CreatorService()
    with Session(engine) as session:
        result = service.get_creator_posts(session, UNKNOWN_CREATOR_ID)
    assert result is None


def test_service_creator_overview_score_fields_valid():
    service = CreatorService()
    with Session(engine) as session:
        result = service.get_creator(session, KNOWN_CREATOR_ID)
    assert result is not None
    for field in METRIC_SCORE_FIELDS:
        val = getattr(result, field)
        assert 0.0 <= val <= 1.0, f"{field} out of range: {val}"


def test_service_all_posts_belong_to_correct_creator():
    service = CreatorService()
    with Session(engine) as session:
        result = service.list_creators(session)
        for item in result.creators:
            posts_result = service.get_creator_posts(session, item.creator_id)
            assert posts_result is not None
            for post in posts_result.posts:
                assert post.creator_id == item.creator_id
