"""
Utility helper functions.
"""

import logging
from datetime import datetime, timedelta
from typing import List

logger = logging.getLogger(__name__)


def extract_domain(email: str) -> str:
    """Extract domain from email address."""
    return email.split("@")[1] if "@" in email else ""


def calculate_recency_weight(created_at: datetime) -> float:
    """
    Calculate recency weight (0-1).
    Newer posts get higher weight, decays over 72 hours.
    """
    age = datetime.utcnow() - created_at
    max_age = timedelta(hours=72)

    if age >= max_age:
        return 0.0

    weight = 1.0 - (age.total_seconds() / max_age.total_seconds())
    return max(0.0, min(1.0, weight))


def get_role_weight(role: str) -> float:
    """Get weight for detected role."""
    role_weights = {
        "principal": 20,
        "headmaster": 20,
        "director": 18,
        "admin": 15,
        "administrator": 15,
        "superintendent": 18,
        "teacher": 8,
        "educator": 8,
        "staff": 5,
    }
    return float(role_weights.get(role.lower() if role else "", 5))


def get_urgency_weight(urgency_level: str) -> float:
    """Get weight for urgency level."""
    urgency_weights = {
        "high": 30,
        "urgent": 30,
        "asap": 30,
        "immediate": 30,
        "medium": 15,
        "moderate": 15,
        "low": 5,
        "eventual": 5,
    }
    return float(urgency_weights.get(urgency_level.lower() if urgency_level else "", 10))


def get_sentiment_weight(sentiment_score: float) -> float:
    """Get weight for sentiment score (negative = frustrated = hot lead)."""
    if sentiment_score is None:
        return 12.5  # neutral middle

    # More negative sentiment (frustrated) = higher weight
    # Normalize from [-1, 1] to [0, 25]
    return max(0, 12.5 - (sentiment_score * 12.5))


def format_lead_tags(tags: List[str]) -> str:
    """Format pain point tags for display."""
    return ", ".join([f"#{tag.replace('_', ' ')}" for tag in tags])


def log_action(action: str, details: dict = None):
    """Log an action with optional details."""
    msg = f"[ACTION] {action}"
    if details:
        msg += f" | {details}"
    logger.info(msg)
