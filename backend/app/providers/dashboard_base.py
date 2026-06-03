from abc import ABC, abstractmethod
from typing import Optional


class DashboardProviderError(Exception):
    """Raised by a DashboardNewsProvider when fetching or parsing fails at runtime."""


class DashboardNewsProvider(ABC):
    """
    Abstract base for all dashboard news providers.

    Each provider is responsible for returning raw article dicts for a given
    category. Scoring, sorting, and pagination are handled by DashboardService.

    A dict returned by ``fetch`` must contain at least:
        id, headline, source, category, published_at, neutral_summary,
        importance_score, credibility_score, relevance_score, freshness_score,
        source_diversity_score, framing_label, key_claims, support_summary,
        contradiction_warnings, why_selected

    On any retrieval or parse failure, raise ``DashboardProviderError``.
    DashboardService will catch it and fall back to DashboardFixturesProvider.
    """

    @abstractmethod
    def fetch(self, category: str) -> list[dict]:
        """Return all available article dicts for *category*, unscored and unsorted."""

    def fetch_by_id(self, article_id: str) -> Optional[dict]:
        """
        Return the article dict for *article_id*, or None if not found.

        The default implementation raises NotImplementedError. Providers that
        support efficient ID lookup (e.g. DashboardFixturesProvider) should
        override this method. Providers that cannot look up by ID (e.g. live RSS)
        leave this as-is; DashboardService falls back to the fixtures provider.
        """
        raise NotImplementedError(
            f"{type(self).__name__} does not support fetch_by_id. "
            "DashboardService will fall back to fixtures for article ID lookups."
        )
