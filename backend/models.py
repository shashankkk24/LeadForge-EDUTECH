"""SQLAlchemy ORM models for LeadForge EDU."""

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON, TIMESTAMP, Column, Float, ForeignKey,
    Index, Integer, String, Text, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Lead(Base):
    __tablename__ = "leads"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform        = Column(String(50),  default="reddit")
    username        = Column(String(255))
    post_url        = Column(Text)
    post_content    = Column(Text)

    extracted_at    = Column(TIMESTAMP, default=datetime.utcnow)
    created_at      = Column(TIMESTAMP, server_default=func.now())
    updated_at      = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    pain_point      = Column(Text)
    pain_point_tags = Column(Text, default="[]")   # JSON-encoded list
    detected_role   = Column(String(100))
    urgency_level   = Column(String(20))
    sentiment_score = Column(Float)
    intent_label    = Column(String(50))

    lead_score      = Column(Integer, default=0)
    priority        = Column(String(10), default="COLD")
    status          = Column(String(20), default="New")

    ai_subject      = Column(Text)
    ai_message      = Column(Text)
    sent_at         = Column(TIMESTAMP)
    notes           = Column(Text)

    outreach_logs   = relationship("OutreachLog", back_populates="lead", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_leads_status",     "status"),
        Index("idx_leads_priority",   "priority"),
        Index("idx_leads_score",      "lead_score"),
        Index("idx_leads_created_at", "created_at"),
    )


class OutreachLog(Base):
    __tablename__ = "outreach_logs"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id      = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"))
    subject      = Column(Text)
    message_body = Column(Text)
    sent_to      = Column(String(255))
    sent_via     = Column(String(50),  default="smtp")
    status       = Column(String(20),  default="sent")
    sent_at      = Column(TIMESTAMP,   default=datetime.utcnow)

    lead = relationship("Lead", back_populates="outreach_logs")


class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform      = Column(String(50))
    keywords      = Column(JSON,      default=list)
    status        = Column(String(20), default="pending")
    started_at    = Column(TIMESTAMP,  default=datetime.utcnow)
    completed_at  = Column(TIMESTAMP)
    leads_found   = Column(Integer,    default=0)
    error_message = Column(Text)
