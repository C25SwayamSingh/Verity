from app.providers.dashboard_base import DashboardNewsProvider
from app.providers.dashboard_fixtures_provider import DashboardFixturesProvider
from app.providers.dashboard_gdelt_provider import DashboardGdeltProvider
from app.providers.dashboard_live_provider import DashboardLiveProvider

_REGISTRY: dict[str, type[DashboardNewsProvider]] = {
    "fixtures": DashboardFixturesProvider,
    "live": DashboardLiveProvider,
    "gdelt": DashboardGdeltProvider,
}


def available_dashboard_providers() -> list[str]:
    return sorted(_REGISTRY)


def get_dashboard_provider_by_name(name: str) -> DashboardNewsProvider:
    normalized = (name or "").strip().lower()
    provider_cls = _REGISTRY.get(normalized)
    if provider_cls is None:
        raise ValueError(
            f"Unknown dashboard provider '{normalized}'. "
            f"Supported values: {sorted(_REGISTRY)}"
        )
    return provider_cls()


def get_dashboard_provider(settings) -> DashboardNewsProvider:
    """
    Return the DashboardNewsProvider configured by ``settings.dashboard_news_provider``.

    Supported values (DASHBOARD_NEWS_PROVIDER env var):
        fixtures  — DashboardFixturesProvider (default, offline/tests)
        live      — DashboardLiveProvider (public RSS feeds, no key; falls back to fixtures)
        gdelt     — DashboardGdeltProvider (open GDELT index, no key; falls back to fixtures)

    Raises ValueError for unknown provider names so misconfiguration is caught at startup.
    """
    name = settings.dashboard_news_provider.strip().lower()
    try:
        return get_dashboard_provider_by_name(name)
    except ValueError as exc:
        raise ValueError(
            f"Unknown DASHBOARD_NEWS_PROVIDER='{name}'. "
            f"Supported values: {sorted(_REGISTRY)}"
        ) from exc
