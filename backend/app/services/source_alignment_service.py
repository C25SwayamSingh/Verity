import json
from pathlib import Path

from app.providers.mock_provider import MockSourceProvider
from app.schemas.domain import ClaimResult, ClaimType, CorroborationStatus, SourceRef
from app.utils.scoring import corroboration_from_counts
from app.utils.similarity import combined_similarity

_FIXTURE_PATH = Path(__file__).resolve().parents[1] / "providers" / "fixtures" / "sample_sources.json"


class SourceAlignmentService:
    def __init__(self) -> None:
        self._provider = MockSourceProvider()
        with _FIXTURE_PATH.open(encoding="utf-8") as f:
            self._fixture_meta = {s["source_id"]: s for s in json.load(f)}

    def align_claims(
        self,
        raw_claims: list[dict],
        category: str,
        eligible: bool,
    ) -> list[ClaimResult]:
        results: list[ClaimResult] = []
        for claim in raw_claims:
            if not eligible:
                results.append(
                    ClaimResult(
                        claim_id=claim["claim_id"],
                        text=claim["text"],
                        claim_type=claim["claim_type"],
                        corroboration_status=CorroborationStatus.not_checkable,
                        explanation="Cross-source corroboration is not available for this content category.",
                    )
                )
                continue

            sources = self._provider.search(claim["text"], category, limit=6)
            supporting: list[SourceRef] = []
            contradicting: list[SourceRef] = []
            max_rel = 0.0

            for src in sources:
                meta = self._fixture_meta.get(src.source_id, {})
                max_rel = max(max_rel, src.relevance_score)
                if meta.get("stance") == "contradictory" and src.relevance_score >= 0.2:
                    contradicting.append(src)
                elif src.relevance_score >= 0.25:
                    supporting.append(src)
                elif src.relevance_score >= 0.15:
                    supporting.append(src)

            status = corroboration_from_counts(
                len(supporting),
                len(contradicting),
                claim["claim_type"],
                max_rel,
            )
            explanation = self._build_explanation(status, supporting, contradicting)

            results.append(
                ClaimResult(
                    claim_id=claim["claim_id"],
                    text=claim["text"],
                    claim_type=claim["claim_type"],
                    corroboration_status=status,
                    supporting_sources=supporting[:3],
                    contradicting_sources=contradicting[:2],
                    explanation=explanation,
                )
            )
        return results

    def _build_explanation(
        self,
        status: CorroborationStatus,
        supporting: list[SourceRef],
        contradicting: list[SourceRef],
    ) -> str:
        if status == CorroborationStatus.not_checkable:
            return "This statement type is not suited for factual cross-source corroboration."
        if status == CorroborationStatus.contradicted:
            return "Available fixture sources include signals that contradict this claim's framing or details."
        if status == CorroborationStatus.high_corroboration:
            return f"Multiple fixture sources show alignment ({len(supporting)} supporting references)."
        if status == CorroborationStatus.medium_corroboration:
            return "Some fixture sources show partial alignment; corroboration is moderate."
        if status == CorroborationStatus.low_corroboration:
            return "Limited alignment with available fixture sources; treat as low corroboration."
        return "Corroboration could not be established from available sources."
