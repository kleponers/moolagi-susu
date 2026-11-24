from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_version: str = "0.1.0"
    jwt_secret_key: str = "dev-only-change-this-secret-key-min-32-chars"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    database_url: str = ""
    ml_service_url: str = "http://localhost:8001"
    gemini_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def storage_mode(self) -> str:
        return "postgres" if self.database_url.strip() else "memory"


@lru_cache
def get_settings() -> Settings:
    return Settings()
