from abc import ABC, abstractmethod

from app.schemas.domain import SourceRef


class SourceProvider(ABC):
    @abstractmethod
    def search(self, query: str, category: str, limit: int = 5) -> list[SourceRef]:
        pass
