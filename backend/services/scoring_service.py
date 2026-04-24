"""
Lead scoring service.
Implements the Heat Score™ algorithm (0-100) with 5-signal weighting.
"""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from models import Lead
from utils.helpers import (
    calculate_recency_weight,
    get_role_weight,
    get_sentiment_weight,
    get_urgency_weight,
)

logger = logging.getLogger(__name__)


class ScoringService:
    """Lead Heat Score calculation service."""

    # Weights for each signal (must sum to 100 for percentage-based scoring)
    URGENCY_WEIGHT = 30
    SENTIMENT_WEIGHT = 25
    ROLE_WEIGHT = 20
    RECENCY_WEIGHT = 15
    SPECIFICITY_WEIGHT = 10
    TOTAL_WEIGHT = 100

    @staticmethod
    def calculate_lead_score(lead: Lead) -> tuple[int, str]:
        """
        Calculate lead heat score (0-100) and assign priority bucket.

        Args:
            lead: Lead object with analysis fields populated

        Returns:
            Tuple of (score: int, priority: str)
            Priority: "HOT" (70+), "WARM" (40-69), "COLD" (<40)
        """
        # Get individual weights (0-1 scale)
        urgency_signal = get_urgency_weight(lead.urgency_level) / 30.0
        sentiment_signal = get_sentiment_weight(lead.sentiment_score) / 25.0
        role_signal = get_role_weight(lead.detected_role) / 20.0
        recency_signal = calculate_recency_weight(lead.extracted_at)
        specificity_signal = ScoringService._calculate_specificity(lead)

        # Calculate composite score
        score = int(
            (
                ScoringService.URGENCY_WEIGHT * min(1.0, urgency_signal)
                + ScoringService.SENTIMENT_WEIGHT * min(1.0, sentiment_signal)
                + ScoringService.ROLE_WEIGHT * min(1.0, role_signal)
                + ScoringService.RECENCY_WEIGHT * recency_signal
                + ScoringService.SPECIFICITY_WEIGHT * specificity_signal
            )
            / ScoringService.TOTAL_WEIGHT
            * 100
        )

        # Clamp score between 0-100
        score = max(0, min(100, score))

        # Determine priority bucket
        if score >= 70:
            priority = "HOT"
        elif score >= 40:
            priority = "WARM"
        else:
            priority = "COLD"

        logger.info(
            f"Calculated score for lead {lead.username}: {score} ({priority}) "
            f"[urgency={urgency_signal:.2f}, sentiment={sentiment_signal:.2f}, "
            f"role={role_signal:.2f}, recency={recency_signal:.2f}, specificity={specificity_signal:.2f}]"
        )

        return score, priority

    @staticmethod
    def _calculate_specificity(lead: Lead) -> float:
        """
        Calculate specificity weight (0-1).
        Higher if lead mentions specific budget, timeline, or vendor names.
        """
        specificity_keywords = [
            "budget",
            "timeline",
            "deadline",
            "implement",
            "implementation",
            "launch",
            "deploy",
            "purchase",
            "buying",
            "pricing",
            "cost",
            "demo",
            "trial",
            "evaluation",
            "next semester",
            "next year",
            "before semester",
        ]

        content = (lead.post_content or "").lower()
        pain_point = (lead.pain_point or "").lower()
        combined = content + " " + pain_point

        count = sum(1 for keyword in specificity_keywords if keyword in combined)

        # Normalize: 0-3 mentions = 0.0-1.0
        return min(1.0, count / 3.0)

    @staticmethod
    async def rescore_all_leads(db: AsyncSession) -> int:
        """
        Rescore all leads in database.
        Useful for re-calibrating after algorithm changes.

        Args:
            db: Database session

        Returns:
            Number of leads rescored
        """
        from sqlalchemy import select

        result = await db.execute(select(Lead))
        leads = result.scalars().all()

        count = 0
        for lead in leads:
            score, priority = ScoringService.calculate_lead_score(lead)
            lead.lead_score = score
            lead.priority = priority
            count += 1

        await db.commit()
        logger.info(f"Rescored {count} leads")
        return count
