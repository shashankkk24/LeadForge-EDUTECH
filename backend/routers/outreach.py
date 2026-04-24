"""
Outreach API router.
Handles message generation and email sending endpoints.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from database import get_db
from models import Lead, OutreachLog
from services.email_service import EmailService
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/outreach", tags=["outreach"])

gemini_service = GeminiService()
email_service = EmailService()


@router.post("/generate-message/{lead_id}", response_model=schemas.GenerateMessageResponse)
async def generate_message(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Generate AI personalized outreach message for a lead.

    Path Parameters:
    - lead_id: UUID of the lead

    Returns:
        Generated message with subject and body
    """
    # Get lead from database
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()

    if not lead:
        logger.warning(f"Lead not found: {lead_id}")
        raise HTTPException(status_code=404, detail="Lead not found")

    logger.info(f"Generating message for lead {lead_id}")

    # Use Gemini to generate personalized message
    response = await gemini_service.generate_outreach_message(
        post_content=lead.post_content,
        pain_point_tags=lead.pain_point_tags or [],
        detected_role=lead.detected_role,
        urgency_level=lead.urgency_level,
        intent_label=lead.intent_label,
    )

    # Save generated message to lead
    lead.ai_subject = response.get("subject", "")
    lead.ai_message = response.get("body", "")
    lead.status = "Drafted"
    await db.commit()

    logger.info(f"Generated message for lead {lead_id}")

    return {
        "subject": response.get("subject", ""),
        "body": response.get("body", ""),
        "confidence": response.get("confidence", 0.85),
    }


@router.post("/send-email/{lead_id}", response_model=schemas.SendEmailResponse)
async def send_email(
    lead_id: str,
    request: schemas.SendEmailRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Send outreach email to lead.

    Path Parameters:
    - lead_id: UUID of the lead

    Request Body:
    - recipient_email: Email address to send to
    - subject: Optional override of generated subject
    - body: Optional override of generated body

    Returns:
        Send status and confirmation
    """
    # Get lead from database
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()

    if not lead:
        logger.warning(f"Lead not found: {lead_id}")
        raise HTTPException(status_code=404, detail="Lead not found")

    # Use provided or generated message
    subject = request.subject or lead.ai_subject or "EdTech Solution for Your School"
    body = request.body or lead.ai_message or "Let's discuss how we can help your school."

    logger.info(f"Sending email to {request.recipient_email} for lead {lead_id}")

    # Send email
    success, message = await email_service.send_email(
        to_addr=request.recipient_email,
        subject=subject,
        body=body,
        html=True,
    )

    # Log outreach
    outreach_log = OutreachLog(
        lead_id=lead_id,
        subject=subject,
        message_body=body,
        sent_to=request.recipient_email,
        sent_via="smtp",
        status="sent" if success else "failed",
        sent_at=datetime.utcnow(),
    )
    db.add(outreach_log)

    # Update lead status
    if success:
        lead.status = "Contacted"
        lead.sent_at = datetime.utcnow()
        logger.info(f"Email sent successfully for lead {lead_id}")
    else:
        logger.error(f"Email send failed for lead {lead_id}")

    await db.commit()

    return {
        "success": success,
        "message": message,
        "outreach_log_id": str(outreach_log.id) if success else None,
    }


@router.get("/intelligence/{lead_id}", response_model=schemas.IntelligenceCard)
async def get_lead_intelligence(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get AI-generated sales intelligence for a lead (Feature 7).

    Path Parameters:
    - lead_id: UUID of the lead

    Returns:
        Sales intelligence card with talk track, features, objections, timing
    """
    # Get lead from database
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()

    if not lead:
        logger.warning(f"Lead not found: {lead_id}")
        raise HTTPException(status_code=404, detail="Lead not found")

    logger.info(f"Generating intelligence for lead {lead_id}")

    # Generate sales intelligence
    intelligence = await gemini_service.generate_sales_intelligence(
        post_content=lead.post_content,
        pain_point_tags=lead.pain_point_tags or [],
        detected_role=lead.detected_role,
    )

    return {
        "lead_id": lead_id,
        "talk_track": intelligence.get("talk_track", ""),
        "feature_highlights": intelligence.get("feature_highlights", []),
        "objection_responses": intelligence.get("objection_responses", {}),
        "follow_up_timing": intelligence.get("follow_up_timing", ""),
    }


@router.get("/logs/{lead_id}", response_model=list[schemas.OutreachLogResponse])
async def get_outreach_logs(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
) -> list:
    """
    Get outreach logs for a lead.

    Path Parameters:
    - lead_id: UUID of the lead

    Returns:
        List of outreach logs
    """
    result = await db.execute(
        select(OutreachLog).where(OutreachLog.lead_id == lead_id).order_by(OutreachLog.sent_at.desc())
    )
    logs = result.scalars().all()

    return logs
