"""
Multi-platform scraper service for extracting leads from multiple sources:
- Reddit (PRAW)
- LinkedIn (Selenium)
- Apify (web scraping platform)
- Generic web scraping (Selenium)
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from models import Lead, ScrapeJob

logger = logging.getLogger(__name__)
settings = get_settings()

# Optional imports
try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    logger.warning("PRAW not installed")

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium not installed")

try:
    from apify_client import ApifyClient
    APIFY_AVAILABLE = True
except ImportError:
    APIFY_AVAILABLE = False
    logger.warning("Apify client not installed")

try:
    from linkedin_api import Linkedin
    LINKEDIN_UNOFFICIAL_AVAILABLE = True
except ImportError:
    LINKEDIN_UNOFFICIAL_AVAILABLE = False
    logger.warning("linkedin-api not installed")


class LinkedInScraper:
    """Scraper for LinkedIn using Selenium and unofficial LinkedIn API."""

    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        """Initialize LinkedIn scraper."""
        self.email = email or settings.LINKEDIN_EMAIL
        self.password = password or settings.LINKEDIN_PASSWORD
        self.driver = None
        self.available = SELENIUM_AVAILABLE

    def _init_driver(self):
        """Initialize Selenium WebDriver."""
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium not available for LinkedIn scraping")
            return False

        try:
            browser = settings.SELENIUM_BROWSER.lower()
            headless = settings.SELENIUM_HEADLESS

            if browser == "chrome":
                options = webdriver.ChromeOptions()
                if headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            elif browser == "firefox":
                options = webdriver.FirefoxOptions()
                if headless:
                    options.add_argument("--headless")
                
                service = Service(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)
            else:
                logger.error(f"Unsupported browser: {browser}")
                return False

            logger.info(f"WebDriver initialized: {browser}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            return False

    async def scrape_linkedin_posts(
        self, keywords: List[str], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Scrape LinkedIn posts matching keywords using Selenium.

        Args:
            keywords: List of search keywords
            limit: Number of posts per keyword

        Returns:
            List of lead dictionaries
        """
        if not self.email or not self.password:
            logger.warning("LinkedIn credentials not configured")
            return []

        if not self._init_driver():
            return []

        leads = []
        try:
            # Login to LinkedIn
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for login form and fill credentials
            wait = WebDriverWait(self.driver, 10)
            email_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
            email_field.send_keys(self.email)
            
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            
            # Click login button
            login_btn = self.driver.find_element(By.XPATH, "//button[@aria-label='Sign in']")
            login_btn.click()
            
            # Wait for dashboard to load
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "global-nav")))
            
            for keyword in keywords:
                logger.info(f"Scraping LinkedIn for: {keyword}")
                
                # Search for keyword
                self.driver.get(f"https://www.linkedin.com/search/results/content/?keywords={keyword}")
                
                await asyncio.sleep(2)  # Wait for page load
                
                # Extract posts
                posts = self.driver.find_elements(By.CLASS_NAME, "base-feed-list__item")
                
                for post in posts[:limit]:
                    try:
                        post_text = post.find_element(By.CLASS_NAME, "feed-shared-text").text
                        author = post.find_element(By.CLASS_NAME, "hoverable-link").text
                        
                        lead = {
                            "platform": "linkedin",
                            "username": author,
                            "post_url": self.driver.current_url,
                            "post_content": post_text,
                            "extracted_at": datetime.utcnow(),
                        }
                        leads.append(lead)
                    except Exception as e:
                        logger.debug(f"Error extracting post: {e}")
                        continue
            
            logger.info(f"Scraped {len(leads)} leads from LinkedIn")
            return leads

        except Exception as e:
            logger.error(f"LinkedIn scraping error: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()

    async def scrape_linkedin_unofficial(
        self, keywords: List[str], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Scrape LinkedIn using unofficial API (faster, no login required).

        Args:
            keywords: List of search keywords
            limit: Number of results per keyword

        Returns:
            List of lead dictionaries
        """
        if not LINKEDIN_UNOFFICIAL_AVAILABLE:
            logger.warning("linkedin-api not installed")
            return []

        leads = []
        try:
            api = Linkedin(self.email, self.password)
            
            for keyword in keywords:
                logger.info(f"Searching LinkedIn for: {keyword}")
                
                # Search for people matching keywords
                results = api.search_people(
                    keywords=keyword,
                    limit=limit,
                )
                
                for person in results:
                    lead = {
                        "platform": "linkedin",
                        "username": person.get("name", "Unknown"),
                        "post_url": person.get("profile_url", ""),
                        "post_content": person.get("headline", "") + " - " + person.get("location", ""),
                        "extracted_at": datetime.utcnow(),
                    }
                    leads.append(lead)
            
            logger.info(f"Found {len(leads)} contacts on LinkedIn")
            return leads

        except Exception as e:
            logger.error(f"LinkedIn unofficial API error: {e}")
            return []


class ApifyScraper:
    """Scraper using Apify platform for distributed web scraping."""

    def __init__(self, api_token: Optional[str] = None):
        """Initialize Apify scraper."""
        self.api_token = api_token or settings.APIFY_API_TOKEN
        self.client = None
        self.available = APIFY_AVAILABLE and self.api_token

        if self.available:
            try:
                self.client = ApifyClient(self.api_token)
                logger.info("Apify client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Apify: {e}")
                self.available = False

    async def scrape_with_actor(
        self, actor_id: str, input_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Run an Apify actor and extract leads.

        Args:
            actor_id: Apify actor ID (e.g., 'jbMR8dEWC5OmBWHJh' for Google Search)
            input_data: Input parameters for the actor

        Returns:
            List of extracted data
        """
        if not self.available:
            logger.warning("Apify not configured")
            return []

        try:
            logger.info(f"Running Apify actor: {actor_id}")
            
            # Run the actor
            run = self.client.actor(actor_id).call(run_input=input_data)
            
            # Get results from dataset
            dataset_items = self.client.dataset(run["defaultDatasetId"]).list_items()
            
            leads = []
            for item in dataset_items.get("items", []):
                leads.append(item)
            
            logger.info(f"Apify actor returned {len(leads)} results")
            return leads

        except Exception as e:
            logger.error(f"Apify actor error: {e}")
            return []

    async def scrape_search_results(
        self, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Scrape Google search results using Apify.

        Args:
            query: Search query
            limit: Number of results

        Returns:
            List of search results
        """
        input_data = {
            "queries": query,
            "maxPagesPerQuery": 1,
            "maxResultsPerPage": limit,
        }
        
        # Google Search Scraper actor ID
        actor_id = settings.APIFY_ACTOR_ID or "jbMR8dEWC5OmBWHJh"
        
        return await self.scrape_with_actor(actor_id, input_data)

    async def scrape_linkedin_profiles(
        self, search_query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Scrape LinkedIn profiles using Apify.

        Args:
            search_query: Search query for LinkedIn
            limit: Number of profiles

        Returns:
            List of profile data
        """
        input_data = {
            "searchQuery": search_query,
            "maxResults": limit,
            "waitForPageLoad": True,
        }
        
        # LinkedIn Scraper actor ID (example)
        actor_id = "61RPP7dywgAH6w8nL"  # LinkedIn scraper
        
        return await self.scrape_with_actor(actor_id, input_data)


class GenericWebScraper:
    """Generic web scraper for custom websites using Selenium."""

    def __init__(self):
        """Initialize web scraper."""
        self.driver = None
        self.available = SELENIUM_AVAILABLE

    def _init_driver(self):
        """Initialize Selenium WebDriver."""
        if not SELENIUM_AVAILABLE:
            return False

        try:
            browser = settings.SELENIUM_BROWSER.lower()
            headless = settings.SELENIUM_HEADLESS

            if browser == "chrome":
                options = webdriver.ChromeOptions()
                if headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            elif browser == "firefox":
                options = webdriver.FirefoxOptions()
                if headless:
                    options.add_argument("--headless")
                
                service = Service(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)
            
            return True

        except Exception as e:
            logger.error(f"WebDriver init error: {e}")
            return False

    async def scrape_website(
        self,
        url: str,
        selector: str,
        extract_fields: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        """
        Scrape a website and extract structured data.

        Args:
            url: Website URL to scrape
            selector: CSS selector for items to extract
            extract_fields: Dict of field_name -> CSS_selector

        Returns:
            List of extracted items
        """
        if not self._init_driver():
            return []

        items = []
        try:
            logger.info(f"Scraping {url}")
            self.driver.get(url)
            
            wait = WebDriverWait(self.driver, settings.SELENIUM_TIMEOUT)
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
            
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            
            for element in elements:
                item = {}
                for field_name, field_selector in extract_fields.items():
                    try:
                        field_value = element.find_element(By.CSS_SELECTOR, field_selector).text
                        item[field_name] = field_value
                    except:
                        item[field_name] = None
                
                items.append(item)
            
            logger.info(f"Extracted {len(items)} items from {url}")
            return items

        except Exception as e:
            logger.error(f"Web scraping error: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()


class MultiSourceScraperService:
    """Unified scraper service for multiple platforms."""

    def __init__(self):
        """Initialize all scraper sources."""
        self.linkedin_scraper = LinkedInScraper()
        self.apify_scraper = ApifyScraper()
        self.web_scraper = GenericWebScraper()

    async def scrape_all_sources(
        self, keywords: List[str], limit: int = 10, db: Optional[AsyncSession] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scrape all available sources concurrently.

        Args:
            keywords: Search keywords
            limit: Results per source
            db: Optional database session for saving

        Returns:
            Dictionary of platform -> leads
        """
        results = {
            "linkedin": [],
            "apify": [],
            "web": [],
        }

        tasks = []

        if settings.ENABLE_LINKEDIN_SCRAPER:
            tasks.append(
                self._scrape_linkedin(keywords, limit)
            )

        if settings.ENABLE_APIFY_SCRAPER:
            tasks.append(
                self._scrape_apify(keywords, limit)
            )

        if tasks:
            all_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(all_results):
                if isinstance(result, Exception):
                    logger.error(f"Scraper task error: {result}")
                elif i == 0 and settings.ENABLE_LINKEDIN_SCRAPER:
                    results["linkedin"] = result
                elif settings.ENABLE_APIFY_SCRAPER:
                    results["apify"] = result

        if db:
            for platform, leads in results.items():
                if leads:
                    await self._save_leads(leads, db, platform)

        return results

    async def _scrape_linkedin(
        self, keywords: List[str], limit: int
    ) -> List[Dict[str, Any]]:
        """Scrape LinkedIn with fallback options."""
        try:
            if settings.LINKEDIN_ACCESS_TOKEN:
                logger.info("Using LinkedIn official API (todo)")
                # Implement official API when available
                return []
            elif settings.LINKEDIN_EMAIL and settings.LINKEDIN_PASSWORD:
                # Try unofficial API first (faster)
                leads = await self.linkedin_scraper.scrape_linkedin_unofficial(
                    keywords, limit
                )
                if leads:
                    return leads
                
                # Fallback to Selenium
                return await self.linkedin_scraper.scrape_linkedin_posts(
                    keywords, limit
                )
        except Exception as e:
            logger.error(f"LinkedIn scraping failed: {e}")
        
        return []

    async def _scrape_apify(
        self, keywords: List[str], limit: int
    ) -> List[Dict[str, Any]]:
        """Scrape using Apify."""
        leads = []
        try:
            for keyword in keywords:
                results = await self.apify_scraper.scrape_search_results(keyword, limit)
                leads.extend(results)
        except Exception as e:
            logger.error(f"Apify scraping failed: {e}")
        
        return leads

    async def _save_leads(
        self, leads: List[Dict[str, Any]], db: AsyncSession, platform: str
    ) -> int:
        """Save leads to database."""
        count = 0
        for lead_data in leads:
            try:
                lead = Lead(
                    platform=platform,
                    username=lead_data.get("username", "unknown"),
                    post_url=lead_data.get("post_url", ""),
                    post_content=lead_data.get("post_content", ""),
                    extracted_at=datetime.utcnow(),
                    status="New",
                    lead_score=0,
                    priority="COLD",
                )
                db.add(lead)
                count += 1
            except Exception as e:
                logger.error(f"Error saving lead: {e}")
                continue

        if count > 0:
            await db.commit()
            logger.info(f"Saved {count} leads from {platform}")
        
        return count
