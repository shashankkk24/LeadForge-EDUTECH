"""
Tests for scraper service and lead extraction pipeline.
"""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import Lead, ScrapeJob
from services.scraper_service import ScraperService


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
def scraper_service():
    """Create scraper service instance."""
    return ScraperService(client_id=None, client_secret=None)


# ============ MOCK SCRAPE TESTS ============


def test_should_return_leads_from_mock_scrape(scraper_service: ScraperService):
    """Test that mock scraper returns sample leads."""
    # Arrange
    keywords = ["school management software"]

    # Act
    leads = scraper_service._mock_scrape(keywords, limit=5)

    # Assert
    assert len(leads) > 0
    assert all("platform" in lead for lead in leads)
    assert all("username" in lead for lead in leads)
    assert all("post_content" in lead for lead in leads)


def test_should_respect_limit_in_mock_scrape(scraper_service: ScraperService):
    """Test that mock scraper respects limit parameter."""
    # Arrange
    keywords = ["school software"]

    # Act
    leads = scraper_service._mock_scrape(keywords, limit=3)

    # Assert
    assert len(leads) <= 3


def test_should_return_reddit_platform_in_mock_leads(scraper_service: ScraperService):
    """Test that mock leads are marked as reddit platform."""
    # Arrange
    keywords = ["software"]

    # Act
    leads = scraper_service._mock_scrape(keywords, limit=1)

    # Assert
    assert leads[0]["platform"] == "reddit"
    assert leads[0]["post_url"].startswith("https://reddit.com")


# ============ SAVE LEADS TESTS ============


@pytest.mark.asyncio
async def test_should_save_leads_to_database(test_db: AsyncSession, scraper_service: ScraperService):
    """Test that leads are saved to database."""
    # Arrange
    raw_leads = scraper_service._mock_scrape(["school software"], limit=2)

    # Act
    count = await scraper_service.save_leads_to_db(raw_leads, test_db)

    # Assert
    assert count == 2
    from sqlalchemy import select

    result = await test_db.execute(select(Lead))
    saved_leads = result.scalars().all()
    assert len(saved_leads) == 2


@pytest.mark.asyncio
async def test_should_set_default_values_when_saving_leads(test_db: AsyncSession, scraper_service: ScraperService):
    """Test that default values are set when saving leads."""
    # Arrange
    raw_leads = [
        {
            "platform": "reddit",
            "username": "test_user",
            "post_url": "http://example.com",
            "post_content": "Test content",
            "extracted_at": datetime.utcnow(),
        }
    ]

    # Act
    await scraper_service.save_leads_to_db(raw_leads, test_db)

    # Assert
    from sqlalchemy import select

    result = await test_db.execute(select(Lead))
    lead = result.scalars().first()
    assert lead.status == "New"
    assert lead.lead_score == 0
    assert lead.priority == "COLD"


@pytest.mark.asyncio
async def test_should_handle_missing_fields_in_raw_lead(test_db: AsyncSession, scraper_service: ScraperService):
    """Test that missing fields are handled gracefully."""
    # Arrange
    raw_leads = [
        {
            "platform": "reddit",
            "username": "user",
        }
    ]

    # Act
    count = await scraper_service.save_leads_to_db(raw_leads, test_db)

    # Assert
    assert count == 1


# ============ SCRAPE JOB TESTS ============


@pytest.mark.asyncio
async def test_should_create_scrape_job(test_db: AsyncSession, scraper_service: ScraperService):
    """Test that scrape job can be created."""
    # Arrange
    platform = "reddit"
    keywords = ["school software", "grading system"]

    # Act
    job = await scraper_service.create_scrape_job(test_db, platform, keywords)

    # Assert
    assert job.id is not None
    assert job.platform == platform
    assert job.keywords == keywords
    assert job.status == "pending"


@pytest.mark.asyncio
async def test_should_update_scrape_job_status(test_db: AsyncSession, scraper_service: ScraperService):
    """Test that scrape job status can be updated."""
    # Arrange
    job = await scraper_service.create_scrape_job(test_db, "reddit", ["test"])
    job_id = str(job.id)

    # Act
    await scraper_service.update_scrape_job(
        test_db,
        job_id,
        "completed",
        leads_found=5,
    )

    # Assert
    from sqlalchemy import select

    result = await test_db.execute(select(ScrapeJob).where(ScrapeJob.id == job_id))
    updated_job = result.scalar_one_or_none()
    assert updated_job.status == "completed"
    assert updated_job.leads_found == 5
    assert updated_job.completed_at is not None


@pytest.mark.asyncio
async def test_should_store_error_message_on_job_failure(test_db: AsyncSession, scraper_service: ScraperService):
    """Test that error message is stored on job failure."""
    # Arrange
    job = await scraper_service.create_scrape_job(test_db, "reddit", ["test"])
    job_id = str(job.id)
    error_msg = "API rate limit exceeded"

    # Act
    await scraper_service.update_scrape_job(
        test_db,
        job_id,
        "failed",
        error_message=error_msg,
    )

    # Assert
    from sqlalchemy import select

    result = await test_db.execute(select(ScrapeJob).where(ScrapeJob.id == job_id))
    updated_job = result.scalar_one_or_none()
    assert updated_job.status == "failed"
    assert updated_job.error_message == error_msg
