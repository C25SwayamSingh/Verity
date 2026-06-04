"""Aggregate creator integrity metrics from IngestService analysis outputs."""

from collections import Counter
from typing import Optional

from app.schemas.creator import CreatorPost, PostClaim, WeakClaim
from app.schemas.domain import AnalyzeResponse, ClaimResult, CorroborationStatus, FramingOverallLabel
from app.services.ingest_service import IngestService

METRICS_SOURCE_DERIVED = "derived_from_analysis"

_FRAMING_SCORES: dict[str, float] = {
    FramingOverallLabel.mostly_neutral.value: 0.85,
    FramingOverallLabel.mixed_framing.value: 0.55,
    FramingOverallLabel.notable_framing.value: 0.25,
}

_CLAIM_ALIGNMENT_SCORES: dict[str, float] = {
    CorroborationStatus.high_corroboration.value: 1.0,
    CorroborationStatus.medium_corroboration.value: 0.75,
    CorroborationStatus.low_corroboration.value: 0.35,
    CorroborationStatus.contradicted.value: 0.15,
    CorroborationStatus.not_checkable.value: 0.5,
}

_SUPPORTED_STATUSES = {
    CorroborationStatus.high_corroboration,
    CorroborationStatus.medium_corroboration,
}

_WEAK_STATUSES = {
    CorroborationStatus.low_corroboration,
    CorroborationStatus.contradicted,
}


def post_content(post: dict) -> str:
    """Return analyzable text for a fixture post."""
    if post.get("content"):
        return str(post["content"])
    parts = [post.get("title", ""), post.get("summary", "")]
    for claim in post.get("claims", []):
        parts.append(claim.get("text", ""))
    return "\n\n".join(p.strip() for p in parts if p and str(p).strip())


def _checkable_claims(claims: list[ClaimResult]) -> list[ClaimResult]:
    return [c for c in claims if c.corroboration_status != CorroborationStatus.not_checkable]


def claim_alignment_score(claim: ClaimResult) -> float:
    return _CLAIM_ALIGNMENT_SCORES.get(claim.corroboration_status.value, 0.5)


def post_source_alignment(claims: list[ClaimResult]) -> float:
    pool = _checkable_claims(claims) or claims
    if not pool:
        return 0.0
    return round(sum(claim_alignment_score(c) for c in pool) / len(pool), 4)


def claim_support_rate(claims: list[ClaimResult]) -> float:
    checkable = _checkable_claims(claims)
    if not checkable:
        return 0.0
    supported = sum(1 for c in checkable if c.corroboration_status in _SUPPORTED_STATUSES)
    return round(supported / len(checkable), 4)


def contradiction_rate(claims: list[ClaimResult]) -> float:
    checkable = _checkable_claims(claims)
    if not checkable:
        return 0.0
    contradicted = sum(
        1 for c in checkable if c.corroboration_status == CorroborationStatus.contradicted
    )
    return round(contradicted / len(checkable), 4)


def low_corroboration_rate(claims: list[ClaimResult]) -> float:
    checkable = _checkable_claims(claims)
    if not checkable:
        return 0.0
    low = sum(
        1 for c in checkable if c.corroboration_status == CorroborationStatus.low_corroboration
    )
    return round(low / len(checkable), 4)


def framing_score(label: str) -> float:
    return _FRAMING_SCORES.get(label, 0.5)


def collect_publishers(analyses: list[AnalyzeResponse]) -> list[str]:
    publishers: list[str] = []
    for analysis in analyses:
        for claim in analysis.claims:
            for src in claim.supporting_sources:
                if src.publisher:
                    publishers.append(src.publisher)
    return publishers


def source_diversity_score(analyses: list[AnalyzeResponse]) -> float:
    publishers = collect_publishers(analyses)
    if not publishers:
        return 0.0
    unique = len(set(publishers))
    return round(min(1.0, unique / 8.0), 4)


class CreatorMetricsService:
    def __init__(self, ingest: Optional[IngestService] = None) -> None:
        self._ingest = ingest if ingest is not None else IngestService()

    def analyze_post(
        self,
        post: dict,
        category: str,
        content_type: str = "article",
    ) -> AnalyzeResponse:
        return self._ingest.run_analysis(
            text=post_content(post),
            content_type=content_type,
            user_selected_category=category,
        )

    def build_creator_post(self, post: dict, analysis: AnalyzeResponse) -> CreatorPost:
        claims = analysis.claims
        checkable = _checkable_claims(claims)
        supported = sum(1 for c in checkable if c.corroboration_status in _SUPPORTED_STATUSES)
        contradicted = sum(
            1 for c in checkable if c.corroboration_status == CorroborationStatus.contradicted
        )
        low = sum(
            1 for c in checkable if c.corroboration_status == CorroborationStatus.low_corroboration
        )
        sources_used = list(
            dict.fromkeys(
                src.publisher
                for c in claims
                for src in c.supporting_sources
                if src.publisher
            )
        )
        if not sources_used and post.get("sources_used"):
            sources_used = list(post["sources_used"])

        return CreatorPost(
            post_id=post["post_id"],
            creator_id=post["creator_id"],
            title=post["title"],
            platform=post["platform"],
            published_at=post["published_at"],
            source_url=post["source_url"],
            topic=post["topic"],
            summary=analysis.summary or post.get("summary", ""),
            claims=[
                PostClaim(
                    claim_id=c.claim_id,
                    text=c.text,
                    claim_type=c.claim_type.value,
                    corroboration_status=c.corroboration_status.value,
                )
                for c in claims
            ],
            supported_claims_count=supported,
            contradicted_claims_count=contradicted,
            low_corroboration_claims_count=low,
            source_alignment_score=post_source_alignment(claims),
            framing_label=analysis.framing.overall_label.value,
            sources_used=sources_used,
            audience_signal_placeholder=post.get(
                "audience_signal_placeholder",
                "Engagement rate and comment sentiment data not yet collected.",
            ),
            metrics_source=METRICS_SOURCE_DERIVED,
        )

    def aggregate_metrics(
        self,
        posts: list[dict],
        analyses: list[AnalyzeResponse],
    ) -> dict:
        all_claims: list[ClaimResult] = []
        for analysis in analyses:
            all_claims.extend(analysis.claims)

        post_alignments = [
            (posts[i]["post_id"], post_source_alignment(analyses[i].claims))
            for i in range(len(posts))
        ]
        post_alignments.sort(key=lambda x: x[1], reverse=True)

        topic_counts = Counter(p.get("topic", "") for p in posts if p.get("topic"))
        publisher_counts = Counter(collect_publishers(analyses))

        weak: list[WeakClaim] = []
        for post, analysis in zip(posts, analyses):
            for claim in analysis.claims:
                if claim.corroboration_status not in _WEAK_STATUSES:
                    continue
                weak.append(
                    WeakClaim(
                        claim_id=claim.claim_id,
                        post_id=post["post_id"],
                        text=claim.text,
                        corroboration_status=claim.corroboration_status.value,
                        note=claim.explanation or "Limited cross-source corroboration for this claim.",
                    )
                )
        weak.sort(key=lambda w: _CLAIM_ALIGNMENT_SCORES.get(w.corroboration_status, 0.5))
        weak = weak[:5]

        support = claim_support_rate(all_claims)
        contra = contradiction_rate(all_claims)
        low = low_corroboration_rate(all_claims)
        align = post_source_alignment(all_claims)
        diversity = source_diversity_score(analyses)
        framing_avg = (
            round(
                sum(framing_score(a.framing.overall_label.value) for a in analyses) / len(analyses),
                4,
            )
            if analyses
            else 0.0
        )

        n = len(posts)
        support_pct = int(round(support * 100))
        transparency_summary = (
            f"Integrity signals are derived from {n} analyzed post{'s' if n != 1 else ''} "
            f"using the core information-integrity engine. "
            f"{support_pct}% of checkable claims show medium or high corroboration; "
            f"{int(round(contra * 100))}% show contradiction signals; "
            f"{int(round(low * 100))}% show low corroboration. "
            "This summary describes source alignment and claim patterns only — not a verdict on the creator."
        )

        return {
            "total_analyzed_posts": n,
            "source_alignment_score": align,
            "claim_support_rate": support,
            "contradiction_rate": contra,
            "low_corroboration_rate": low,
            "source_diversity_score": diversity,
            "average_framing_score": framing_avg,
            "top_topics": [t for t, _ in topic_counts.most_common(5)],
            "most_used_sources": [s for s, _ in publisher_counts.most_common(5)],
            "most_reliable_posts": [pid for pid, _ in post_alignments[:3]],
            "weakest_claims": weak,
            "transparency_summary": transparency_summary,
            "metrics_source": METRICS_SOURCE_DERIVED,
        }
