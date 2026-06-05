from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    database_url: str = "sqlite:///./verity.db"
    rate_limit_enabled: bool = True
    rate_limit_analyze_requests: int = 5
    rate_limit_analyze_window_seconds: int = 3600
    cors_origins: str = "http://localhost:3000"
    dashboard_news_provider: str = "fixtures"
    # Comma-separated provider stack for the News Integrity Feed clustering path.
    # Keep fixtures first for deterministic offline mode unless intentionally changed.
    news_feed_provider_stack: str = "fixtures"
    # Max number of raw articles read from each provider per category for feed clustering.
    news_feed_max_articles_per_provider: int = 20
    # Optional API keys for future/licensed providers. Empty by default; the app
    # never crashes when these are unset (providers stay disabled / fall back).
    newsapi_api_key: str = ""
    gnews_api_key: str = ""
    google_factcheck_api_key: str = ""
    transcription_provider: str = "mock"
    media_max_upload_bytes: int = 52_428_800
    article_extraction_enabled: bool = True
    article_extraction_timeout_seconds: float = 10.0
    article_extraction_max_bytes: int = 3_000_000
    article_extraction_min_chars: int = 250

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
