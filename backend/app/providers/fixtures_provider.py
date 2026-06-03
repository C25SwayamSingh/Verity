import json
from pathlib import Path

from app.providers.base import SourceProvider
from app.schemas.domain import SourceRef
from app.utils.similarity import combined_similarity

_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_sources.json"


class FixturesSourceProvider(SourceProvider):
    def __init__(self) -> None:
        with _FIXTURE_PATH.open(encoding="utf-8") as f:
            self._sources = json.load(f)

    def search(self, query: str, category: str, limit: int = 5) -> list[SourceRef]:
        scored: list[tuple[float, dict]] = []
        query_lower = query.lower()
        for src in self._sources:
            cats = src.get("categories", [])
            if category not in cats and category != "other":
                cat_boost = 0.0
            else:
                cat_boost = 0.1
            kw_text = " ".join(src.get("keywords", []))
            sim = combined_similarity(query, src.get("snippet", "") + " " + kw_text)
            if any(k in query_lower for k in src.get("keywords", [])):
                sim += 0.15
            scored.append((sim + cat_boost, src))

        scored.sort(key=lambda x: x[0], reverse=True)
        results: list[SourceRef] = []
        for score, src in scored[:limit]:
            if score < 0.12:
                continue
            results.append(
                SourceRef(
                    source_id=src["source_id"],
                    title=src["title"],
                    publisher=src["publisher"],
                    url=src["url"],
                    snippet=src["snippet"],
                    relevance_score=round(min(1.0, score), 2),
                )
            )
        return results
