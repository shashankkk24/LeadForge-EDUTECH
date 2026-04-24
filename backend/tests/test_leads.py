"""
Tests for Lead CRUD operations and scoring.
Uses pytest with async support and database fixtures.
"""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import Lead
from services.scoring_service import ScoringService
from schemas import LeadCreate


# ============ FIXTURES ============


@pytest.fixture
async def test_db():
    """Create in-memory SQLite database for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def sample_lead():
    """Create sample lead for testing."""
    return Lead(
        platform="reddit",
        username="test_user",
        post_url="https://reddit.com/r/education/test",
        post_content="We desperately need better grading software ASAP",
        extracted_at=datetime.utcnow(),
        pain_point_tags=["manual_grading"],
        detected_role="admin",
        urgency_level="high",
        sentiment_score=-0.8,
        intent_label="ACTIVELY_SEEKING",
        status="New",
    )


# ============ CREATE TESTS ============


@pytest.mark.asyncio
async def test_should_create_lead_in_database(test_db: AsyncSession, sample_lead: Lead):
    """Test that a lead can be created and saved to database."""
    # Arrange
    test_db.add(sample_lead)

    # Act
    await test_db.commit()
    await test_db.refresh(sample_lead)

    # Assert
    assert sample_lead.id is not None
    assert sample_lead.username == "test_user"
    assert sample_lead.platform == "reddit"


@pytest.mark.asyncio
async def test_should_create_lead_with_default_values(test_db: AsyncSession):
    """Test that lead defaults are applied on creation."""
    # Arrange
    lead = Lead(
        platform="reddit",
        username="user",
        post_url="http://example.com",
        post_content="Test content",
    )
    test_db.add(lead)

    # Act
    await test_db.commit()

    # Assert
    assert lead.status == "New"
    assert lead.lead_score == 0
    assert lead.created_at is not None


# ============ SCORING TESTS ============


def test_should_score_hot_lead_with_high_urgency_and_negative_sentiment():
    """Test that HOT score is assigned to urgent, frustrated leads."""
    # Arrange
    lead = Lead(
        platform="reddit",
        username="principal",
        post_url="http://example.com",
        post_content="We need grading software ASAP",
        detected_role="principal",
        urgency_level="high",
        sentiment_score=-0.9,
        pain_point_tags=["manual_grading"],
    )

    # Act
    score, priority = ScoringService.calculate_lead_score(lead)

    # Assert
    assert priority == "HOT"
    assert score >= 70


def test_should_score_warm_lead_with_medium_signals():
    """Test that WARM score is assigned to moderate-intent leads."""
    # Arrange
    lead = Lead(
        platform="reddit",
        username="teacher",
        post_url="http://example.com",
        post_content="Considering a new LMS soon",
        detected_role="teacher",
        urgency_level="medium",
        sentiment_score=0.0,
        pain_point_tags=["manual_grading"],
    )

    # Act
    score, priority = ScoringService.calculate_lead_score(lead)

    # Assert
    assert priority == "WARM"
    assert 40 <= score < 70


def test_should_score_cold_lead_with_low_signals():
    """Test that COLD score is assigned to exploratory leads."""
    # Arrange
    lead = Lead(
        platform="reddit",
        username="researcher",
        post_url="http://example.com",
        post_content="Just researching school software options",
        detected_role="teacher",
        urgency_level="low",
        sentiment_score=0.5,
        pain_point_tags=[],
    )

    # Act
    score, priority = ScoringService.calculate_lead_score(lead)

    # Assert
    assert priority == "COLD"
    assert score < 40


def test_should_calculate_score_between_0_and_100():
    """Test that scores are always clamped between 0-100."""
    # Arrange
    lead = Lead(
        platform="reddit",
        username="user",
        post_url="http://example.com",
        post_content="Test",
    )

    # Act
    score, priority = ScoringService.calculate_lead_score(lead)

    # Assert
    assert 0 <= score <= 100


# ============ READ TESTS ============


@pytest.mark.asyncio
async def test_should_retrieve_lead_by_id(test_db: AsyncSession, sample_lead: Lead):
    """Test that lead can be retrieved by ID."""
    # Arrange
    test_db.add(sample_lead)
    await test_db.commit()
    await test_db.refresh(sample_lead)
    lead_id = sample_lead.id

    # Act
    from sqlalchemy import select

    result = await test_db.execute(select(Lead).where(Lead.id == lead_id))
    retrieved_lead = result.scalar_one_or_none()

    # Assert
    assert retrieved_lead is not None
    assert retrieved_lead.username == "test_user"


@pytest.mark.asyncio
async def test_should_return_none_for_nonexistent_lead(test_db: AsyncSession):
    """Test that retrieving nonexistent lead returns None."""
    # Arrange
    from sqlalchemy import select
    import uuid

    # Act
    result = await test_db.execute(select(Lead).where(Lead.id == str(uuid.uuid4())))
    lead = result.scalar_one_or_none()

    # Assert
    assert lead is None


# ============ UPDATE TESTS ============


@pytest.mark.asyncio
async def test_should_update_lead_status(test_db: AsyncSession, sample_lead: Lead):
    """Test that lead status can be updated."""
    # Arrange
    test_db.add(sample_lead)
    await test_db.commit()

    # Act
    sample_lead.status = "Contacted"
    await test_db.commit()
    await test_db.refresh(sample_lead)

    # Assert
    assert sample_lead.status == "Contacted"


@pytest.mark.asyncio
async def test_should_update_lead_notes(test_db: AsyncSession, sample_lead: Lead):
    """Test that lead notes can be updated."""
    # Arrange
    test_db.add(sample_lead)
    await test_db.commit()

    # Act
    sample_lead.notes = "Follow up on Friday"
    await test_db.commit()
    await test_db.refresh(sample_lead)

    # Assert
    assert sample_lead.notes == "Follow up on Friday"


# ============ DELETE TESTS ============


@pytest.mark.asyncio
async def test_should_delete_lead(test_db: AsyncSession, sample_lead: Lead):
    """Test that lead can be deleted."""
    # Arrange
    test_db.add(sample_lead)
    await test_db.commit()
    lead_id = sample_lead.id

    # Act
    await test_db.delete(sample_lead)
    await test_db.commit()

    # Assert
    from sqlalchemy import select

    result = await test_db.execute(select(Lead).where(Lead.id == lead_id))
    deleted_lead = result.scalar_one_or_none()
    assert deleted_lead is None


# ============ PAIN POINT TESTS ============


@pytest.mark.asyncio
async def test_should_store_pain_point_tags(test_db: AsyncSession):
    """Test that pain point tags are stored as array."""
    # Arrange
    lead = Lead(
        platform="reddit",
        username="user",
        post_url="http://example.com",
        post_content="Test",
        pain_point_tags=["manual_grading", "parent_communication_gap"],
    )
    test_db.add(lead)

    # Act
    await test_db.commit()

    # Assert
    assert lead.pain_point_tags == ["manual_grading", "parent_communication_gap"]
