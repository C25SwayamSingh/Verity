import json
from pathlib import Path

from app.schemas.dashboard import DashboardArticle, DashboardResponse
from app.schemas.domain import UserCategory

_FIXTURE_PATH = Path(__file__).parent.parent / "providers" / "fixtures" / "dashboard_articles.json"

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
    def __init__(self) -> None:
        with _FIXTURE_PATH.open(encoding="utf-8") as f:
            raw: list[dict] = json.load(f)
        self._articles: list[dict] = raw

    def get_top_articles(self, category: str, limit: int = 5) -> DashboardResponse:
        if category not in SUPPORTED_CATEGORIES:
            raise ValueError(
                f"Unsupported category '{category}'. "
                f"Supported: {sorted(SUPPORTED_CATEGORIES)}"
            )

        candidates = [a for a in self._articles if a["category"] == category]
        scored = sorted(
            candidates,
            key=lambda a: _compute_final_score(a),
            reverse=True,
        )

        articles = [
            DashboardArticle(
                **{k: v for k, v in a.items()},
                final_score=_compute_final_score(a),
            )
            for a in scored[:limit]
        ]

        return DashboardResponse(category=category, articles=articles)
