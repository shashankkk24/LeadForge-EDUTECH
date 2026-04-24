"""
Configuration management for LeadForge EDU backend.
Loads environment variables and provides app configuration.
"""

import os
from functools import lru_cache
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://neondb_owner:npg_hVuBbD1yM7cL@ep-lively-frost-ae2m0s7o-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require",
    )

    # Gemini AI
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)

    # SMTP Email
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "465"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER", None)
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD", None)

    # Reddit API
    REDDIT_CLIENT_ID: Optional[str] = os.getenv("REDDIT_CLIENT_ID", None)
    REDDIT_CLIENT_SECRET: Optional[str] = os.getenv("REDDIT_CLIENT_SECRET", None)
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "LeadForgeEDU/1.0")

    # App config
    APP_NAME: str = "LeadForge EDU"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # API
    API_PREFIX: str = "/api"
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    @property
    def has_gemini_key(self) -> bool:
        """Check if Gemini API key is configured."""
        return self.GEMINI_API_KEY is not None and self.GEMINI_API_KEY.strip() != ""

    @property
    def has_smtp_config(self) -> bool:
        """Check if SMTP configuration is complete."""
        return (
            self.SMTP_USER is not None
            and self.SMTP_PASSWORD is not None
            and self.SMTP_USER.strip() != ""
            and self.SMTP_PASSWORD.strip() != ""
        )


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()
