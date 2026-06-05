"""News Integrity Feed service.

Builds the home-page daily feed: a list of current stories per category, each
annotated with concise information-integrity signals (cross-source
corroboration, contradiction signals, framing indicators, source diversity, and
a confidence signal).

It reuses the existing dashboard provider + scoring pipeline so there is exactly
one provider path and one scoring formula in the system. Provider failures fall
back to fixtures (handled inside ``DashboardService``); this service never
performs its own network calls.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from app.core.config import get_settings
from app.core import news_scoring
from app.providers.dashboard_base import DashboardNewsProvider, DashboardProviderError
from app.providers.dashboard_fixtures_provider import DashboardFixturesProvider
from app.providers.dashboard_registry import available_dashboard_providers, get_dashboard_provider_by_name
from app.schemas.news_feed import (
    ClusterArticleRef,
    ConfidenceSignal,
    ContradictionSignal,
    CorroborationSignal,
    FramingSignal,
    NewsFeedItem,
    NewsFeedResponse,
    ScoreExplanation,
    ScoringMethodResponse,
    SourceDiversitySignal,
)
from app.services.dashboard_service import SUPPORTED_CATEGORIES
from app.services.story_cluster_service import StoryCluster, StoryClusterService

# How many cards to surface per category in the feed.
_DEFAULT_FEED_LIMIT = 8

logger = logging.getLogger(__name__)


class NewsFeedService:
    def __init__(
        self,
        providers: Optional[list[tuple[str, DashboardNewsProvider]]] = None,
        cluster_service: Optional[StoryClusterService] = None,
    ) -> None:
        self._settings = get_settings()
        self._provider_mode = self._settings.news_feed_provider_stack
        self._providers = providers if providers is not None else self._build_provider_stack()
        self._cluster_service = cluster_service if cluster_service is not None else StoryClusterService()
        self._fallback = DashboardFixturesProvider()
        self._max_per_provider = max(1, int(self._settings.news_feed_max_articles_per_provider))

    def get_feed(self, category: str, limit: int = _DEFAULT_FEED_LIMIT) -> NewsFeedResponse:
        if category not in SUPPORTED_CATEGORIES:
            raise ValueError(
                f"Unsupported category '{category}'. "
                f"Supported: {sorted(SUPPORTED_CATEGORIES)}"
            )

        raw_articles, active_providers = self._fetch_provider_articles(category)
        clusters = self._cluster_service.cluster_articles(category, raw_articles)
        explanations = self.score_explanations(evidence_mode=True)
        items = [
            self._to_feed_item(cluster, explanations)
            for cluster in clusters[:limit]
        ]

        return NewsFeedResponse(
            category=category,
            provider_mode=",".join(active_providers),
            generated_at=datetime.now(timezone.utc).isoformat(),
            items=items,
            score_explanations=explanations,
            disclaimer=news_scoring.SCORING_DISCLAIMER,
        )

    def scoring_method(self) -> ScoringMethodResponse:
        return ScoringMethodResponse(
            formula=news_scoring.SCORE_FORMULA,
            weights=dict(news_scoring.SCORE_WEIGHTS),
            score_explanations=self.score_explanations(evidence_mode=True),
            disclaimer=news_scoring.SCORING_DISCLAIMER,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def score_explanations(evidence_mode: bool = False) -> list[ScoreExplanation]:
        return [ScoreExplanation(**d) for d in news_scoring.score_explanations(evidence_mode=evidence_mode)]

    def _build_provider_stack(self) -> list[tuple[str, DashboardNewsProvider]]:
        configured = [
            name.strip().lower()
            for name in (self._settings.news_feed_provider_stack or "").split(",")
            if name.strip()
        ]
        if not configured:
            configured = ["fixtures"]

        providers: list[tuple[str, DashboardNewsProvider]] = []
        for name in configured:
            try:
                providers.append((name, get_dashboard_provider_by_name(name)))
            except ValueError:
                logger.warning(
                    "Ignoring unknown provider '%s' in NEWS_FEED_PROVIDER_STACK. Supported: %s",
                    name,
                    available_dashboard_providers(),
                )
        if not providers:
            providers.append(("fixtures", DashboardFixturesProvider()))
        return providers

    def _fetch_provider_articles(self, category: str) -> tuple[list[dict], list[str]]:
        combined: list[dict] = []
        active_providers: list[str] = []
        seen: set[tuple[str, str, str]] = set()

        for provider_name, provider in self._providers:
            try:
                rows = provider.fetch(category)
            except (DashboardProviderError, NotImplementedError) as exc:
                logger.warning(
                    "Feed provider '%s' failed for '%s' (%s: %s).",
                    provider_name,
                    category,
                    type(exc).__name__,
                    exc,
                )
                continue

            active_providers.append(provider_name)
            for raw in rows[: self._max_per_provider]:
                article = dict(raw)
                article["provider_name"] = provider_name
                key = (
                    str(article.get("id", "")),
                    str(article.get("headline", "")).strip().lower(),
                    str(article.get("source", "")).strip().lower(),
                )
                if key in seen:
                    continue
                seen.add(key)
                combined.append(article)

        if combined:
            return combined, active_providers

        # Ultimate safety fallback for empty or fully-failed stacks.
        fallback_rows = [dict(a) for a in self._fallback.fetch(category)]
        for row in fallback_rows:
            row["provider_name"] = "fixtures_fallback"
        return fallback_rows, ["fixtures_fallback"]

    @staticmethod
    def _to_feed_item(cluster: StoryCluster, explanations: list[ScoreExplanation]) -> NewsFeedItem:
        representative_source = cluster.publishers[0] if cluster.publishers else "Unknown"
        detail_path = (
            f"/dashboard/{cluster.representative_article_id}"
            if cluster.representative_article_id.startswith(("dash_", "live_", "gdelt_"))
            else "/dashboard"
        )
        return NewsFeedItem(
            id=cluster.cluster_id,
            cluster_id=cluster.cluster_id,
            headline=cluster.representative_headline,
            source=representative_source,
            publishers=cluster.publishers,
            source_count=cluster.source_count,
            independent_source_count=cluster.independent_source_count,
            category=cluster.category,
            published_at=cluster.latest_published_at,
            earliest_published_at=cluster.earliest_published_at,
            latest_published_at=cluster.latest_published_at,
            neutral_summary=cluster.representative_summary,
            commonly_reported_details=cluster.common_reported_details,
            differing_details=cluster.differing_details,
            articles=[ClusterArticleRef(**a) for a in cluster.articles],
            final_score=cluster.final_score,
            importance_score=cluster.importance_score,
            credibility_score=cluster.credibility_score,
            relevance_score=cluster.relevance_score,
            freshness_score=cluster.freshness_score,
            source_diversity_score=cluster.source_diversity_score,
            corroboration=CorroborationSignal(**cluster.corroboration_signal),
            source_diversity=SourceDiversitySignal(**cluster.source_diversity_signal),
            contradiction=ContradictionSignal(**news_scoring.contradiction_signal(
                {"contradiction_warnings": cluster.contradiction_warnings}
            )),
            framing=FramingSignal(**cluster.framing_signal),
            confidence=ConfidenceSignal(**cluster.confidence_signal),
            key_claims=cluster.common_reported_details,
            why_selected=cluster.why_selected,
            detail_path=detail_path,
            score_explanations=explanations,
        )
