"""Pydantic schemas for LeadForge EDU API."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ── Lead ──────────────────────────────────────────────────────────────────────

class LeadResponse(BaseModel):
    id:               Any                       # UUID
    platform:         Optional[str] = None
    username:         Optional[str] = None
    post_url:         Optional[str] = None
    post_content:     Optional[str] = None

    pain_point:       Optional[str]   = None
    pain_point_tags:  List[str]       = Field(default_factory=list)
    detected_role:    Optional[str]   = None
    urgency_level:    Optional[str]   = None
    sentiment_score:  Optional[float] = None
    intent_label:     Optional[str]   = None

    lead_score:  int = 0
    priority:    str = "COLD"
    status:      str = "New"

    ai_subject:  Optional[str]      = None
    ai_message:  Optional[str]      = None
    sent_at:     Optional[datetime] = None
    notes:       Optional[str]      = None

    extracted_at: Optional[datetime] = None
    created_at:   Optional[datetime] = None
    updated_at:   Optional[datetime] = None

    @field_validator("pain_point_tags", mode="before")
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v or []

    @field_validator("id", mode="before")
    @classmethod
    def stringify_id(cls, v):
        return str(v) if v is not None else v

    class Config:
        from_attributes = True


class LeadUpdate(BaseModel):
    status:          Optional[str]       = None
    notes:           Optional[str]       = None
    ai_message:      Optional[str]       = None
    ai_subject:      Optional[str]       = None
    pain_point:      Optional[str]       = None
    pain_point_tags: Optional[List[str]] = None


class LeadListResponse(BaseModel):
    total:     int
    page:      int
    page_size: int
    leads:     List[LeadResponse]


class DashboardStats(BaseModel):
    total_leads:     int
    hot_leads:       int
    warm_leads:      int
    cold_leads:      int
    contacted_leads: int
    closed_leads:    int


# ── Scrape Job ────────────────────────────────────────────────────────────────

class ScrapeJobCreate(BaseModel):
    platform: str = "reddit"
    keywords: List[str] = Field(default=[
        "school ERP", "LMS recommendation",
        "grading system", "attendance software",
        "school management software",
    ])


class ScrapeJobResponse(BaseModel):
    id:            Any
    platform:      str
    keywords:      List[str]
    status:        str
    started_at:    Optional[datetime] = None
    completed_at:  Optional[datetime] = None
    leads_found:   int = 0
    error_message: Optional[str] = None

    @field_validator("id", mode="before")
    @classmethod
    def stringify_id(cls, v):
        return str(v) if v is not None else v

    class Config:
        from_attributes = True


# ── Outreach ──────────────────────────────────────────────────────────────────

class GenerateMessageResponse(BaseModel):
    subject:    str
    body:       str
    confidence: float = 0.85


class SendEmailRequest(BaseModel):
    lead_id:         str
    recipient_email: str
    subject:         Optional[str] = None
    body:            Optional[str] = None


class SendEmailResponse(BaseModel):
    success:          bool
    message:          str
    outreach_log_id:  Optional[str] = None


class OutreachLogResponse(BaseModel):
    id:           Any
    lead_id:      Any
    subject:      Optional[str]      = None
    message_body: Optional[str]      = None
    sent_to:      Optional[str]      = None
    sent_via:     Optional[str]      = None
    status:       Optional[str]      = None
    sent_at:      Optional[datetime] = None

    @field_validator("id", "lead_id", mode="before")
    @classmethod
    def stringify_ids(cls, v):
        return str(v) if v is not None else v

    class Config:
        from_attributes = True


# ── Intelligence ──────────────────────────────────────────────────────────────

class IntelligenceCard(BaseModel):
    lead_id:             str
    talk_track:          str
    feature_highlights:  List[str]
    objection_responses: Dict[str, str]
    follow_up_timing:    str
