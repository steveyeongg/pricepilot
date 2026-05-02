from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    secret_key: str = "dev-secret-change-in-production"
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    database_url: str = "postgresql+asyncpg://pricepilot:pricepilot@localhost:5432/pricepilot"
    redis_url: str = ""

    scrape_request_delay_ms: int = 1500
    scrape_max_retries: int = 3
    scrape_timeout_secs: int = 30
    proxy_list: str = ""

    price_check_interval_minutes: int = 60
    alert_check_interval_minutes: int = 15

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def proxies(self) -> list[str]:
        if not self.proxy_list:
            return []
        return [p.strip() for p in self.proxy_list.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
