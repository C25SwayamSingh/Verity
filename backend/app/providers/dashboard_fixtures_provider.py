import json
from pathlib import Path
from typing import Optional

from app.providers.dashboard_base import DashboardNewsProvider

_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "dashboard_articles.json"


class DashboardFixturesProvider(DashboardNewsProvider):
    """Loads articles from the local fixture JSON. Default provider for Phase 2 scaffold."""

    def __init__(self) -> None:
        with _FIXTURE_PATH.open(encoding="utf-8") as f:
            self._articles: list[dict] = json.load(f)

    def fetch(self, category: str) -> list[dict]:
        return [a for a in self._articles if a["category"] == category]

    def fetch_by_id(self, article_id: str) -> Optional[dict]:
        for a in self._articles:
            if a["id"] == article_id:
                return a
        return None
