"""Outreach router — generate messages, send emails, intelligence cards."""

import json
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
from socket_manager import ws_manager   # singleton

logger        = logging.getLogger(__name__)
router        = APIRouter(prefix="/outreach", tags=["outreach"])
gemini_svc    = GeminiService()
email_svc     = EmailService()


def _parse_tags(raw) -> list:
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return []
    return raw or []


@router.post("/generate-message/{lead_id}", response_model=schemas.GenerateMessageResponse)
async def generate_message(lead_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead   = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    tags = _parse_tags(lead.pain_point_tags)
    resp = await gemini_svc.generate_outreach_message(
        post_content=lead.post_content or "",
        pain_point_tags=tags,
        detected_role=lead.detected_role,
        urgency_level=lead.urgency_level,
        intent_label=lead.intent_label,
    )

    subject = resp.get("subject", "EdTech Solution for Your School")
    body    = resp.get("body", "")

    lead.ai_subject = subject
    lead.ai_message = body
    lead.status     = "Drafted"
    await db.commit()
    await db.refresh(lead)

    await ws_manager.broadcast_message("LEAD_UPDATED", {
        "id": str(lead.id), "status": lead.status,
        "ai_subject": lead.ai_subject, "ai_message": lead.ai_message,
    })

    return {"subject": subject, "body": body, "confidence": resp.get("confidence", 0.85)}


@router.post("/send-email/{lead_id}", response_model=schemas.SendEmailResponse)
async def send_email(lead_id: str, request: schemas.SendEmailRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead   = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    subject = request.subject or lead.ai_subject or "EdTech Solution for Your School"
    body    = request.body    or lead.ai_message or "Let's discuss how we can help your school."

    success, message = await email_svc.send_email(
        to_addr=request.recipient_email, subject=subject, body=body, html=False,
    )

    log = OutreachLog(
        lead_id=lead_id, subject=subject, message_body=body,
        sent_to=request.recipient_email,
        sent_via="smtp" if email_svc.has_smtp else "simulated",
        status="sent" if success else "failed",
        sent_at=datetime.utcnow(),
    )
    db.add(log)

    if success:
        lead.status  = "Contacted"
        lead.sent_at = datetime.utcnow()

    await db.commit()
    await db.refresh(lead)

    await ws_manager.broadcast_message("LEAD_UPDATED", {"id": str(lead.id), "status": lead.status})

    return {"success": success, "message": message, "outreach_log_id": str(log.id) if success else None}


@router.get("/intelligence/{lead_id}", response_model=schemas.IntelligenceCard)
async def get_lead_intelligence(lead_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead   = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    tags  = _parse_tags(lead.pain_point_tags)
    intel = await gemini_svc.generate_sales_intelligence(
        post_content=lead.post_content or "",
        pain_point_tags=tags,
        detected_role=lead.detected_role,
    )

    return {
        "lead_id":             lead_id,
        "talk_track":          intel.get("talk_track", ""),
        "feature_highlights":  intel.get("feature_highlights", []),
        "objection_responses": intel.get("objection_responses", {}),
        "follow_up_timing":    intel.get("follow_up_timing", ""),
    }


@router.get("/logs/{lead_id}", response_model=list[schemas.OutreachLogResponse])
async def get_outreach_logs(lead_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(OutreachLog).where(OutreachLog.lead_id == lead_id).order_by(OutreachLog.sent_at.desc())
    )
    return result.scalars().all()
