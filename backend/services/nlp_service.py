"""
NLP service for lead analysis.
Uses spaCy for named entity recognition and basic text analysis.
"""

import logging
import re
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# Try to load spaCy model, graceful fallback if not available
try:
    import spacy

    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except (ImportError, OSError):
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available - using basic NLP fallback")
    nlp = None


class NLPService:
    """Natural Language Processing service for lead analysis."""

    # Pain point keywords mapped to snake_case tags
    PAIN_POINT_PATTERNS = {
        "manual_attendance_tracking": [
            r"manual attendance",
            r"attendance tracking",
            r"track attendance",
            r"attendance system",
        ],
        "parent_communication_gap": [
            r"parent communication",
            r"parent engagement",
            r"communicate with parents",
            r"parent updates",
        ],
        "exam_result_delays": [
            r"exam result",
            r"grade.*report",
            r"result.*publish",
            r"slow report card",
        ],
        "manual_grading": [
            r"manual grad",
            r"grade by hand",
            r"tedious grad",
        ],
        "time_consuming_admin": [
            r"time.*consum",
            r"administrative.*burden",
            r"paperwork",
            r"manual process",
        ],
        "insufficient_analytics": [
            r"analytic",
            r"insights",
            r"dashboard",
            r"report",
        ],
        "poor_student_engagement": [
            r"student engagement",
            r"engagement.*low",
            r"drop.*rate",
        ],
        "scheduling_conflicts": [
            r"schedul",
            r"timetable",
            r"class.*conflict",
        ],
        "fee_management_issues": [
            r"fee",
            r"payment",
            r"billing",
            r"collect.*fee",
        ],
        "data_security_concerns": [
            r"security",
            r"privacy",
            r"data.*protect",
        ],
    }

    # Role detection patterns
    ROLE_PATTERNS = {
        "principal": [r"principal", r"headmaster", r"headmistress", r"director"],
        "admin": [r"administrator", r"admin", r"school admin", r"administrator"],
        "teacher": [r"teacher", r"educator", r"instructor", r"professor"],
        "superintendent": [r"superintendent", r"district", r"school board"],
    }

    # Urgency indicators
    URGENCY_INDICATORS = {
        "high": [r"asap", r"urgent", r"immediately", r"desperately", r"critical", r"emergency"],
        "medium": [r"soon", r"quickly", r"need.*now", r"before.*semester", r"by.*date"],
        "low": [r"eventually", r"someday", r"future", r"considering"],
    }

    @staticmethod
    def extract_pain_points(text: str, max_tags: int = 3) -> List[str]:
        """
        Extract pain point tags from text.

        Args:
            text: Post or lead content
            max_tags: Maximum number of tags to return

        Returns:
            List of snake_case pain point tags
        """
        if not text:
            return []

        text_lower = text.lower()
        matched_tags = []

        for tag, patterns in NLPService.PAIN_POINT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matched_tags.append(tag)
                    break  # Avoid duplicates for same tag

        # Remove duplicates and limit to max_tags
        matched_tags = list(dict.fromkeys(matched_tags))[:max_tags]
        logger.debug(f"Extracted pain points: {matched_tags}")
        return matched_tags

    @staticmethod
    def detect_role(text: str) -> Optional[str]:
        """
        Detect user role from text.

        Args:
            text: Post or lead content

        Returns:
            Detected role or None
        """
        if not text:
            return None

        text_lower = text.lower()

        # Check principal/director first (most valuable)
        for role, patterns in [
            ("principal", NLPService.ROLE_PATTERNS["principal"]),
            ("admin", NLPService.ROLE_PATTERNS["admin"]),
            ("teacher", NLPService.ROLE_PATTERNS["teacher"]),
            ("superintendent", NLPService.ROLE_PATTERNS["superintendent"]),
        ]:
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    logger.debug(f"Detected role: {role}")
                    return role

        return None

    @staticmethod
    def detect_urgency(text: str) -> str:
        """
        Detect urgency level from text.

        Args:
            text: Post or lead content

        Returns:
            Urgency level: "high", "medium", or "low" (default)
        """
        if not text:
            return "low"

        text_lower = text.lower()

        # Check high urgency first
        for pattern in NLPService.URGENCY_INDICATORS["high"]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.debug("Detected high urgency")
                return "high"

        # Check medium urgency
        for pattern in NLPService.URGENCY_INDICATORS["medium"]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.debug("Detected medium urgency")
                return "medium"

        # Default to low
        return "low"

    @staticmethod
    def extract_entities(text: str) -> dict:
        """
        Extract named entities from text using spaCy.

        Args:
            text: Post or lead content

        Returns:
            Dictionary with extracted entities
        """
        entities = {"schools": [], "locations": [], "organizations": [], "grades": []}

        if not SPACY_AVAILABLE or not nlp:
            return entities

        try:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PERSON", "GPE"]:
                    entities["organizations"].append(ent.text)
                elif ent.label_ == "GPE":
                    entities["locations"].append(ent.text)

        except Exception as e:
            logger.warning(f"Error extracting entities: {e}")

        return entities

    @staticmethod
    def calculate_sentiment(text: str) -> float:
        """
        Simple sentiment analysis (0-1 scale, negative=frustrated).

        Args:
            text: Post or lead content

        Returns:
            Sentiment score from -1.0 (negative) to 1.0 (positive)
        """
        if not text:
            return 0.0

        negative_words = [
            "terrible",
            "awful",
            "hate",
            "frustrated",
            "frustrated",
            "struggling",
            "problem",
            "issue",
            "broken",
            "slow",
            "expensive",
            "worst",
            "bad",
            "poor",
        ]
        positive_words = [
            "great",
            "excellent",
            "love",
            "amazing",
            "wonderful",
            "happy",
            "satisfied",
            "good",
            "best",
        ]

        text_lower = text.lower()

        negative_count = sum(1 for word in negative_words if word in text_lower)
        positive_count = sum(1 for word in positive_words if word in text_lower)

        if negative_count == 0 and positive_count == 0:
            return 0.0

        score = (positive_count - negative_count) / max(1, negative_count + positive_count)
        return max(-1.0, min(1.0, score))
