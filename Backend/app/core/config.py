"""
Centralised application settings — loaded once from .env via Pydantic BaseSettings.
"""

from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Runtime configuration has one source: process environment variables.
        # Docker Compose loads the repository-root .env file. Local commands
        # outside Docker should use: uvicorn --env-file ../.env ...
        extra="ignore"
    )
    PROJECT_NAME: str = "AI Learning Assistant Platform"
    API_V1_STR: str = "/api/v1"

    # Runtime environment — controls docs visibility, cookie security, log level
    ENVIRONMENT: Literal["development", "production"] = "development"
    ALLOW_LOCAL_PRODUCTION: bool = False

    # ── Database connections ──────────────────────────────────────────────────
    DATABASE_URL: str
    MONGODB_URL: str
    REDIS_URL: str

    # ── Security ─────────────────────────────────────────────────────────────
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://localhost",
        "https://127.0.0.1",
    ]
    TRUSTED_HOSTS: list[str] = ["localhost", "127.0.0.1"]
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["text", "json"] = "json"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE_SECONDS: int = 1800

    @property
    def COOKIE_SECURE(self) -> bool:
        """Automatically enforce secure cookies in production."""
        return self.ENVIRONMENT == "production"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    # ── AI keys ──────────────────────────────────────────────────────────────
    GEMINI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek/deepseek-v4-flash"
    # Base URL for the OpenAI-compatible AI provider.
    # Override in .env to switch providers without touching code.
    AI_BASE_URL: str = "https://api.cline.bot/api/v1"
    USE_DEEPSEEK: bool = False

    # ── Email (SMTP / SendGrid / Mailgun) ────────────────────────────────────
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_FROM_NAME: str = "AI Learning Assistant"
    MAIL_SERVER: str = ""
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_TIMEOUT_SECONDS: int = 15
    APP_URL: str = "http://localhost:3000"

    @property
    def mail_enabled(self) -> bool:
        """Email is enabled only when SMTP credentials are fully configured."""
        return bool(self.MAIL_SERVER and self.MAIL_USERNAME and self.MAIL_FROM)


    # ── Cloudinary ───────────────────────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    @model_validator(mode="after")
    def validate_runtime_configuration(self):
        if self.ALGORITHM != "HS256":
            raise ValueError("ALGORITHM must be HS256")
        if self.ENVIRONMENT == "production":
            weak_markers = ("change_this", "your_", "example")
            normalized_secret = self.SECRET_KEY.lower()
            if len(self.SECRET_KEY) < 64 or any(
                marker in normalized_secret for marker in weak_markers
            ):
                raise ValueError(
                    "Production SECRET_KEY must be at least 64 random characters and not a placeholder"
                )
            if not self.ALLOW_LOCAL_PRODUCTION and any(
                "localhost" in origin or "127.0.0.1" in origin
                for origin in self.BACKEND_CORS_ORIGINS
            ):
                raise ValueError("Production BACKEND_CORS_ORIGINS must use the real HTTPS domain")
            if not self.ALLOW_LOCAL_PRODUCTION and any(
                host in {"localhost", "127.0.0.1", "*"}
                for host in self.TRUSTED_HOSTS
            ):
                raise ValueError("Production TRUSTED_HOSTS must contain only real deployment hosts")
            if not self.APP_URL.startswith("https://"):
                raise ValueError("Production APP_URL must use HTTPS")
        if self.MAIL_STARTTLS and self.MAIL_SSL_TLS:
            raise ValueError("MAIL_STARTTLS and MAIL_SSL_TLS cannot both be enabled")
        if self.ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be positive")
        if self.REFRESH_TOKEN_EXPIRE_DAYS <= 0:
            raise ValueError("REFRESH_TOKEN_EXPIRE_DAYS must be positive")
        if self.ACCESS_TOKEN_EXPIRE_MINUTES >= self.REFRESH_TOKEN_EXPIRE_DAYS * 1440:
            raise ValueError("Access token must expire before refresh token")
        if self.DB_POOL_SIZE < 1 or self.DB_MAX_OVERFLOW < 0:
            raise ValueError("Database pool sizes must be valid")
        return self

settings = Settings()
## Tìm hiểu lru cache
## Nên có logic validate biến mtr
