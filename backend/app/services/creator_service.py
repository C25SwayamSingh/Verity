import json
import logging
from pathlib import Path
from typing import Optional

from app.schemas.creator import (
    CreatorListItem,
    CreatorListResponse,
    CreatorOverview,
    CreatorPost,
    CreatorPostsResponse,
)
from app.services.creator_metrics_service import CreatorMetricsService
from app.services.ingest_service import IngestService

logger = logging.getLogger(__name__)

_FIXTURES_DIR = Path(__file__).parent.parent / "providers" / "fixtures"


def _load_creators() -> list[dict]:
    path = _FIXTURES_DIR / "creators.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_creator_posts() -> list[dict]:
    path = _FIXTURES_DIR / "creator_posts.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class CreatorService:
    def __init__(
        self,
        ingest: Optional[IngestService] = None,
        metrics: Optional[CreatorMetricsService] = None,
    ) -> None:
        self._creators: list[dict] = _load_creators()
        self._posts: list[dict] = _load_creator_posts()
        self._ingest = ingest if ingest is not None else IngestService()
        self._metrics = metrics if metrics is not None else CreatorMetricsService(self._ingest)
        self._derived_cache: dict[str, dict] = {}

    def _derive_for_creator(self, creator_id: str) -> Optional[dict]:
        if creator_id in self._derived_cache:
            return self._derived_cache[creator_id]

        creator = next((c for c in self._creators if c["creator_id"] == creator_id), None)
        if creator is None:
            return None

        posts = [p for p in self._posts if p["creator_id"] == creator_id]
        category = creator["category"]
        analyses = [self._metrics.analyze_post(p, category) for p in posts]
        aggregated = self._metrics.aggregate_metrics(posts, analyses)
        built_posts = [
            self._metrics.build_creator_post(p, a) for p, a in zip(posts, analyses)
        ]

        result = {
            "creator": creator,
            "metrics": aggregated,
            "posts": built_posts,
        }
        self._derived_cache[creator_id] = result
        return result

    def list_creators(self) -> CreatorListResponse:
        items: list[CreatorListItem] = []
        for c in self._creators:
            derived = self._derive_for_creator(c["creator_id"])
            if derived is None:
                continue
            m = derived["metrics"]
            items.append(
                CreatorListItem(
                    creator_id=c["creator_id"],
                    name=c["name"],
                    platform=c["platform"],
                    handle=c["handle"],
                    category=c["category"],
                    bio=c["bio"],
                    metrics_source=m["metrics_source"],
                    total_analyzed_posts=m["total_analyzed_posts"],
                    source_alignment_score=m["source_alignment_score"],
                    claim_support_rate=m["claim_support_rate"],
                    contradiction_rate=m["contradiction_rate"],
                    top_topics=m["top_topics"],
                )
            )
        return CreatorListResponse(creators=items)

    def get_creator(self, creator_id: str) -> Optional[CreatorOverview]:
        derived = self._derive_for_creator(creator_id)
        if derived is None:
            return None
        c = derived["creator"]
        m = derived["metrics"]
        return CreatorOverview(
            creator_id=c["creator_id"],
            name=c["name"],
            platform=c["platform"],
            handle=c["handle"],
            category=c["category"],
            bio=c["bio"],
            metrics_source=m["metrics_source"],
            total_analyzed_posts=m["total_analyzed_posts"],
            source_alignment_score=m["source_alignment_score"],
            claim_support_rate=m["claim_support_rate"],
            contradiction_rate=m["contradiction_rate"],
            low_corroboration_rate=m["low_corroboration_rate"],
            source_diversity_score=m["source_diversity_score"],
            average_framing_score=m["average_framing_score"],
            top_topics=m["top_topics"],
            most_used_sources=m["most_used_sources"],
            most_reliable_posts=m["most_reliable_posts"],
            weakest_claims=m["weakest_claims"],
            transparency_summary=m["transparency_summary"],
        )

    def get_creator_posts(self, creator_id: str) -> Optional[CreatorPostsResponse]:
        derived = self._derive_for_creator(creator_id)
        if derived is None:
            return None
        return CreatorPostsResponse(creator_id=creator_id, posts=derived["posts"])
