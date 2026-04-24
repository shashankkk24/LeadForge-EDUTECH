"""
Pydantic schemas for request/response validation.
Defines data contracts for all API endpoints.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============ LEAD SCHEMAS ============


class LeadBase(BaseModel):
    """Base schema for Lead data."""

    platform: str
    username: str
    post_url: str
    post_content: str


class LeadCreate(LeadBase):
    """Schema for creating a new lead."""

    pain_point: Optional[str] = None
    pain_point_tags: List[str] = Field(default_factory=list)
    detected_role: Optional[str] = None
    urgency_level: Optional[str] = None
    sentiment_score: Optional[float] = None
    intent_label: Optional[str] = None
    lead_score: int = 0
    priority: str = "COLD"
    status: str = "New"


class LeadUpdate(BaseModel):
    """Schema for updating a lead."""

    status: Optional[str] = None
    notes: Optional[str] = None
    ai_message: Optional[str] = None
    ai_subject: Optional[str] = None
    pain_point: Optional[str] = None
    pain_point_tags: Optional[List[str]] = None


class LeadResponse(LeadBase):
    """Schema for lead response."""

    id: str
    pain_point: Optional[str] = None
    pain_point_tags: List[str]
    detected_role: Optional[str] = None
    urgency_level: Optional[str] = None
    sentiment_score: Optional[float] = None
    intent_label: Optional[str] = None
    lead_score: int
    priority: str
    status: str
    ai_message: Optional[str] = None
    ai_subject: Optional[str] = None
    sent_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ OUTREACH SCHEMAS ============


class OutreachLogCreate(BaseModel):
    """Schema for creating an outreach log."""

    lead_id: str
    subject: str
    message_body: str
    sent_to: str
    sent_via: str = "smtp"
    status: str = "sent"


class OutreachLogResponse(BaseModel):
    """Schema for outreach log response."""

    id: str
    lead_id: str
    subject: str
    message_body: str
    sent_to: str
    sent_via: str
    status: str
    sent_at: datetime

    class Config:
        from_attributes = True


# ============ SCRAPE JOB SCHEMAS ============


class ScrapeJobCreate(BaseModel):
    """Schema for creating a scrape job."""

    platform: str
    keywords: List[str]


class ScrapeJobResponse(BaseModel):
    """Schema for scrape job response."""

    id: str
    platform: str
    keywords: List[str]
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    leads_found: int
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


# ============ AI MESSAGE GENERATION ============


class GenerateMessageRequest(BaseModel):
    """Request to generate AI outreach message."""

    lead_id: str


class GenerateMessageResponse(BaseModel):
    """Response from AI message generation."""

    subject: str
    body: str
    confidence: float = 0.95


# ============ EMAIL SENDING ============


class SendEmailRequest(BaseModel):
    """Request to send email."""

    lead_id: str
    recipient_email: str
    subject: Optional[str] = None
    body: Optional[str] = None


class SendEmailResponse(BaseModel):
    """Response from email sending."""

    success: bool
    message: str
    outreach_log_id: Optional[str] = None


# ============ INTELLIGENCE CARD ============


class IntelligenceCard(BaseModel):
    """AI-generated sales intelligence for a lead."""

    lead_id: str
    talk_track: str
    feature_highlights: List[str]
    objection_responses: dict
    follow_up_timing: str


# ============ DASHBOARD/LIST RESPONSES ============


class LeadListResponse(BaseModel):
    """Response for list of leads with pagination."""

    total: int
    page: int
    page_size: int
    leads: List[LeadResponse]


class DashboardStats(BaseModel):
    """Dashboard statistics."""

    total_leads: int
    hot_leads: int
    warm_leads: int
    cold_leads: int
    contacted_leads: int
    closed_leads: int
