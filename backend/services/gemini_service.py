"""
Gemini AI service for advanced lead analysis and message generation.
Handles intent classification, pain point extraction, and email generation.
"""

import json
import logging
from typing import Optional

from config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class GeminiService:
    """Service for calling Google Gemini API."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.has_api_key = settings.has_gemini_key

        if self.has_api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel("gemini-1.5-flash")
                logger.info("Gemini API initialized successfully")
            except ImportError:
                logger.warning("google-generativeai not installed - using mock responses")
                self.client = None
                self.has_api_key = False
        else:
            logger.info("No Gemini API key provided - using mock responses")
            self.client = None

    async def classify_intent(self, post_content: str) -> dict:
        """
        Classify lead intent (Feature 1: EduIntent Classifier).

        Args:
            post_content: The user's post content

        Returns:
            Dict with intent_label, confidence_score, and notes
        """
        if not self.client:
            return self._mock_intent_response(post_content)

        try:
            prompt = f"""Analyze this EdTech lead post and classify their buying stage intent.

Post: "{post_content}"

Return ONLY valid JSON (no markdown, no extra text):
{{
  "intent_label": "ACTIVELY_SEEKING" or "FRUSTRATED_CURRENT_USER" or "RESEARCH_PHASE" or "BUDGET_APPROVED" or "PEER_RECOMMENDATION_ASK",
  "confidence_score": 0.0-1.0,
  "notes": "brief explanation"
}}"""

            response = await self._call_gemini(prompt)
            return self._parse_json_response(response)

        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            return self._mock_intent_response(post_content)

    async def extract_pain_points(self, post_content: str, max_tags: int = 3) -> dict:
        """
        Extract pain points using Gemini (Feature 2: Psychographic Pain-Point Fingerprinting).

        Args:
            post_content: The user's post content
            max_tags: Maximum number of tags

        Returns:
            Dict with pain_point_tags array and summary
        """
        if not self.client:
            return self._mock_pain_points_response(post_content)

        try:
            prompt = f"""Extract the top {max_tags} operational pain points from this school post.

Post: "{post_content}"

Return ONLY valid JSON (no markdown, no extra text):
{{
  "pain_point_tags": ["snake_case_tag1", "snake_case_tag2", "snake_case_tag3"],
  "summary": "brief summary of main problems"
}}"""

            response = await self._call_gemini(prompt)
            return self._parse_json_response(response)

        except Exception as e:
            logger.error(f"Error extracting pain points: {e}")
            return self._mock_pain_points_response(post_content)

    async def generate_outreach_message(
        self,
        post_content: str,
        pain_point_tags: list,
        detected_role: Optional[str],
        urgency_level: Optional[str],
        intent_label: Optional[str],
    ) -> dict:
        """
        Generate personalized AI outreach message (Feature 4: Contextual AI Outreach).

        Args:
            post_content: The user's actual post
            pain_point_tags: Extracted pain point tags
            detected_role: User's detected role
            urgency_level: Detected urgency
            intent_label: Intent classification

        Returns:
            Dict with subject and body
        """
        if not self.client:
            return self._mock_outreach_response(pain_point_tags)

        try:
            tags_str = ", ".join(pain_point_tags)

            prompt = f"""You are an EdTech sales representative.
Write a personalized cold outreach email to this lead:

Their post: "{post_content}"
Role: {detected_role or "Unknown"}
Pain points: {tags_str}
Urgency: {urgency_level or "Unknown"}
Intent: {intent_label or "Unknown"}

Rules:
- Reference their EXACT problem in line 1
- Mention specific solution for their stated pain
- Keep under 120 words
- Warm, not salesy tone
- End with soft CTA (15-min call)
- Do NOT use generic openings like "I hope this email finds you well"

Return ONLY valid JSON (no markdown, no extra text):
{{
  "subject": "subject line",
  "body": "email body"
}}"""

            response = await self._call_gemini(prompt)
            return self._parse_json_response(response)

        except Exception as e:
            logger.error(f"Error generating outreach message: {e}")
            return self._mock_outreach_response(pain_point_tags)

    async def generate_sales_intelligence(
        self, post_content: str, pain_point_tags: list, detected_role: Optional[str]
    ) -> dict:
        """
        Generate sales intelligence summary (Feature 7: Lead Intelligence Summary Card).

        Args:
            post_content: The user's post
            pain_point_tags: Extracted pain point tags
            detected_role: User's role

        Returns:
            Dict with talk_track, features, objections, timing
        """
        if not self.client:
            return self._mock_intelligence_response()

        try:
            tags_str = ", ".join(pain_point_tags)

            prompt = f"""You are an EdTech sales coach.
Generate sales strategy for closing this lead:

Post: "{post_content}"
Role: {detected_role or "Unknown"}
Pain points: {tags_str}

Return ONLY valid JSON (no markdown, no extra text):
{{
  "talk_track": "one-line opening",
  "feature_highlights": ["feature_1", "feature_2"],
  "objection_responses": {{"common_objection": "response"}},
  "follow_up_timing": "when to follow up"
}}"""

            response = await self._call_gemini(prompt)
            return self._parse_json_response(response)

        except Exception as e:
            logger.error(f"Error generating sales intelligence: {e}")
            return self._mock_intelligence_response()

    async def _call_gemini(self, prompt: str) -> str:
        """
        Call Gemini API with retry logic.

        Args:
            prompt: The prompt to send

        Returns:
            API response text
        """
        if not self.client:
            raise ValueError("Gemini client not initialized")

        try:
            response = self.client.generate_content(prompt)
            return response.text

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    def _parse_json_response(self, response: str) -> dict:
        """Parse JSON from Gemini response, handling markdown code blocks."""
        try:
            # Remove markdown code block if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            return json.loads(response.strip())

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}\nResponse: {response}")
            return {}

    def _mock_intent_response(self, post_content: str) -> dict:
        """Generate mock intent response for testing."""
        if "urgent" in post_content.lower() or "asap" in post_content.lower():
            return {
                "intent_label": "ACTIVELY_SEEKING",
                "confidence_score": 0.85,
                "notes": "Clear urgency signals detected",
            }
        else:
            return {
                "intent_label": "RESEARCH_PHASE",
                "confidence_score": 0.7,
                "notes": "Exploratory research mode",
            }

    def _mock_pain_points_response(self, post_content: str) -> dict:
        """Generate mock pain points response."""
        if "grading" in post_content.lower():
            return {
                "pain_point_tags": ["manual_grading", "time_consuming_admin"],
                "summary": "Struggling with manual grading processes",
            }
        else:
            return {
                "pain_point_tags": ["manual_attendance_tracking", "parent_communication_gap"],
                "summary": "General administrative challenges",
            }

    def _mock_outreach_response(self, pain_point_tags: list) -> dict:
        """Generate mock outreach message."""
        tag_str = ", ".join(pain_point_tags)
        return {
            "subject": f"Solution for {tag_str.replace('_', ' ')}",
            "body": f"""Hi,

I noticed your school is dealing with {tag_str.replace('_', ' ')}. 
We've helped 500+ schools automate these exact workflows.

Would you be open to a quick 15-minute call to explore how?

Best regards,
LeadForge EDU""",
        }

    def _mock_intelligence_response(self) -> dict:
        """Generate mock intelligence card."""
        return {
            "talk_track": "We help schools cut administrative time by 70% - would you like to see how?",
            "feature_highlights": ["Automated attendance tracking", "Real-time parent portal"],
            "objection_responses": {
                "We already use [competitor]": "Many schools switch because [reason]"
            },
            "follow_up_timing": "Follow up in 3 days if no response",
        }
