"""Phase 3.6 — persisted creator post analyses and demo workflow."""
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.db.models import CreatorPostAnalysisRecord
from app.db.session import engine
from app.main import _creators, app
from app.services.creator_analysis_store import compute_content_hash
from app.services.creator_metrics_service import post_content
from app.services.creator_service import CreatorService
from app.services.ingest_service import IngestService

client = TestClient(app)

KNOWN_CREATOR_ID = "creator-001"
UNKNOWN_CREATOR_ID = "creator-does-not-exist-xyz"

DEMO_POST_BODY = {
    "title": "Demo transcript on Federal Reserve policy",
    "content": (
        "The Federal Reserve left interest rates unchanged on Wednesday, according to officials, "
        "as policymakers cited persistent inflation pressures. Stock indexes rose after several "
        "large companies reported earnings that exceeded expectations in the United States economy."
    ),
    "topic": "monetary policy",
    "platform": "manual transcript",
    "content_type": "transcript",
}


def test_persisted_analysis_reused_without_recompute():
    with Session(engine) as session:
        with patch.object(
            _creators._ingest,
            "run_analysis",
            wraps=_creators._ingest.run_analysis,
        ) as mock_run:
            client.get(f"/v1/creators/{KNOWN_CREATOR_ID}")
            first_calls = mock_run.call_count
            assert first_calls > 0

            records = session.exec(select(CreatorPostAnalysisRecord)).all()
            assert len(records) >= 1

            client.get(f"/v1/creators/{KNOWN_CREATOR_ID}")
            assert mock_run.call_count == first_calls


def test_content_hash_change_triggers_recompute():
    service = CreatorService()
    posts = [p for p in service._fixture_posts if p["creator_id"] == KNOWN_CREATOR_ID]
    post = posts[0]
    original_hash = compute_content_hash(post_content(post))

    with Session(engine) as session:
        service._get_or_analyze_post(session, post, "tech_ai")
        record = session.get(CreatorPostAnalysisRecord, post["post_id"])
        assert record is not None
        assert record.content_hash == original_hash

        mutated = {**post, "content": post_content(post) + " Additional context on artificial intelligence policy."}
        new_hash = compute_content_hash(post_content(mutated))
        assert new_hash != original_hash

        with patch.object(
            IngestService,
            "run_analysis",
            wraps=service._ingest.run_analysis,
        ) as mock_run:
            service._get_or_analyze_post(session, mutated, "tech_ai")
            assert mock_run.call_count == 1

        record = session.get(CreatorPostAnalysisRecord, post["post_id"])
        assert record.content_hash == new_hash


def test_add_demo_post_endpoint():
    r = client.post(
        f"/v1/creators/{KNOWN_CREATOR_ID}/posts/demo",
        json=DEMO_POST_BODY,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["analysis_persisted"] is True
    assert data["post"]["creator_id"] == KNOWN_CREATOR_ID
    assert len(data["post"]["claims"]) >= 0

    posts_r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}/posts")
    assert posts_r.status_code == 200
    post_ids = [p["post_id"] for p in posts_r.json()["posts"]]
    assert data["post"]["post_id"] in post_ids


def test_demo_post_input_basis_defaults_and_note():
    r = client.post(
        f"/v1/creators/{KNOWN_CREATOR_ID}/posts/demo",
        json={**DEMO_POST_BODY, "post_id": "demo-input-basis-test"},
    )
    assert r.status_code == 201
    post = r.json()["post"]
    assert post["input_basis"] == "third_party_extracted_key_points"
    assert post["input_basis_label"] == "Third-party extracted key points"
    assert post["input_basis_note"]
    assert "verbatim transcript" in post["input_basis_note"].lower()


def test_demo_post_full_transcript_no_non_verbatim_note():
    body = {
        **DEMO_POST_BODY,
        "post_id": "demo-full-transcript-test",
        "input_basis": "full_transcript",
    }
    r = client.post(f"/v1/creators/{KNOWN_CREATOR_ID}/posts/demo", json=body)
    assert r.status_code == 201
    post = r.json()["post"]
    assert post["input_basis"] == "full_transcript"
    assert not post.get("input_basis_note")


def test_add_demo_post_unknown_creator_404():
    r = client.post(
        f"/v1/creators/{UNKNOWN_CREATOR_ID}/posts/demo",
        json=DEMO_POST_BODY,
    )
    assert r.status_code == 404


def test_demo_post_update_recomputes_when_content_changes():
    body = {**DEMO_POST_BODY, "post_id": "demo-test-update"}
    r1 = client.post(f"/v1/creators/{KNOWN_CREATOR_ID}/posts/demo", json=body)
    assert r1.status_code == 201
    pid = r1.json()["post"]["post_id"]

    with Session(engine) as session:
        record = session.get(CreatorPostAnalysisRecord, pid)
        old_hash = record.content_hash

    body2 = {
        **body,
        "content": body["content"] + " Congress debated additional fiscal measures the same week.",
    }
    r2 = client.post(f"/v1/creators/{KNOWN_CREATOR_ID}/posts/demo", json=body2)
    assert r2.status_code == 201

    with Session(engine) as session:
        record = session.get(CreatorPostAnalysisRecord, pid)
        assert record.content_hash != old_hash


def test_invalid_creator_id_still_404():
    assert client.get(f"/v1/creators/{UNKNOWN_CREATOR_ID}").status_code == 404
