"""
Centralised application settings — loaded once from .env via Pydantic BaseSettings.
"""

from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Learning Assistant Platform"
    API_V1_STR: str = "/api/v1"

    # Runtime environment — controls docs visibility, cookie security, log level
    ENVIRONMENT: Literal["development", "production"] = "development"

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

    @property
    def COOKIE_SECURE(self) -> bool:
        """Automatically enforce secure cookies in production."""
        return self.ENVIRONMENT == "production"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    # ── AI keys ──────────────────────────────────────────────────────────────
    GEMINI_API_KEY: str = ""
    NVIDIA_API_KEY: str = ""
    NVIDIA_MODEL: str = "meta/llama-3.1-8b-instruct"
    USE_NVIDIA: bool = False

    # ── Email (SMTP / SendGrid / Mailgun) ────────────────────────────────────
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_FROM_NAME: str = "AI Learning Assistant"
    MAIL_SERVER: str = ""
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    @property
    def mail_enabled(self) -> bool:
        """Email is enabled only when SMTP credentials are fully configured."""
        return bool(self.MAIL_SERVER and self.MAIL_USERNAME and self.MAIL_FROM)

    # ── Cloudinary ───────────────────────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
