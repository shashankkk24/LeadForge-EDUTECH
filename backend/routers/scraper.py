"""
Scraper API router.
Handles POST /scrape endpoint to trigger scraping jobs and lead extraction.
"""

import asyncio
import logging
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from config import get_settings
from database import get_db
from models import Lead
from services.nlp_service import NLPService
from services.scoring_service import ScoringService
from services.scraper_service import ScraperService
from websocket.manager import WebSocketManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scrape", tags=["scraper"])

settings = get_settings()
ws_manager = WebSocketManager()


@router.post("", response_model=schemas.ScrapeJobResponse)
async def trigger_scrape(
    request: schemas.ScrapeJobCreate,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None,
) -> dict:
    """
    Trigger a scraping job.

    Request Body:
    - platform: Platform to scrape (reddit, twitter, forum)
    - keywords: List of keywords to search for

    Returns:
        ScrapeJob object with job ID and initial status
    """
    logger.info(f"Received scrape request for {request.platform} with keywords: {request.keywords}")

    # Create scraper service
    scraper = ScraperService(
        client_id=settings.REDDIT_CLIENT_ID,
        client_secret=settings.REDDIT_CLIENT_SECRET,
    )

    # Create scrape job record
    job = await scraper.create_scrape_job(db, request.platform, request.keywords)

    # Add background task to perform scraping
    if background_tasks:
        background_tasks.add_task(
            _perform_scrape,
            job_id=str(job.id),
            platform=request.platform,
            keywords=request.keywords,
            scraper=scraper,
            db=db,
        )

    logger.info(f"Created scrape job {job.id}")

    return {
        "id": str(job.id),
        "platform": job.platform,
        "keywords": job.keywords,
        "status": job.status,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "leads_found": job.leads_found,
        "error_message": job.error_message,
    }


async def _perform_scrape(
    job_id: str,
    platform: str,
    keywords: List[str],
    scraper: ScraperService,
    db: AsyncSession,
):
    """
    Perform scraping in background and update database.

    Args:
        job_id: ID of the scrape job
        platform: Platform to scrape
        keywords: Keywords to search
        scraper: ScraperService instance
        db: Database session
    """
    try:
        # Update job status
        await scraper.update_scrape_job(db, job_id, "running")
        await ws_manager.broadcast_job_status(job_id, "running", 0)

        # Scrape leads
        logger.info(f"Starting scrape job {job_id} on {platform}")
        raw_leads = await scraper.scrape_reddit(keywords, limit=5)

        # Process and save leads
        nlp_service = NLPService()
        leads_created = 0

        for raw_lead in raw_leads:
            try:
                # Extract NLP features
                pain_points = nlp_service.extract_pain_points(raw_lead["post_content"], max_tags=3)
                detected_role = nlp_service.detect_role(raw_lead["post_content"])
                urgency = nlp_service.detect_urgency(raw_lead["post_content"])
                sentiment = nlp_service.calculate_sentiment(raw_lead["post_content"])

                # Create lead object
                lead = Lead(
                    platform=raw_lead["platform"],
                    username=raw_lead["username"],
                    post_url=raw_lead["post_url"],
                    post_content=raw_lead["post_content"],
                    extracted_at=raw_lead["extracted_at"],
                    pain_point_tags=pain_points,
                    detected_role=detected_role,
                    urgency_level=urgency,
                    sentiment_score=sentiment,
                    status="New",
                    intent_label="RESEARCH_PHASE",  # Default, overridden by Gemini
                )

                # Calculate lead score
                score, priority = ScoringService.calculate_lead_score(lead)
                lead.lead_score = score
                lead.priority = priority

                db.add(lead)
                leads_created += 1

                # Broadcast new lead via WebSocket
                await ws_manager.broadcast_new_lead(
                    {
                        "id": str(lead.id),
                        "username": lead.username,
                        "priority": lead.priority,
                        "score": lead.lead_score,
                        "pain_points": lead.pain_point_tags,
                    }
                )

            except Exception as e:
                logger.error(f"Error processing lead: {e}")
                continue

        # Commit all leads
        await db.commit()

        # Update job status
        await scraper.update_scrape_job(db, job_id, "completed", leads_created)
        await ws_manager.broadcast_job_status(job_id, "completed", leads_created)

        logger.info(f"Scrape job {job_id} completed. Created {leads_created} leads.")

    except Exception as e:
        logger.error(f"Error in scrape job {job_id}: {e}")
        await scraper.update_scrape_job(db, job_id, "failed", error_message=str(e))
        await ws_manager.broadcast_job_status(job_id, "failed", 0)


@router.get("/jobs/{job_id}", response_model=schemas.ScrapeJobResponse)
async def get_scrape_job(job_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    """
    Get scrape job status.

    Path Parameters:
    - job_id: ID of the scrape job

    Returns:
        ScrapeJob object with current status
    """
    from sqlalchemy import select

    from models import ScrapeJob

    result = await db.execute(select(ScrapeJob).where(ScrapeJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        logger.warning(f"Scrape job not found: {job_id}")
        raise HTTPException(status_code=404, detail="Scrape job not found")

    return {
        "id": str(job.id),
        "platform": job.platform,
        "keywords": job.keywords,
        "status": job.status,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "leads_found": job.leads_found,
        "error_message": job.error_message,
    }
