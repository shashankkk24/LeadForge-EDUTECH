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
    SMTP_USE_SSL: bool = os.getenv("SMTP_USE_SSL", "true").lower() == "true"
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "false").lower() == "true"

    # LinkedIn
    LINKEDIN_EMAIL: Optional[str] = os.getenv("LINKEDIN_EMAIL", None)
    LINKEDIN_PASSWORD: Optional[str] = os.getenv("LINKEDIN_PASSWORD", None)
    LINKEDIN_ACCESS_TOKEN: Optional[str] = os.getenv("LINKEDIN_ACCESS_TOKEN", None)

    # Apify
    APIFY_API_TOKEN: Optional[str] = os.getenv("APIFY_API_TOKEN", None)
    APIFY_ACTOR_ID: Optional[str] = os.getenv("APIFY_ACTOR_ID", None)

    # Browserbase
    BROWSERBASE_API_KEY: Optional[str] = os.getenv("BROWSERBASE_API_KEY", "bb_live_bFUP_jIwIwxv8zQC8Bwa8qXdAkc")

    # Reddit API (OAuth2 — bypasses IP rate limits)
    REDDIT_CLIENT_ID:     Optional[str] = os.getenv("REDDIT_CLIENT_ID",     None)
    REDDIT_CLIENT_SECRET: Optional[str] = os.getenv("REDDIT_CLIENT_SECRET", None)
    REDDIT_USERNAME:      str           = os.getenv("REDDIT_USERNAME",      "leadforge_bot")
    REDDIT_USER_AGENT:    str           = os.getenv("REDDIT_USER_AGENT",    "LeadForgeEDU/1.0")

    # Scraping targets and keywords
    SCRAPE_TARGETS: str = os.getenv("SCRAPE_TARGETS", "reddit.com,linkedin.com,twitter.com")
    SCRAPE_KEYWORDS: str = os.getenv("SCRAPE_KEYWORDS", "edtech,school management,student assessment")

    # Feature flags
    ENABLE_REDDIT_SCRAPER: bool = os.getenv("ENABLE_REDDIT_SCRAPER", "true").lower() == "true"
    ENABLE_LINKEDIN_SCRAPER: bool = os.getenv("ENABLE_LINKEDIN_SCRAPER", "true").lower() == "true"
    ENABLE_APIFY_SCRAPER: bool = os.getenv("ENABLE_APIFY_SCRAPER", "false").lower() == "true"
    ENABLE_SELENIUM_SCRAPER: bool = os.getenv("ENABLE_SELENIUM_SCRAPER", "false").lower() == "true"
    ENABLE_SMART_ENRICHMENT: bool = os.getenv("ENABLE_SMART_ENRICHMENT", "true").lower() == "true"

    # App config
    APP_NAME: str = "LeadForge EDU"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # API
    API_PREFIX: str = "/api"
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173", "http://localhost:5175"]

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
