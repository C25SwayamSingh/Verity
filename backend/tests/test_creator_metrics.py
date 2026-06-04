"""
Phase 3.5 — creator metrics derived from IngestService analysis pipeline.
"""
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.domain import ClaimResult, ClaimType, CorroborationStatus
from app.services.creator_metrics_service import (
    METRICS_SOURCE_DERIVED,
    claim_support_rate,
    contradiction_rate,
    low_corroboration_rate,
    post_content,
    post_source_alignment,
)
from app.services.creator_service import CreatorService
from app.services.ingest_service import IngestService

client = TestClient(app)

KNOWN_CREATOR_ID = "creator-001"
UNKNOWN_CREATOR_ID = "creator-does-not-exist-xyz"


def _sample_claims() -> list[ClaimResult]:
    return [
        ClaimResult(
            claim_id="1",
            text="A",
            claim_type=ClaimType.factual_claim,
            corroboration_status=CorroborationStatus.high_corroboration,
            explanation="ok",
        ),
        ClaimResult(
            claim_id="2",
            text="B",
            claim_type=ClaimType.factual_claim,
            corroboration_status=CorroborationStatus.medium_corroboration,
            explanation="ok",
        ),
        ClaimResult(
            claim_id="3",
            text="C",
            claim_type=ClaimType.factual_claim,
            corroboration_status=CorroborationStatus.low_corroboration,
            explanation="low",
        ),
        ClaimResult(
            claim_id="4",
            text="D",
            claim_type=ClaimType.factual_claim,
            corroboration_status=CorroborationStatus.contradicted,
            explanation="contra",
        ),
    ]


def test_post_content_builds_from_fixture_fields():
    post = {
        "title": "Test Title",
        "summary": "A short summary.",
        "claims": [{"text": "Claim one about artificial intelligence policy."}],
    }
    text = post_content(post)
    assert "Test Title" in text
    assert len(text) >= 50


def test_claim_support_rate_from_claims():
    claims = _sample_claims()
    # 2 supported (high + medium) out of 4 checkable
    assert claim_support_rate(claims) == 0.5


def test_contradiction_rate_from_claims():
    claims = _sample_claims()
    assert contradiction_rate(claims) == 0.25


def test_low_corroboration_rate_from_claims():
    claims = _sample_claims()
    assert low_corroboration_rate(claims) == 0.25


def test_post_source_alignment_from_claims():
    claims = _sample_claims()
    # (1.0 + 0.75 + 0.35 + 0.15) / 4 = 0.5625
    assert post_source_alignment(claims) == 0.5625


def test_creator_overview_metrics_source_derived():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}")
    assert r.status_code == 200
    data = r.json()
    assert data["metrics_source"] == METRICS_SOURCE_DERIVED


def test_creator_list_metrics_source_derived():
    r = client.get("/v1/creators")
    assert r.status_code == 200
    for creator in r.json()["creators"]:
        assert creator["metrics_source"] == METRICS_SOURCE_DERIVED


def test_creator_metrics_match_aggregated_posts():
    """Overview rates must match pooling claims from derived post payloads."""
    overview = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}").json()
    posts = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}/posts").json()["posts"]

    all_statuses = []
    for post in posts:
        assert post["metrics_source"] == METRICS_SOURCE_DERIVED
        for claim in post["claims"]:
            if claim["corroboration_status"] != "not_checkable":
                all_statuses.append(claim["corroboration_status"])

    if all_statuses:
        expected_support = sum(
            1 for s in all_statuses if s in ("high_corroboration", "medium_corroboration")
        ) / len(all_statuses)
        expected_contra = sum(1 for s in all_statuses if s == "contradicted") / len(all_statuses)
        expected_low = sum(1 for s in all_statuses if s == "low_corroboration") / len(all_statuses)
        assert abs(overview["claim_support_rate"] - round(expected_support, 4)) < 1e-3
        assert abs(overview["contradiction_rate"] - round(expected_contra, 4)) < 1e-3
        assert abs(overview["low_corroboration_rate"] - round(expected_low, 4)) < 1e-3


def test_creator_metrics_derived_from_analyzed_post_content():
    service = CreatorService()
    posts = [p for p in service._fixture_posts if p["creator_id"] == KNOWN_CREATOR_ID]
    assert posts
    analysis = service._metrics.analyze_post(posts[0], "tech_ai")
    assert analysis.claims
    assert analysis.summary


def test_run_analysis_does_not_require_db_session():
    ingest = IngestService()
    result = ingest.run_analysis(
        text=(
            "The Federal Reserve left interest rates unchanged on Wednesday, according to officials, "
            "as policymakers cited persistent inflation pressures in the United States economy and stock markets."
        ),
        content_type="article",
        user_selected_category="domestic_us",
    )
    assert result.analysis_id
    assert isinstance(result.claims, list)


def test_invalid_creator_id_still_404():
    assert client.get(f"/v1/creators/{UNKNOWN_CREATOR_ID}").status_code == 404
    assert client.get(f"/v1/creators/{UNKNOWN_CREATOR_ID}/posts").status_code == 404


def test_transparency_summary_mentions_derived():
    r = client.get(f"/v1/creators/{KNOWN_CREATOR_ID}")
    summary = r.json()["transparency_summary"].lower()
    assert "derived" in summary or "analyzed" in summary
    assert "not a verdict" in summary
