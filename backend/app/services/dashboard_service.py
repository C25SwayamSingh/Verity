import logging
from typing import Optional

from app.core.config import get_settings
from app.providers.dashboard_base import DashboardNewsProvider, DashboardProviderError
from app.providers.dashboard_fixtures_provider import DashboardFixturesProvider
from app.providers.dashboard_registry import get_dashboard_provider
from app.schemas.dashboard import DashboardArticle, DashboardResponse
from app.schemas.domain import UserCategory

logger = logging.getLogger(__name__)

SUPPORTED_CATEGORIES = {c.value for c in UserCategory if c != UserCategory.other}

_SCORE_WEIGHTS = {
    "importance_score": 0.35,
    "credibility_score": 0.30,
    "relevance_score": 0.20,
    "freshness_score": 0.10,
    "source_diversity_score": 0.05,
}


def _compute_final_score(article: dict) -> float:
    return round(
        sum(article[k] * w for k, w in _SCORE_WEIGHTS.items()),
        4,
    )


class DashboardService:
    def __init__(self, provider: Optional[DashboardNewsProvider] = None) -> None:
        self._provider = provider if provider is not None else get_dashboard_provider(get_settings())
        self._fallback = DashboardFixturesProvider()

    def get_top_articles(self, category: str, limit: int = 5) -> DashboardResponse:
        if category not in SUPPORTED_CATEGORIES:
            raise ValueError(
                f"Unsupported category '{category}'. "
                f"Supported: {sorted(SUPPORTED_CATEGORIES)}"
            )

        try:
            candidates = self._provider.fetch(category)
        except (NotImplementedError, DashboardProviderError) as exc:
            logger.warning(
                "Dashboard provider failed (%s: %s); falling back to fixtures.",
                type(exc).__name__,
                exc,
            )
            candidates = self._fallback.fetch(category)

        scored = sorted(candidates, key=_compute_final_score, reverse=True)
        articles = [
            DashboardArticle(
                **{k: v for k, v in a.items()},
                final_score=_compute_final_score(a),
            )
            for a in scored[:limit]
        ]
        return DashboardResponse(category=category, articles=articles)
