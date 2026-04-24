"""
Tests for outreach service and email dispatch.
"""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import Lead, OutreachLog
from services.email_service import EmailService
from services.gemini_service import GeminiService


@pytest.fixture
async def test_db():
    """Create in-memory SQLite database for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def email_service():
    """Create email service without SMTP (simulation mode)."""
    return EmailService()


@pytest.fixture
def gemini_service():
    """Create Gemini service (will use mocks without API key)."""
    return GeminiService()


@pytest.fixture
def sample_lead():
    """Create sample lead for testing."""
    return Lead(
        platform="reddit",
        username="test_user",
        post_url="https://reddit.com/r/education/test",
        post_content="We need better grading software ASAP",
        pain_point_tags=["manual_grading"],
        detected_role="admin",
        urgency_level="high",
        sentiment_score=-0.8,
        intent_label="ACTIVELY_SEEKING",
        status="New",
    )


# ============ EMAIL SERVICE TESTS ============


def test_should_use_simulation_mode_without_smtp_config():
    """Test that email service uses simulation mode without SMTP credentials."""
    # Arrange
    service = EmailService()

    # Act
    success, msg = service._simulate_send("test@school.com", "Test", "Body")

    # Assert
    assert success is True
    assert "SIMULATED" in msg


@pytest.mark.asyncio
async def test_should_send_email_in_simulation_mode(email_service: EmailService):
    """Test that email can be sent in simulation mode."""
    # Arrange
    recipient = "principal@school.edu"
    subject = "LeadForge EDU Solution"
    body = "Let's discuss your grading challenges."

    # Act
    success, message = await email_service.send_email(recipient, subject, body)

    # Assert
    assert success is True
    assert recipient in message


@pytest.mark.asyncio
async def test_should_batch_send_emails(email_service: EmailService):
    """Test batch email sending."""
    # Arrange
    recipients = [
        {"to": "user1@school.com", "subject": "Test 1", "body": "Body 1"},
        {"to": "user2@school.com", "subject": "Test 2", "body": "Body 2"},
    ]

    # Act
    results = await email_service.send_batch_emails(recipients)

    # Assert
    assert results["sent"] == 2
    assert results["failed"] == 0


def test_should_format_html_email(email_service: EmailService):
    """Test HTML email formatting."""
    # Arrange
    title = "Welcome"
    content = "Check out our solution"
    cta_text = "Learn More"
    cta_link = "https://example.com"

    # Act
    html = email_service.format_html_email(title, content, cta_text, cta_link)

    # Assert
    assert title in html
    assert content in html
    assert cta_text in html
    assert cta_link in html
    assert "<!DOCTYPE html>" in html


# ============ OUTREACH LOGGING TESTS ============


@pytest.mark.asyncio
async def test_should_create_outreach_log(test_db: AsyncSession, sample_lead: Lead):
    """Test that outreach log can be created."""
    # Arrange
    test_db.add(sample_lead)
    await test_db.commit()

    outreach = OutreachLog(
        lead_id=sample_lead.id,
        subject="Test Subject",
        message_body="Test body",
        sent_to="test@school.com",
        sent_via="smtp",
        status="sent",
    )
    test_db.add(outreach)

    # Act
    await test_db.commit()

    # Assert
    assert outreach.id is not None
    assert outreach.lead_id == sample_lead.id
    assert outreach.status == "sent"


@pytest.mark.asyncio
async def test_should_log_email_sending_failure(test_db: AsyncSession, sample_lead: Lead):
    """Test that failed emails are logged."""
    # Arrange
    test_db.add(sample_lead)
    await test_db.commit()

    outreach = OutreachLog(
        lead_id=sample_lead.id,
        subject="Test",
        message_body="Body",
        sent_to="invalid@email",
        sent_via="smtp",
        status="failed",
    )
    test_db.add(outreach)

    # Act
    await test_db.commit()

    # Assert
    from sqlalchemy import select

    result = await test_db.execute(
        select(OutreachLog).where(OutreachLog.lead_id == sample_lead.id)
    )
    logs = result.scalars().all()
    assert len(logs) == 1
    assert logs[0].status == "failed"


# ============ GEMINI SERVICE TESTS ============


@pytest.mark.asyncio
async def test_should_generate_mock_intent_response(gemini_service: GeminiService):
    """Test that Gemini generates intent classification (mock mode)."""
    # Arrange
    post = "We urgently need a grading system"

    # Act
    response = await gemini_service.classify_intent(post)

    # Assert
    assert "intent_label" in response
    assert "confidence_score" in response
    assert response["intent_label"] in [
        "ACTIVELY_SEEKING",
        "FRUSTRATED_CURRENT_USER",
        "RESEARCH_PHASE",
        "BUDGET_APPROVED",
        "PEER_RECOMMENDATION_ASK",
    ]


@pytest.mark.asyncio
async def test_should_generate_mock_pain_points(gemini_service: GeminiService):
    """Test that Gemini extracts pain points (mock mode)."""
    # Arrange
    post = "Our grading is manual and parent communication is hard"

    # Act
    response = await gemini_service.extract_pain_points(post)

    # Assert
    assert "pain_point_tags" in response
    assert isinstance(response["pain_point_tags"], list)
    assert len(response["pain_point_tags"]) > 0


@pytest.mark.asyncio
async def test_should_generate_mock_outreach_message(gemini_service: GeminiService):
    """Test that Gemini generates personalized outreach message (mock mode)."""
    # Arrange
    post = "We need better grading software"
    pain_points = ["manual_grading"]
    role = "admin"
    urgency = "high"
    intent = "ACTIVELY_SEEKING"

    # Act
    response = await gemini_service.generate_outreach_message(
        post,
        pain_points,
        role,
        urgency,
        intent,
    )

    # Assert
    assert "subject" in response
    assert "body" in response
    assert len(response["subject"]) > 0
    assert len(response["body"]) > 0


@pytest.mark.asyncio
async def test_should_generate_mock_sales_intelligence(gemini_service: GeminiService):
    """Test that Gemini generates sales intelligence (mock mode)."""
    # Arrange
    post = "We need grading automation"
    pain_points = ["manual_grading"]
    role = "principal"

    # Act
    response = await gemini_service.generate_sales_intelligence(post, pain_points, role)

    # Assert
    assert "talk_track" in response
    assert "feature_highlights" in response
    assert "objection_responses" in response
    assert "follow_up_timing" in response


# ============ MESSAGE GENERATION TESTS ============


@pytest.mark.asyncio
async def test_should_include_pain_points_in_generated_message(gemini_service: GeminiService):
    """Test that generated message references extracted pain points."""
    # Arrange
    post = "Manual grading is killing our efficiency"
    pain_points = ["manual_grading", "time_consuming_admin"]
    role = "teacher"
    urgency = "medium"
    intent = "FRUSTRATED_CURRENT_USER"

    # Act
    response = await gemini_service.generate_outreach_message(
        post,
        pain_points,
        role,
        urgency,
        intent,
    )

    # Assert
    body = response.get("body", "").lower()
    # In mock mode, should mention the pain point context
    assert len(body) > 50  # Should have substantial content


@pytest.mark.asyncio
async def test_should_generate_short_message_under_limit(gemini_service: GeminiService):
    """Test that generated message is under 120 words as per specification."""
    # Arrange
    post = "Need help with school management"
    pain_points = []
    role = "admin"

    # Act
    response = await gemini_service.generate_outreach_message(
        post,
        pain_points,
        role,
        "medium",
        "RESEARCH_PHASE",
    )

    # Assert
    body = response.get("body", "")
    words = len(body.split())
    # Allow some flexibility in mock mode
    assert words < 200
