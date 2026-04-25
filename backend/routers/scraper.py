"""Scraper router — POST /scrape triggers background Reddit scrape."""

import asyncio
import json
import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from database import get_db, AsyncSessionLocal
from models import Lead, ScrapeJob
from services.nlp_service import NLPService
from services.scoring_service import ScoringService
from services.scraper_service import ScraperService
from services.gemini_service import GeminiService
from socket_manager import ws_manager   # singleton

logger        = logging.getLogger(__name__)
router        = APIRouter(prefix="/scrape", tags=["scraper"])
nlp_service   = NLPService()
gemini_svc    = GeminiService()


@router.post("", response_model=schemas.ScrapeJobResponse)
async def trigger_scrape(
    request: schemas.ScrapeJobCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict:
    scraper = ScraperService()
    job     = await scraper.create_scrape_job(db, request.platform, request.keywords)
    job_id  = str(job.id)

    background_tasks.add_task(_perform_scrape, job_id, request.platform, request.keywords)

    return {
        "id": job_id, "platform": job.platform, "keywords": job.keywords,
        "status": job.status, "started_at": job.started_at,
        "completed_at": job.completed_at, "leads_found": job.leads_found,
        "error_message": job.error_message,
    }


async def _perform_scrape(job_id: str, platform: str, keywords: List[str]):
    """Background worker — own DB session, no shared state with HTTP request."""
    scraper = ScraperService()

    async with AsyncSessionLocal() as session:
        try:
            await scraper.update_scrape_job(session, job_id, "running")
            await ws_manager.broadcast_job_status(job_id, "running", 0)

            raw_leads = await scraper.scrape(platform, keywords, limit=10)
            logger.info(f"Job {job_id}: {len(raw_leads)} raw leads scraped")

            leads_created = 0
            for raw in raw_leads:
                try:
                    content      = raw.get("post_content", "")
                    url          = raw.get("post_url", "")
                    extracted_at = raw.get("extracted_at", datetime.utcnow())

                    # NLP (local, instant)
                    pain_tags     = nlp_service.extract_pain_points(content, max_tags=3)
                    detected_role = nlp_service.detect_role(content)
                    urgency       = nlp_service.detect_urgency(content)
                    sentiment     = nlp_service.calculate_sentiment(content)

                    # Gemini intent — hard 6s timeout, fall back to mock immediately
                    try:
                        res = await asyncio.wait_for(gemini_svc.classify_intent(content), timeout=6.0)
                        intent_label = res.get("intent_label", "RESEARCH_PHASE")
                    except Exception:
                        intent_label = gemini_svc._mock_intent_response(content).get("intent_label", "RESEARCH_PHASE")

                    # Gemini pain points if NLP found nothing
                    if not pain_tags:
                        try:
                            res2 = await asyncio.wait_for(gemini_svc.extract_pain_points(content), timeout=6.0)
                            pain_tags = res2.get("pain_point_tags", [])
                        except Exception:
                            pain_tags = gemini_svc._mock_pain_points_response(content).get("pain_point_tags", [])

                    lead = Lead(
                        platform=raw.get("platform", "reddit"),
                        username=raw.get("username", "unknown"),
                        post_url=url,
                        post_content=content,
                        extracted_at=extracted_at,
                        pain_point_tags=json.dumps(pain_tags),
                        detected_role=detected_role,
                        urgency_level=urgency,
                        sentiment_score=sentiment,
                        intent_label=intent_label,
                        status="New",
                    )
                    score, priority = ScoringService.calculate_lead_score(lead)
                    lead.lead_score = score
                    lead.priority   = priority

                    session.add(lead)
                    await session.flush()   # get UUID without full commit

                    leads_created += 1

                    await ws_manager.broadcast_new_lead({
                        "id":              str(lead.id),
                        "platform":        lead.platform,
                        "username":        lead.username,
                        "post_url":        lead.post_url,
                        "post_content":    lead.post_content,
                        "pain_point_tags": pain_tags,
                        "detected_role":   lead.detected_role,
                        "urgency_level":   lead.urgency_level,
                        "sentiment_score": lead.sentiment_score,
                        "intent_label":    lead.intent_label,
                        "lead_score":      lead.lead_score,
                        "priority":        lead.priority,
                        "status":          lead.status,
                        "ai_subject":      None,
                        "ai_message":      None,
                        "notes":           None,
                        "extracted_at":    extracted_at.isoformat(),
                        "created_at":      extracted_at.isoformat(),
                        "updated_at":      extracted_at.isoformat(),
                        "sent_at":         None,
                    })
                    await asyncio.sleep(0.05)

                except Exception as e:
                    logger.error(f"Lead processing error: {e}", exc_info=True)
                    continue

            await session.commit()
            await scraper.update_scrape_job(session, job_id, "completed", leads_created)
            await ws_manager.broadcast_job_status(job_id, "completed", leads_created)
            logger.info(f"Job {job_id}: DONE — {leads_created} leads")

        except Exception as e:
            logger.error(f"Job {job_id} FAILED: {e}", exc_info=True)
            try:
                await scraper.update_scrape_job(session, job_id, "failed", error_message=str(e))
            except Exception:
                pass
            await ws_manager.broadcast_job_status(job_id, "failed", 0)


@router.get("/jobs/{job_id}", response_model=schemas.ScrapeJobResponse)
async def get_scrape_job(job_id: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(ScrapeJob).where(ScrapeJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Scrape job not found")
    return {
        "id": str(job.id), "platform": job.platform, "keywords": job.keywords,
        "status": job.status, "started_at": job.started_at,
        "completed_at": job.completed_at, "leads_found": job.leads_found,
        "error_message": job.error_message,
    }
