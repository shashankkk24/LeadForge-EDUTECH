"""
Seed data script for demo/testing.
Creates 20 realistic mock leads with varied characteristics.

Usage:
    python scripts/seed_leads.py
"""

import asyncio
import sys
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, "..")

from database import Base
from models import Lead
from services.scoring_service import ScoringService


# Sample seed data - 20 realistic EdTech leads
SEED_LEADS = [
    {
        "platform": "reddit",
        "username": "principal_johnson",
        "post_url": "https://reddit.com/r/education/comments/abc123",
        "post_content": "We desperately need to replace our manual attendance system ASAP. Currently taking 3 hours daily. Budget approved for next semester implementation. Any recommendations for K-12 attendance software?",
        "pain_point_tags": ["manual_attendance_tracking", "time_consuming_admin"],
        "detected_role": "principal",
        "urgency_level": "high",
        "sentiment_score": -0.85,
        "intent_label": "ACTIVELY_SEEKING",
    },
    {
        "platform": "reddit",
        "username": "teacher_smith",
        "post_url": "https://reddit.com/r/education/comments/def456",
        "post_content": "Spent 15 hours last week grading manually. Is there any automated grading system that actually works for essay-based assignments?",
        "pain_point_tags": ["manual_grading", "time_consuming_admin"],
        "detected_role": "teacher",
        "urgency_level": "high",
        "sentiment_score": -0.9,
        "intent_label": "FRUSTRATED_CURRENT_USER",
    },
    {
        "platform": "reddit",
        "username": "admin_patel",
        "post_url": "https://reddit.com/r/education/comments/ghi789",
        "post_content": "Our current LMS is terrible. Looking for alternatives that integrate with Google Classroom. Who's had good experiences with K-12 LMS solutions?",
        "pain_point_tags": ["insufficient_analytics", "poor_student_engagement"],
        "detected_role": "admin",
        "urgency_level": "medium",
        "sentiment_score": -0.7,
        "intent_label": "RESEARCH_PHASE",
    },
    {
        "platform": "reddit",
        "username": "dean_wilson",
        "post_url": "https://reddit.com/r/education/comments/jkl012",
        "post_content": "Parent communication is completely fragmented. Emails, calls, messages... we need one unified platform. Budget available. Demo availability important.",
        "pain_point_tags": ["parent_communication_gap"],
        "detected_role": "admin",
        "urgency_level": "high",
        "sentiment_score": -0.75,
        "intent_label": "BUDGET_APPROVED",
    },
    {
        "platform": "reddit",
        "username": "headmaster_khan",
        "post_url": "https://reddit.com/r/education/comments/mno345",
        "post_content": "Fee collection is a nightmare with spreadsheets. We need automated fee management software urgently. Implement before next academic year.",
        "pain_point_tags": ["fee_management_issues"],
        "detected_role": "principal",
        "urgency_level": "high",
        "sentiment_score": -0.8,
        "intent_label": "ACTIVELY_SEEKING",
    },
    {
        "platform": "reddit",
        "username": "coord_garcia",
        "post_url": "https://reddit.com/r/education/comments/pqr678",
        "post_content": "Exam result publishing takes forever. Students wait 3-4 weeks. Looking for digital report card solutions that can publish instantly.",
        "pain_point_tags": ["exam_result_delays"],
        "detected_role": "admin",
        "urgency_level": "medium",
        "sentiment_score": -0.65,
        "intent_label": "FRUSTRATED_CURRENT_USER",
    },
    {
        "platform": "reddit",
        "username": "staff_chen",
        "post_url": "https://reddit.com/r/education/comments/stu901",
        "post_content": "Anyone using school management software? We're evaluating options. Would love recommendations based on your experiences.",
        "pain_point_tags": ["time_consuming_admin"],
        "detected_role": "admin",
        "urgency_level": "medium",
        "sentiment_score": 0.2,
        "intent_label": "PEER_RECOMMENDATION_ASK",
    },
    {
        "platform": "reddit",
        "username": "teacher_nguyen",
        "post_url": "https://reddit.com/r/education/comments/vwx234",
        "post_content": "Tried our old scheduling tool last year - nightmare. Looking for better timetable software for next semester.",
        "pain_point_tags": ["scheduling_conflicts"],
        "detected_role": "teacher",
        "urgency_level": "medium",
        "sentiment_score": -0.6,
        "intent_label": "RESEARCH_PHASE",
    },
    {
        "platform": "reddit",
        "username": "principal_lee",
        "post_url": "https://reddit.com/r/education/comments/yza567",
        "post_content": "URGENT: Need to migrate to cloud-based system ASAP due to security concerns with our current setup. Anyone have recommendations?",
        "pain_point_tags": ["data_security_concerns"],
        "detected_role": "principal",
        "urgency_level": "high",
        "sentiment_score": -0.9,
        "intent_label": "ACTIVELY_SEEKING",
    },
    {
        "platform": "reddit",
        "username": "teacher_brown",
        "post_url": "https://reddit.com/r/education/comments/abc890",
        "post_content": "Looking for EdTech solutions. What software are schools using in 2024?",
        "pain_point_tags": [],
        "detected_role": "teacher",
        "urgency_level": "low",
        "sentiment_score": 0.3,
        "intent_label": "RESEARCH_PHASE",
    },
    {
        "platform": "reddit",
        "username": "admin_rodriguez",
        "post_url": "https://reddit.com/r/education/comments/def123",
        "post_content": "Student engagement is down. Looking for interactive learning platforms. Budget is secured for Q1 implementation.",
        "pain_point_tags": ["poor_student_engagement"],
        "detected_role": "admin",
        "urgency_level": "high",
        "sentiment_score": -0.5,
        "intent_label": "BUDGET_APPROVED",
    },
    {
        "platform": "reddit",
        "username": "coord_torres",
        "post_url": "https://reddit.com/r/education/comments/ghi456",
        "post_content": "Thinking about switching from our current system next year. Any suggestions appreciated.",
        "pain_point_tags": ["manual_grading"],
        "detected_role": "admin",
        "urgency_level": "low",
        "sentiment_score": 0.0,
        "intent_label": "RESEARCH_PHASE",
    },
    {
        "platform": "reddit",
        "username": "principal_martinez",
        "post_url": "https://reddit.com/r/education/comments/jkl789",
        "post_content": "Data security and privacy are critical. Need ERP with enterprise-level security. Evaluation starting next month.",
        "pain_point_tags": ["data_security_concerns"],
        "detected_role": "principal",
        "urgency_level": "high",
        "sentiment_score": 0.1,
        "intent_label": "ACTIVELY_SEEKING",
    },
    {
        "platform": "reddit",
        "username": "teacher_white",
        "post_url": "https://reddit.com/r/education/comments/mno012",
        "post_content": "Our manual attendance tracking is outdated. Looking for modern alternatives with mobile app support.",
        "pain_point_tags": ["manual_attendance_tracking"],
        "detected_role": "teacher",
        "urgency_level": "medium",
        "sentiment_score": -0.55,
        "intent_label": "FRUSTRATED_CURRENT_USER",
    },
    {
        "platform": "reddit",
        "username": "admin_garcia",
        "post_url": "https://reddit.com/r/education/comments/pqr345",
        "post_content": "Desperately need parent communication solution. Parents complain constantly about lack of real-time updates. Budget is ready.",
        "pain_point_tags": ["parent_communication_gap"],
        "detected_role": "admin",
        "urgency_level": "high",
        "sentiment_score": -0.8,
        "intent_label": "ACTIVELY_SEEKING",
    },
    {
        "platform": "reddit",
        "username": "principal_jackson",
        "post_url": "https://reddit.com/r/education/comments/stu678",
        "post_content": "Consolidating multiple systems into one ERP. Evaluating school management software. Decision by end of quarter.",
        "pain_point_tags": ["time_consuming_admin"],
        "detected_role": "principal",
        "urgency_level": "high",
        "sentiment_score": -0.3,
        "intent_label": "BUDGET_APPROVED",
    },
    {
        "platform": "reddit",
        "username": "coord_miller",
        "post_url": "https://reddit.com/r/education/comments/vwx890",
        "post_content": "Has anyone tried cloud-based school ERP? Looking for scalable solution for 10 campuses.",
        "pain_point_tags": [],
        "detected_role": "admin",
        "urgency_level": "medium",
        "sentiment_score": 0.0,
        "intent_label": "RESEARCH_PHASE",
    },
    {
        "platform": "reddit",
        "username": "teacher_davis",
        "post_url": "https://reddit.com/r/education/comments/yza123",
        "post_content": "Tedious grade entry process. What tools do other schools use for streamlined grading workflows?",
        "pain_point_tags": ["manual_grading"],
        "detected_role": "teacher",
        "urgency_level": "low",
        "sentiment_score": -0.5,
        "intent_label": "PEER_RECOMMENDATION_ASK",
    },
    {
        "platform": "reddit",
        "username": "principal_harris",
        "post_url": "https://reddit.com/r/education/comments/abc234",
        "post_content": "Managing multiple schools efficiently requires integrated software. Looking for established vendors with proven track record.",
        "pain_point_tags": ["time_consuming_admin"],
        "detected_role": "principal",
        "urgency_level": "medium",
        "sentiment_score": -0.2,
        "intent_label": "RESEARCH_PHASE",
    },
]


async def seed_database():
    """
    Seed database with sample leads.
    """
    # Create database engine
    from config import get_settings

    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    AsyncSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with AsyncSessionLocal() as session:
        print(f"Seeding {len(SEED_LEADS)} leads...")

        for i, lead_data in enumerate(SEED_LEADS, 1):
            # Create lead object
            lead = Lead(
                platform=lead_data["platform"],
                username=lead_data["username"],
                post_url=lead_data["post_url"],
                post_content=lead_data["post_content"],
                pain_point_tags=lead_data.get("pain_point_tags", []),
                detected_role=lead_data.get("detected_role"),
                urgency_level=lead_data.get("urgency_level"),
                sentiment_score=lead_data.get("sentiment_score"),
                intent_label=lead_data.get("intent_label"),
                status="New",
            )

            # Calculate score
            score, priority = ScoringService.calculate_lead_score(lead)
            lead.lead_score = score
            lead.priority = priority

            session.add(lead)

            print(f"  [{i:2d}] {lead_data['username']:20s} | Score: {score:3d} | {priority:5s}")

        # Commit all leads
        await session.commit()

    await engine.dispose()
    print(f"\n✓ Successfully seeded {len(SEED_LEADS)} leads")


if __name__ == "__main__":
    # Run seed function
    asyncio.run(seed_database())
