from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    database_url: str = "sqlite:///./the_giver.db"
    rate_limit_enabled: bool = True
    rate_limit_analyze_requests: int = 5
    rate_limit_analyze_window_seconds: int = 3600
    cors_origins: str = "http://localhost:3000"
    dashboard_news_provider: str = "fixtures"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
