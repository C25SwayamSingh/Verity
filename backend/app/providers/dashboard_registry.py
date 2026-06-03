from app.providers.dashboard_base import DashboardNewsProvider
from app.providers.dashboard_fixtures_provider import DashboardFixturesProvider
from app.providers.dashboard_live_provider import DashboardLiveProvider

_REGISTRY: dict[str, type[DashboardNewsProvider]] = {
    "fixtures": DashboardFixturesProvider,
    "live": DashboardLiveProvider,
}


def get_dashboard_provider(settings) -> DashboardNewsProvider:
    """
    Return the DashboardNewsProvider configured by ``settings.dashboard_news_provider``.

    Supported values (DASHBOARD_NEWS_PROVIDER env var):
        fixtures  — DashboardFixturesProvider (default, Phase 2 scaffold)
        live      — DashboardLiveProvider (placeholder; falls back to fixtures at runtime)

    Raises ValueError for unknown provider names so misconfiguration is caught at startup.
    """
    name = settings.dashboard_news_provider.strip().lower()
    provider_cls = _REGISTRY.get(name)
    if provider_cls is None:
        raise ValueError(
            f"Unknown DASHBOARD_NEWS_PROVIDER='{name}'. "
            f"Supported values: {sorted(_REGISTRY)}"
        )
    return provider_cls()
