"""
SQLAlchemy ORM models for LeadForge EDU.
Defines Lead, OutreachLog, and ScrapeJob tables.
"""

from datetime import datetime
from typing import List

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    Column,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UUID,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Lead(Base):
    """
    Lead model representing extracted and scored sales leads.
    Stores lead information, AI analysis, and outreach status.
    """

    __tablename__ = "leads"

    # Primary key
    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())

    # Source information
    platform = Column(String(50))  # reddit / twitter / forum
    username = Column(String(255))
    post_url = Column(Text)
    post_content = Column(Text)

    # Timestamps
    extracted_at = Column(TIMESTAMP, server_default=func.now())
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # NLP Analysis
    pain_point = Column(Text)  # Summary of detected problems
    pain_point_tags = Column(JSON, default=[])  # snake_case tags array
    detected_role = Column(String(100))  # teacher / admin / principal
    urgency_level = Column(String(20))  # high / medium / low
    sentiment_score = Column(Float)  # -1.0 to 1.0

    # Intent Classification (Feature 1: EduIntent Classifier)
    intent_label = Column(String(50))  # ACTIVELY_SEEKING, FRUSTRATED_CURRENT_USER, etc.

    # Scoring (Feature 3: Lead Heat Score)
    lead_score = Column(Integer, default=0)  # 0-100
    priority = Column(String(10))  # HOT / WARM / COLD

    # Status tracking
    status = Column(String(20), default="New")  # New / Drafted / Contacted / Closed

    # AI Outreach (Feature 4: Contextual Outreach)
    ai_message = Column(Text)  # Generated message body
    ai_subject = Column(Text)  # Generated subject line
    sent_at = Column(TIMESTAMP)  # When email was sent

    # Additional notes
    notes = Column(Text)

    # Relationships
    outreach_logs = relationship("OutreachLog", back_populates="lead", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index("idx_leads_status", "status"),
        Index("idx_leads_priority", "priority"),
        Index("idx_leads_score", "lead_score"),
        Index("idx_leads_created", "created_at"),
    )

    def __repr__(self):
        return f"<Lead {self.id}: {self.username} [{self.priority}]>"


class OutreachLog(Base):
    """
    Outreach log for tracking sent messages and their status.
    """

    __tablename__ = "outreach_logs"

    # Primary key
    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())

    # Foreign key
    lead_id = Column(UUID, ForeignKey("leads.id"), nullable=False)

    # Message details
    subject = Column(Text)
    message_body = Column(Text)
    sent_to = Column(String(255))  # Email or DM address

    # Dispatch details
    sent_via = Column(String(50))  # smtp / api / simulated
    sent_at = Column(TIMESTAMP, server_default=func.now())
    status = Column(String(20))  # sent / failed / simulated / pending

    # Relationship
    lead = relationship("Lead", back_populates="outreach_logs")

    def __repr__(self):
        return f"<OutreachLog {self.id}: {self.status}>"


class ScrapeJob(Base):
    """
    Scrape job tracking for monitoring scraper runs.
    """

    __tablename__ = "scrape_jobs"

    # Primary key
    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())

    # Job details
    platform = Column(String(50))  # reddit / twitter / forum
    keywords = Column(JSON, default=[])  # List of keywords used

    # Status tracking
    status = Column(String(20), default="pending")  # pending / running / completed / failed
    started_at = Column(TIMESTAMP, server_default=func.now())
    completed_at = Column(TIMESTAMP)

    # Results
    leads_found = Column(Integer, default=0)
    error_message = Column(Text)

    def __repr__(self):
        return f"<ScrapeJob {self.id}: {self.status}>"
