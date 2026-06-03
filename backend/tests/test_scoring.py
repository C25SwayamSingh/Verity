from app.schemas.domain import ClaimType, CorroborationStatus
from app.utils.scoring import corroboration_from_counts


def test_high_corroboration():
    status = corroboration_from_counts(2, 0, ClaimType.factual_claim, 0.5)
    assert status == CorroborationStatus.high_corroboration


def test_contradicted():
    status = corroboration_from_counts(0, 2, ClaimType.factual_claim, 0.4)
    assert status == CorroborationStatus.contradicted


def test_not_checkable_opinion():
    status = corroboration_from_counts(3, 0, ClaimType.opinion, 0.9)
    assert status == CorroborationStatus.not_checkable


def test_low_corroboration():
    status = corroboration_from_counts(0, 0, ClaimType.factual_claim, 0.1)
    assert status == CorroborationStatus.low_corroboration
