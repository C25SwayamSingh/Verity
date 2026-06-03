from app.providers.base import SourceProvider
from app.providers.fixtures_provider import FixturesSourceProvider
from app.schemas.domain import SourceRef


class MockSourceProvider(SourceProvider):
    """MVP provider delegating to fixture corpus."""

    def __init__(self) -> None:
        self._fixtures = FixturesSourceProvider()

    def search(self, query: str, category: str, limit: int = 5) -> list[SourceRef]:
        return self._fixtures.search(query, category, limit)
