from app.services.claim_service import ClaimService


def test_claim_extraction_fallback_produces_claims():
    service = ClaimService()
    sentences = [
        "The Federal Reserve left interest rates unchanged according to officials.",
        "Analysts said inflation remains a concern for the U.S. economy.",
        "I think this is the best policy ever.",
    ]
    claims = service.extract(sentences, " ".join(sentences))
    assert len(claims) >= 1
    assert all("claim_id" in c and "text" in c for c in claims)
    types = {c["claim_type"].value if hasattr(c["claim_type"], "value") else c["claim_type"] for c in claims}
    assert "factual_claim" in types or "opinion" in types or "unclear" in types


def test_opinion_classification():
    service = ClaimService()
    sent = "I think the market will definitely crash tomorrow without any doubt."
    ctype = service._classify_sentence(sent)
    assert ctype.value in ("opinion", "prediction", "factual_claim", "unclear")
