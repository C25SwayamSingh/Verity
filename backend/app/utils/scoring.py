from app.schemas.domain import ClaimType, CorroborationStatus


def corroboration_from_counts(
    support_count: int,
    contradict_count: int,
    claim_type: ClaimType,
    max_relevance: float,
) -> CorroborationStatus:
    if claim_type in {
        ClaimType.opinion,
        ClaimType.advice,
        ClaimType.personal_experience,
        ClaimType.promotional_claim,
    }:
        return CorroborationStatus.not_checkable

    if claim_type == ClaimType.prediction:
        return CorroborationStatus.not_checkable

    if contradict_count > 0 and support_count <= contradict_count:
        return CorroborationStatus.contradicted

    if support_count >= 2 and max_relevance >= 0.45:
        return CorroborationStatus.high_corroboration

    if support_count >= 1 and max_relevance >= 0.35:
        return CorroborationStatus.medium_corroboration

    if support_count >= 1:
        return CorroborationStatus.low_corroboration

    if claim_type == ClaimType.unclear:
        return CorroborationStatus.not_checkable

    return CorroborationStatus.low_corroboration
