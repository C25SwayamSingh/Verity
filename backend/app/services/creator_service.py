import json
import logging
import uuid
from pathlib import Path
from typing import Optional

from sqlmodel import Session

from app.schemas.creator import (
    CreateDemoCreatorPostRequest,
    CreateDemoCreatorPostResponse,
    CreatorListItem,
    CreatorListResponse,
    CreatorOverview,
    CreatorPost,
    CreatorPostsResponse,
)
from app.schemas.domain import AnalyzeResponse
from app.services.creator_analysis_store import (
    compute_content_hash,
    get_persisted_analysis,
    save_persisted_analysis,
)
from app.services.creator_metrics_service import CreatorMetricsService, post_content
from app.services.creator_post_store import create_demo_post, list_demo_posts
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
        self._fixture_posts: list[dict] = _load_creator_posts()
        self._ingest = ingest if ingest is not None else IngestService()
        self._metrics = metrics if metrics is not None else CreatorMetricsService(self._ingest)

    def _creator_exists(self, creator_id: str) -> bool:
        return any(c["creator_id"] == creator_id for c in self._creators)

    def _get_creator_fixture(self, creator_id: str) -> Optional[dict]:
        return next((c for c in self._creators if c["creator_id"] == creator_id), None)

    def _posts_for_creator(self, session: Session, creator_id: str) -> list[dict]:
        fixture = [p for p in self._fixture_posts if p["creator_id"] == creator_id]
        demo = list_demo_posts(session, creator_id)
        by_id = {p["post_id"]: p for p in fixture}
        for post in demo:
            by_id[post["post_id"]] = post
        return list(by_id.values())

    def _get_or_analyze_post(
        self,
        session: Session,
        post: dict,
        category: str,
    ) -> AnalyzeResponse:
        text = post_content(post)
        content_hash = compute_content_hash(text)
        content_type = post.get("content_type") or "article"

        cached = get_persisted_analysis(session, post["post_id"], content_hash)
        if cached is not None:
            return cached

        analysis = self._metrics.analyze_post(post, category, content_type=content_type)
        save_persisted_analysis(
            session,
            post_id=post["post_id"],
            creator_id=post["creator_id"],
            content_hash=content_hash,
            category=category,
            content_type=content_type,
            analysis=analysis,
        )
        return analysis

    def _derive_for_creator(self, session: Session, creator_id: str) -> Optional[dict]:
        creator = self._get_creator_fixture(creator_id)
        if creator is None:
            return None

        posts = self._posts_for_creator(session, creator_id)
        category = creator["category"]
        analyses = [self._get_or_analyze_post(session, p, category) for p in posts]
        aggregated = self._metrics.aggregate_metrics(posts, analyses)
        built_posts = [
            self._metrics.build_creator_post(p, a) for p, a in zip(posts, analyses)
        ]

        return {
            "creator": creator,
            "metrics": aggregated,
            "posts": built_posts,
        }

    def list_creators(self, session: Session) -> CreatorListResponse:
        items: list[CreatorListItem] = []
        for c in self._creators:
            derived = self._derive_for_creator(session, c["creator_id"])
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

    def get_creator(self, session: Session, creator_id: str) -> Optional[CreatorOverview]:
        derived = self._derive_for_creator(session, creator_id)
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

    def get_creator_posts(
        self, session: Session, creator_id: str
    ) -> Optional[CreatorPostsResponse]:
        derived = self._derive_for_creator(session, creator_id)
        if derived is None:
            return None
        return CreatorPostsResponse(creator_id=creator_id, posts=derived["posts"])

    def add_demo_post(
        self,
        session: Session,
        creator_id: str,
        request: CreateDemoCreatorPostRequest,
    ) -> Optional[CreateDemoCreatorPostResponse]:
        if not self._creator_exists(creator_id):
            return None

        creator = self._get_creator_fixture(creator_id)
        assert creator is not None

        post_id = request.post_id or f"demo-{uuid.uuid4().hex[:12]}"

        post_dict = create_demo_post(
            session,
            creator_id,
            title=request.title,
            content=request.content,
            topic=request.topic,
            platform=request.platform,
            published_at=request.published_at,
            source_url=request.source_url,
            content_type=request.content_type,
            post_id=post_id,
        )

        analysis = self._get_or_analyze_post(session, post_dict, creator["category"])
        built = self._metrics.build_creator_post(post_dict, analysis)

        return CreateDemoCreatorPostResponse(
            post=built,
            message="Demo post saved and analyzed. Dashboard metrics will include this content.",
            analysis_persisted=True,
        )
