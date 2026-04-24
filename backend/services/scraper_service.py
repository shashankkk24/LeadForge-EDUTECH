"""
Scraper service for extracting leads from Reddit and other sources.
Handles PRAW Reddit API and fallback mock data.
"""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from models import Lead, ScrapeJob

logger = logging.getLogger(__name__)

# Try to import PRAW
try:
    import praw

    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    logger.warning("PRAW not installed - using mock scraper")


class ScraperService:
    """Service for scraping leads from Reddit and other platforms."""

    # EdTech-related keywords
    KEYWORDS = [
        "looking for school management software",
        "need better grading system",
        "student attendance software recommendation",
        "school admin software",
        "LMS for K-12",
        "tired of manual grading",
        "parent communication app school",
        "exam management software",
        "school ERP recommendation",
        "fee management software school",
        "digital report card software",
        "online timetable generator school",
        "school communication platform",
        "EdTech software for principals",
        "replace paper based attendance",
    ]

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialize scraper with Reddit credentials (optional).

        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.reddit = None

        if PRAW_AVAILABLE and client_id and client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent="LeadForgeEDU/1.0",
                )
                logger.info("PRAW Reddit API initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize PRAW: {e} - using mock scraper")
                self.reddit = None
        else:
            logger.info("Using mock scraper (no Reddit credentials)")

    async def scrape_reddit(self, keywords: List[str], limit: int = 10) -> List[dict]:
        """
        Scrape Reddit for leads matching keywords.

        Args:
            keywords: List of search keywords
            limit: Number of posts per keyword

        Returns:
            List of lead dictionaries
        """
        if not self.reddit:
            return self._mock_scrape(keywords, limit)

        leads = []
        try:
            for keyword in keywords:
                logger.info(f"Scraping Reddit for: {keyword}")

                for submission in self.reddit.subreddit("education").search(keyword, limit=limit):
                    lead = {
                        "platform": "reddit",
                        "username": submission.author.name if submission.author else "deleted",
                        "post_url": f"https://reddit.com{submission.permalink}",
                        "post_content": submission.selftext or submission.title,
                        "extracted_at": datetime.utcnow(),
                    }
                    leads.append(lead)

        except Exception as e:
            logger.error(f"Error scraping Reddit: {e}")
            # Fall back to mock data
            return self._mock_scrape(keywords, limit)

        logger.info(f"Scraped {len(leads)} leads from Reddit")
        return leads

    def _mock_scrape(self, keywords: List[str], limit: int = 10) -> List[dict]:
        """
        Generate mock leads for testing/demo without Reddit API.

        Args:
            keywords: List of keywords (for variety)
            limit: Number of leads to generate

        Returns:
            List of mock lead dictionaries
        """
        mock_leads = [
            {
                "platform": "reddit",
                "username": "principal_johnson",
                "post_url": "https://reddit.com/r/education/comments/mock1",
                "post_content": "We desperately need a better school management system ASAP. Our current manual attendance tracking is consuming 4 hours daily and parent communication is a nightmare. Anyone have recommendations? Budget is approved for implementation by next semester.",
                "extracted_at": datetime.utcnow(),
            },
            {
                "platform": "reddit",
                "username": "teacher_smith",
                "post_url": "https://reddit.com/r/education/comments/mock2",
                "post_content": "Tired of spending 10 hours a week on manual grading. Looking for automated grading software that integrates with our LMS. What do other schools use?",
                "extracted_at": datetime.utcnow(),
            },
            {
                "platform": "reddit",
                "username": "admin_patel",
                "post_url": "https://reddit.com/r/education/comments/mock3",
                "post_content": "Our exam result publishing process is so slow. Students wait 3 weeks for grades. We need a digital report card system urgently.",
                "extracted_at": datetime.utcnow(),
            },
            {
                "platform": "reddit",
                "username": "dean_wilson",
                "post_url": "https://reddit.com/r/education/comments/mock4",
                "post_content": "School communication with parents is fragmented across emails, messages, and calls. We're looking for a unified parent engagement platform. Would love demo suggestions.",
                "extracted_at": datetime.utcnow(),
            },
            {
                "platform": "reddit",
                "username": "headmaster_khan",
                "post_url": "https://reddit.com/r/education/comments/mock5",
                "post_content": "Fee collection from students is chaotic. Currently doing it manually with spreadsheets. Any recommendations for automated fee management software? Budget OK'd. Implement before next term.",
                "extracted_at": datetime.utcnow(),
            },
        ]

        return mock_leads[:limit]

    async def save_leads_to_db(self, leads: List[dict], db: AsyncSession) -> int:
        """
        Save scraped leads to database.

        Args:
            leads: List of lead dictionaries
            db: Database session

        Returns:
            Number of leads saved
        """
        count = 0
        for lead_data in leads:
            try:
                lead = Lead(
                    platform=lead_data.get("platform", "unknown"),
                    username=lead_data.get("username", "unknown"),
                    post_url=lead_data.get("post_url", ""),
                    post_content=lead_data.get("post_content", ""),
                    extracted_at=lead_data.get("extracted_at", datetime.utcnow()),
                    status="New",
                    lead_score=0,
                    priority="COLD",
                )
                db.add(lead)
                count += 1

            except Exception as e:
                logger.error(f"Error saving lead: {e}")
                continue

        await db.commit()
        logger.info(f"Saved {count} leads to database")
        return count

    async def create_scrape_job(self, db: AsyncSession, platform: str, keywords: List[str]) -> ScrapeJob:
        """
        Create a scrape job record.

        Args:
            db: Database session
            platform: Platform being scraped (reddit, twitter, etc.)
            keywords: Keywords to search for

        Returns:
            Created ScrapeJob object
        """
        job = ScrapeJob(
            platform=platform,
            keywords=keywords,
            status="pending",
        )
        db.add(job)
        await db.commit()
        logger.info(f"Created scrape job {job.id} for {platform}")
        return job

    async def update_scrape_job(
        self,
        db: AsyncSession,
        job_id: str,
        status: str,
        leads_found: int = 0,
        error_message: Optional[str] = None,
    ):
        """
        Update scrape job status.

        Args:
            db: Database session
            job_id: Job ID to update
            status: New status (running, completed, failed)
            leads_found: Number of leads found
            error_message: Error message if failed
        """
        from sqlalchemy import select

        result = await db.execute(select(ScrapeJob).where(ScrapeJob.id == job_id))
        job = result.scalar_one_or_none()

        if job:
            job.status = status
            job.leads_found = leads_found
            if status == "completed":
                job.completed_at = datetime.utcnow()
            if error_message:
                job.error_message = error_message
            await db.commit()
            logger.info(f"Updated scrape job {job_id}: {status}")
