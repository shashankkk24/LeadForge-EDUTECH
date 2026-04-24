"""
Leads API router.
Handles GET/PATCH endpoints for lead management and listing.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from database import get_db
from models import Lead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=schemas.LeadListResponse)
async def list_leads(
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    """
    List all leads with optional filters.

    Query Parameters:
    - status: Filter by status (New, Drafted, Contacted, Closed)
    - priority: Filter by priority (HOT, WARM, COLD)
    - skip: Number of records to skip (pagination)
    - limit: Number of records to return (pagination)

    Returns:
        List of leads with pagination info
    """
    query = select(Lead)

    # Apply filters
    if status:
        query = query.where(Lead.status == status)
    if priority:
        query = query.where(Lead.priority == priority)

    # Order by created date (newest first)
    query = query.order_by(desc(Lead.created_at))

    # Get total count
    count_result = await db.execute(select(Lead).distinct())
    if status:
        count_result = await db.execute(
            select(Lead).where(Lead.status == status).distinct()
        )
    if priority:
        count_result = await db.execute(
            select(Lead).where(Lead.priority == priority).distinct()
        )

    total = len(count_result.scalars().all())

    # Apply pagination
    result = await db.execute(query.offset(skip).limit(limit))
    leads = result.scalars().all()

    return {
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "leads": leads,
    }


@router.get("/hot", response_model=list[schemas.LeadResponse])
async def get_hot_leads(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
) -> list:
    """
    Get HOT priority leads (score > 70).

    Query Parameters:
    - limit: Maximum number of leads to return

    Returns:
        List of HOT leads
    """
    result = await db.execute(
        select(Lead)
        .where(Lead.priority == "HOT")
        .order_by(desc(Lead.lead_score))
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/stats", response_model=schemas.DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)) -> dict:
    """
    Get dashboard statistics.

    Returns:
        Dictionary with lead counts by priority and status
    """
    result = await db.execute(select(Lead))
    all_leads = result.scalars().all()

    return {
        "total_leads": len(all_leads),
        "hot_leads": sum(1 for l in all_leads if l.priority == "HOT"),
        "warm_leads": sum(1 for l in all_leads if l.priority == "WARM"),
        "cold_leads": sum(1 for l in all_leads if l.priority == "COLD"),
        "contacted_leads": sum(1 for l in all_leads if l.status == "Contacted"),
        "closed_leads": sum(1 for l in all_leads if l.status == "Closed"),
    }


@router.get("/{lead_id}", response_model=schemas.LeadResponse)
async def get_lead(lead_id: str, db: AsyncSession = Depends(get_db)) -> Lead:
    """
    Get detailed lead information.

    Path Parameters:
    - lead_id: UUID of the lead

    Returns:
        Detailed lead object
    """
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()

    if not lead:
        logger.warning(f"Lead not found: {lead_id}")
        raise HTTPException(status_code=404, detail="Lead not found")

    return lead


@router.patch("/{lead_id}", response_model=schemas.LeadResponse)
async def update_lead(
    lead_id: str,
    update: schemas.LeadUpdate,
    db: AsyncSession = Depends(get_db),
) -> Lead:
    """
    Update lead information.

    Path Parameters:
    - lead_id: UUID of the lead

    Request Body:
    - status: New status
    - notes: Additional notes
    - ai_message: Generated message
    - ai_subject: Message subject

    Returns:
        Updated lead object
    """
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()

    if not lead:
        logger.warning(f"Lead not found: {lead_id}")
        raise HTTPException(status_code=404, detail="Lead not found")

    # Update fields if provided
    if update.status:
        lead.status = update.status
        logger.info(f"Updated lead {lead_id} status to {update.status}")

    if update.notes:
        lead.notes = update.notes

    if update.ai_message:
        lead.ai_message = update.ai_message

    if update.ai_subject:
        lead.ai_subject = update.ai_subject

    if update.pain_point:
        lead.pain_point = update.pain_point

    if update.pain_point_tags:
        lead.pain_point_tags = update.pain_point_tags

    await db.commit()
    await db.refresh(lead)

    return lead


@router.delete("/{lead_id}")
async def delete_lead(lead_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    """
    Delete a lead.

    Path Parameters:
    - lead_id: UUID of the lead

    Returns:
        Confirmation message
    """
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()

    if not lead:
        logger.warning(f"Lead not found: {lead_id}")
        raise HTTPException(status_code=404, detail="Lead not found")

    await db.delete(lead)
    await db.commit()

    logger.info(f"Deleted lead {lead_id}")
    return {"message": f"Lead {lead_id} deleted successfully"}
