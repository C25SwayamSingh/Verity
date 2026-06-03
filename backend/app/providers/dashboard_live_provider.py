from app.providers.dashboard_base import DashboardNewsProvider


class DashboardLiveProvider(DashboardNewsProvider):
    """
    Placeholder for a future live news source provider.

    When DASHBOARD_NEWS_PROVIDER=live is set, this provider is selected.
    It raises NotImplementedError until a real API integration is built.
    DashboardService catches this and falls back to DashboardFixturesProvider.

    To implement:
      1. Add API credentials to config.py (e.g. NEWS_API_KEY).
      2. Implement fetch() to call the external API, normalise the response
         to the standard article dict shape, and return the results.
      3. Remove or update this docstring.
    """

    def fetch(self, category: str) -> list[dict]:
        raise NotImplementedError(
            "DashboardLiveProvider is not yet implemented. "
            "Set DASHBOARD_NEWS_PROVIDER=fixtures to use fixture data, "
            "or implement fetch() to connect a real news source."
        )
