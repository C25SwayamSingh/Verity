from abc import ABC, abstractmethod


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
    """

    @abstractmethod
    def fetch(self, category: str) -> list[dict]:
        """Return all available article dicts for *category*, unscored and unsorted."""
