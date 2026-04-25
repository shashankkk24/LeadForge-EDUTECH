"""Leads router — CRUD + stats."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from database import get_db
from models import Lead

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=schemas.LeadListResponse)
async def list_leads(
    db:       AsyncSession = Depends(get_db),
    status:   Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    skip:     int = Query(0, ge=0),
    limit:    int = Query(100, ge=1, le=200),
):
    q = select(Lead)
    cq = select(func.count()).select_from(Lead)

    if status:
        q  = q.where(Lead.status == status)
        cq = cq.where(Lead.status == status)
    if priority:
        q  = q.where(Lead.priority == priority)
        cq = cq.where(Lead.priority == priority)

    q = q.order_by(desc(Lead.created_at))

    total  = (await db.execute(cq)).scalar_one()
    leads  = (await db.execute(q.offset(skip).limit(limit))).scalars().all()

    return {"total": total, "page": skip // limit + 1, "page_size": limit, "leads": leads}


@router.get("/stats", response_model=schemas.DashboardStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    async def count(where=None):
        q = select(func.count()).select_from(Lead)
        if where is not None:
            q = q.where(where)
        return (await db.execute(q)).scalar_one()

    return {
        "total_leads":     await count(),
        "hot_leads":       await count(Lead.priority == "HOT"),
        "warm_leads":      await count(Lead.priority == "WARM"),
        "cold_leads":      await count(Lead.priority == "COLD"),
        "contacted_leads": await count(Lead.status == "Contacted"),
        "closed_leads":    await count(Lead.status == "Closed"),
    }


@router.get("/hot", response_model=list[schemas.LeadResponse])
async def get_hot_leads(db: AsyncSession = Depends(get_db), limit: int = Query(10)):
    result = await db.execute(
        select(Lead).where(Lead.priority == "HOT").order_by(desc(Lead.lead_score)).limit(limit)
    )
    return result.scalars().all()


@router.get("/{lead_id}", response_model=schemas.LeadResponse)
async def get_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead   = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=schemas.LeadResponse)
async def update_lead(lead_id: str, update: schemas.LeadUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead   = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if update.status          is not None: lead.status          = update.status
    if update.notes           is not None: lead.notes           = update.notes
    if update.ai_message      is not None: lead.ai_message      = update.ai_message
    if update.ai_subject      is not None: lead.ai_subject      = update.ai_subject
    if update.pain_point      is not None: lead.pain_point      = update.pain_point
    if update.pain_point_tags is not None:
        import json
        lead.pain_point_tags = json.dumps(update.pain_point_tags)

    await db.commit()
    await db.refresh(lead)
    return lead


@router.delete("/{lead_id}")
async def delete_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead   = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    await db.delete(lead)
    await db.commit()
    return {"message": f"Lead {lead_id} deleted"}
