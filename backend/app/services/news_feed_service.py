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

from datetime import datetime, timezone
from typing import Optional

from app.core.config import get_settings
from app.core import news_scoring
from app.schemas.news_feed import (
    ConfidenceSignal,
    ContradictionSignal,
    CorroborationSignal,
    FramingSignal,
    NewsFeedItem,
    NewsFeedResponse,
    ScoreExplanation,
    ScoringMethodResponse,
)
from app.services.dashboard_service import SUPPORTED_CATEGORIES, DashboardService

# How many cards to surface per category in the feed.
_DEFAULT_FEED_LIMIT = 8


class NewsFeedService:
    def __init__(self, dashboard: Optional[DashboardService] = None) -> None:
        self._dashboard = dashboard if dashboard is not None else DashboardService()
        self._provider_mode = get_settings().dashboard_news_provider

    def get_feed(self, category: str, limit: int = _DEFAULT_FEED_LIMIT) -> NewsFeedResponse:
        if category not in SUPPORTED_CATEGORIES:
            raise ValueError(
                f"Unsupported category '{category}'. "
                f"Supported: {sorted(SUPPORTED_CATEGORIES)}"
            )

        # DashboardService already scores, sorts, and falls back to fixtures on
        # any provider failure.
        scored = self._dashboard.get_top_articles(category, limit=limit)
        items = [self._to_feed_item(article.model_dump()) for article in scored.articles]

        return NewsFeedResponse(
            category=category,
            provider_mode=self._provider_mode,
            generated_at=datetime.now(timezone.utc).isoformat(),
            items=items,
            score_explanations=self.score_explanations(),
            disclaimer=news_scoring.SCORING_DISCLAIMER,
        )

    def scoring_method(self) -> ScoringMethodResponse:
        return ScoringMethodResponse(
            formula=news_scoring.SCORE_FORMULA,
            weights=dict(news_scoring.SCORE_WEIGHTS),
            score_explanations=self.score_explanations(),
            disclaimer=news_scoring.SCORING_DISCLAIMER,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def score_explanations() -> list[ScoreExplanation]:
        return [ScoreExplanation(**d) for d in news_scoring.score_explanations()]

    @staticmethod
    def _to_feed_item(article: dict) -> NewsFeedItem:
        corr = news_scoring.corroboration_signal(article)
        contra = news_scoring.contradiction_signal(article)
        fram = news_scoring.framing_signal(article)
        conf = news_scoring.confidence_signal(article)

        return NewsFeedItem(
            id=article["id"],
            headline=article["headline"],
            source=article["source"],
            category=article["category"],
            published_at=article["published_at"],
            neutral_summary=article["neutral_summary"],
            final_score=article["final_score"],
            importance_score=article["importance_score"],
            credibility_score=article["credibility_score"],
            relevance_score=article["relevance_score"],
            freshness_score=article["freshness_score"],
            source_diversity_score=article["source_diversity_score"],
            corroboration=CorroborationSignal(**corr),
            contradiction=ContradictionSignal(**contra),
            framing=FramingSignal(**fram),
            confidence=ConfidenceSignal(**conf),
            key_claims=article.get("key_claims", []),
            why_selected=news_scoring.why_selected(article),
            detail_path=f"/dashboard/{article['id']}",
        )
