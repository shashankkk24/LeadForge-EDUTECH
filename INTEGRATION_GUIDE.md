# LeadForge EDU - Integration Guide

## 📋 Table of Contents
1. [SMTP Email Integration](#smtp-email-integration)
2. [LinkedIn Scraping](#linkedin-scraping)
3. [Apify Integration](#apify-integration)
4. [Selenium Browser Automation](#selenium-browser-automation)
5. [PRAW Reddit API](#praw-reddit-api)
6. [Multi-Source Scraping](#multi-source-scraping)
7. [Frontend Integration](#frontend-integration)

---

## 🔐 SMTP Email Integration

### Overview
SMTP (Simple Mail Transfer Protocol) enables the application to send real emails to leads. The system supports multiple email providers and falls back to simulation mode if credentials aren't configured.

### Supported Providers

#### **Gmail (Recommended for Testing)**

1. **Enable 2-Factor Authentication**
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password**
   - Visit https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Google will generate a 16-character password
   - **Important**: Use this generated password, NOT your main Gmail password

3. **Configure .env**
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=465
   SMTP_USE_SSL=true
   SMTP_USE_TLS=false
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_16_char_app_password_here
   ```

#### **Office 365 / Outlook**

```
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USE_SSL=false
SMTP_USE_TLS=true
SMTP_USER=your_email@company.com
SMTP_PASSWORD=your_office365_password
```

#### **Custom SMTP Server**

```
SMTP_HOST=your-smtp-server.com
SMTP_PORT=587  # or 465 for SSL
SMTP_USE_SSL=false
SMTP_USE_TLS=true
SMTP_USER=username
SMTP_PASSWORD=password
```

### Features

✅ **Sync & Async Support**
```python
# Async (recommended for FastAPI)
from services.enhanced_email_service import EnhancedEmailService

service = EnhancedEmailService()
success, msg = await service.send_email(
    to_addr="lead@company.com",
    subject="School Management Solution",
    body="<h1>Hey there!</h1><p>I noticed...</p>",
    html=True
)
```

✅ **HTML Templates**
```python
html_body = EnhancedEmailService.create_html_template(
    name="John Principal",
    company="ABC School",
    pain_point="manual grading taking 10 hours/week",
    solution="automated grading with AI",
    cta="Schedule Demo"
)

await service.send_email(
    to_addr="john@abcschool.edu",
    subject="Reduce Grading Time by 80%",
    body=html_body,
    html=True
)
```

✅ **Batch Sending**
```python
recipients = [
    {
        "to": "principal1@school1.edu",
        "subject": "School Management Solution",
        "body": "<h1>Custom message</h1>",
        "cc": ["director@school1.edu"],
        "html": True
    },
    {
        "to": "admin@school2.edu",
        "subject": "Attendance System Demo",
        "body": "<h1>Another message</h1>",
        "html": True
    }
]

results = await service.send_batch_emails(recipients, max_retries=3)
# Returns: {"sent": 2, "failed": 0, "errors": [], "total": 2}
```

✅ **File Attachments**
```python
attachments = [
    ("proposal.pdf", pdf_file_bytes),
    ("pricing.xlsx", excel_file_bytes)
]

success, msg = await service.send_email(
    to_addr="prospect@school.edu",
    subject="LeadForge EDU Proposal",
    body="<p>Attached is our proposal...</p>",
    attachments=attachments,
    html=True
)
```

✅ **Automatic Retry Logic**
```python
# Automatically retries 3 times on failure
await service.send_email(
    to_addr="lead@company.com",
    subject="Demo Request",
    body="Let's schedule a demo!",
    retry_count=3
)
```

✅ **Simulation Mode** (when SMTP not configured)
```
# .env without SMTP credentials
# → Automatically uses simulation mode
# → Logs all "sent" emails
# → Perfect for development/testing
```

### Error Handling

```python
success, msg = await service.send_email(
    to_addr="lead@company.com",
    subject="Demo",
    body="<p>Test</p>",
    html=True
)

if not success:
    if "Authentication failed" in msg:
        # Fix SMTP credentials
        pass
    elif "SMTP error" in msg:
        # Check SMTP host/port
        pass
    else:
        # Generic error - check logs
        logger.error(f"Email failed: {msg}")
```

### Testing SMTP Configuration

```python
# Quick SMTP test script
import asyncio
from services.enhanced_email_service import EnhancedEmailService

async def test_smtp():
    service = EnhancedEmailService()
    success, msg = await service.send_email(
        to_addr="test@example.com",
        subject="SMTP Test",
        body="<h1>Test Email</h1>",
        html=True
    )
    print(f"Result: {success} - {msg}")

asyncio.run(test_smtp())
```

---

## 🔗 LinkedIn Scraping

### Option 1: Unofficial LinkedIn API (Faster, No Selenium)

**Pros**: Fast, no browser needed, lower CPU
**Cons**: May violate LinkedIn ToS, account risk, less reliable

```python
from services.multi_scraper_service import LinkedInScraper

scraper = LinkedInScraper(
    email="your_linkedin@gmail.com",
    password="your_linkedin_password"
)

# Search for people matching keywords
leads = await scraper.scrape_linkedin_unofficial(
    keywords=["school administrator", "principal", "education director"],
    limit=10
)
```

### Option 2: Selenium-Based Scraping (Safer)

**Pros**: More reliable, mimics human behavior
**Cons**: Slower, requires browser, more resources

```python
from services.multi_scraper_service import LinkedInScraper

scraper = LinkedInScraper(
    email="your_linkedin@gmail.com",
    password="your_linkedin_password"
)

# Browser-based scraping
leads = await scraper.scrape_linkedin_posts(
    keywords=["school management", "edtech", "K-12"],
    limit=10
)
```

### Configuration

```env
LINKEDIN_EMAIL=your_linkedin_email@example.com
LINKEDIN_PASSWORD=your_linkedin_password
LINKEDIN_ACCESS_TOKEN=optional_official_api_token

# Browser settings
SELENIUM_BROWSER=chrome  # Options: chrome, firefox, edge
SELENIUM_HEADLESS=true   # Run browser invisibly
SELENIUM_TIMEOUT=30      # Wait time in seconds
```

---

## 🤖 Apify Integration

### What is Apify?

Apify is a cloud-based web scraping platform with pre-built "Actors" (scrapers) for common tasks:
- Google Search scraper
- LinkedIn scraper
- Website scraper
- Twitter scraper
- And 1000+ more

### Setup

1. **Create Free Account**
   - Visit https://apify.com
   - Sign up (free tier: $5 monthly credit)

2. **Get API Token**
   - Go to https://console.apify.com/account/integrations
   - Copy your API token

3. **Configure .env**
   ```env
   APIFY_API_TOKEN=apify_YOUR_TOKEN_HERE
   APIFY_ACTOR_ID=jbMR8dEWC5OmBWHJh  # Google Search Scraper
   ```

### Common Actor IDs

| Purpose | Actor ID | Cost/1K Results |
|---------|----------|-----------------|
| Google Search | `jbMR8dEWC5OmBWHJh` | ~$0.05 |
| LinkedIn Scraper | `61RPP7dywgAH6w8nL` | ~$0.20 |
| Website Scraper | `quQnARePidAH9w9fJ` | ~$0.01 |
| Twitter Scraper | `nMyy6vB23h8t1rAKZ` | ~$0.10 |

### Usage

```python
from services.multi_scraper_service import ApifyScraper

scraper = ApifyScraper(api_token="your_apify_token")

# Scrape Google Search Results
results = await scraper.scrape_search_results(
    query="school management software reviews",
    limit=50
)

# Scrape LinkedIn Profiles
profiles = await scraper.scrape_linkedin_profiles(
    search_query="school principal education director",
    limit=20
)

# Custom actor
data = await scraper.scrape_with_actor(
    actor_id="quQnARePidAH9w9fJ",
    input_data={
        "startUrls": [{"url": "https://schoolmanagement.com"}],
        "selectors": ["h1", "p", "a"],
        "maxDepth": 2
    }
)
```

### Cost Optimization

```python
# Run during off-peak hours for discounts
# Batch requests to reduce API calls
# Use free actors first before paid ones

# Example: Cost-effective lead research
async def find_leads_cheaply():
    apify = ApifyScraper()
    
    # Step 1: Free Google Search (cheap)
    search_results = await apify.scrape_search_results(
        "edtech reviews forum school",
        limit=20
    )
    
    # Step 2: Extract URLs from results
    urls = [r["url"] for r in search_results]
    
    # Step 3: Scrape those URLs (cheap website scraper)
    for url in urls:
        leads = await apify.scrape_with_actor(
            "quQnARePidAH9w9fJ",  # Website scraper
            input_data={"startUrls": [{"url": url}]}
        )
```

---

## 🌐 Selenium Browser Automation

### Installation

```bash
# Already in requirements.txt:
pip install selenium webdriver-manager

# webdriver-manager automatically downloads Chrome/Firefox drivers
```

### Configuration

```env
SELENIUM_BROWSER=chrome      # chrome, firefox, or edge
SELENIUM_HEADLESS=true       # Run invisibly for servers
SELENIUM_TIMEOUT=30          # Max wait time in seconds
CHROMEDRIVER_PATH=           # Leave empty for auto-download
```

### Generic Website Scraping

```python
from services.multi_scraper_service import GenericWebScraper

scraper = GenericWebScraper()

# Extract structured data from any website
items = await scraper.scrape_website(
    url="https://forum.edtech.com/discussions",
    selector=".discussion-item",  # CSS selector for each item
    extract_fields={
        "title": ".discussion-title",
        "author": ".discussion-author",
        "content": ".discussion-content",
        "date": ".discussion-date"
    }
)

# Returns: [
#   {
#       "title": "Need school management software",
#       "author": "PrincipalJohn",
#       "content": "Looking for...",
#       "date": "2024-01-15"
#   },
#   ...
# ]
```

### Advanced: Form Filling & JavaScript

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
try:
    # Visit page
    driver.get("https://example.com/form")
    
    # Wait for form to load
    wait = WebDriverWait(driver, 10)
    form = wait.until(EC.presence_of_element_located((By.ID, "contact-form")))
    
    # Fill form
    driver.find_element(By.NAME, "name").send_keys("School Principal")
    driver.find_element(By.NAME, "email").send_keys("principal@school.edu")
    driver.find_element(By.NAME, "school").send_keys("ABC High School")
    
    # Submit
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    # Wait for confirmation
    confirmation = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success-message")))
    
finally:
    driver.quit()
```

---

## 📱 PRAW Reddit API

### Setup

1. **Create Reddit App**
   - Go to https://www.reddit.com/prefs/apps
   - Click "Create another app..."
   - Select "script"
   - Fill in the form

2. **Get Credentials**
   - Copy: Client ID, Client Secret
   - Create a User-Agent: `LeadForgeEDU/1.0`

3. **Configure .env**
   ```env
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USER_AGENT=LeadForgeEDU/1.0
   ENABLE_REDDIT_SCRAPER=true
   ```

### Usage

```python
from services.scraper_service import ScraperService

# Already integrated in existing backend
scraper = ScraperService(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

leads = await scraper.scrape_reddit(
    keywords=[
        "looking for school management software",
        "need better grading system",
        "EdTech recommendations"
    ],
    limit=10
)
```

---

## 🚀 Multi-Source Scraping

### Unified Interface

```python
from services.multi_scraper_service import MultiSourceScraperService
from sqlalchemy.ext.asyncio import AsyncSession

service = MultiSourceScraperService()

# Scrape all sources concurrently
results = await service.scrape_all_sources(
    keywords=[
        "school management system",
        "automated grading software",
        "student attendance app"
    ],
    limit=15,
    db=async_db_session  # Save to database automatically
)

# Results structure:
# {
#     "linkedin": [...],  # From LinkedIn scraper
#     "apify": [...],     # From Apify platform
#     "web": [...]        # From Selenium scraper
# }
```

### Feature Flags

Control which scrapers are active:

```env
ENABLE_REDDIT_SCRAPER=true
ENABLE_LINKEDIN_SCRAPER=true
ENABLE_APIFY_SCRAPER=true
ENABLE_SELENIUM_SCRAPER=true
ENABLE_SMART_ENRICHMENT=true  # Auto-enrich leads with additional data
```

---

## 🎨 Frontend Integration

### WebSocket Connection for Live Scraping

The frontend already has `useWebSocket.js` hook. Update it to handle multi-source events:

```javascript
// src/hooks/useWebSocket.js
const { data: leads, loading, error } = useWebSocket({
    endpoints: {
        scrape: "ws://localhost:8000/ws/scrape",
        linkedin: "ws://localhost:8000/ws/scrape/linkedin",
        apify: "ws://localhost:8000/ws/scrape/apify"
    },
    onMessage: (event) => {
        if (event.source === "linkedin") {
            // Handle LinkedIn leads
        } else if (event.source === "apify") {
            // Handle Apify results
        }
    }
});
```

### Email Integration in Frontend

```javascript
// src/services/api.js
export async function sendOutreachEmail(leadId, emailData) {
    const response = await fetch(`/outreach/send-email/${leadId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            subject: emailData.subject,
            body: emailData.body,
            html: true,
            cc: emailData.cc || [],
            retry_count: emailData.retryCount || 3
        })
    });
    return response.json();
}

// Usage in OutreachModal.jsx
async function handleSendEmail() {
    const result = await sendOutreachEmail(lead.id, {
        subject: "LeadForge EDU Demo",
        body: generateHTMLTemplate(lead),
        cc: ["supervisor@company.com"],
        retryCount: 3
    });
    
    if (result.success) {
        toast.success(`Email sent to ${lead.email}`);
    } else {
        toast.error(`Failed: ${result.message}`);
    }
}
```

### Scraping Progress UI

```javascript
// src/components/ScrapeProgress.jsx
import useWebSocket from '../hooks/useWebSocket';

export function ScrapeProgress({ sources = ['linkedin', 'apify', 'web'] }) {
    const { data: events } = useWebSocket("ws://localhost:8000/ws/scrape");
    
    return (
        <div className="scrape-progress">
            {sources.map(source => (
                <SourceStatus
                    key={source}
                    source={source}
                    status={events?.[source]?.status}
                    progress={events?.[source]?.progress}
                    leadsFound={events?.[source]?.leads_found}
                />
            ))}
        </div>
    );
}
```

---

## 📊 Dashboard Metrics

### Email Campaign Tracking

```python
# backend/routers/outreach.py - Add new endpoint

@router.get("/campaigns")
async def get_email_campaigns(db: AsyncSession):
    """Get email campaign performance metrics."""
    campaigns = await db.execute(
        select(OutreachLog).order_by(OutreachLog.sent_at.desc())
    )
    
    return {
        "total_sent": len(campaigns.scalars().all()),
        "open_rate": calculate_open_rate(campaigns),
        "click_rate": calculate_click_rate(campaigns),
        "reply_rate": calculate_reply_rate(campaigns),
        "by_source": group_by_source(campaigns),
        "by_recipient": group_by_recipient(campaigns),
    }
```

---

## ⚠️ Best Practices

### Scraping Ethics
- ✅ Respect robots.txt files
- ✅ Add delays between requests (rate limiting)
- ✅ Use official APIs when available
- ✅ Don't overload servers
- ❌ Don't scrape protected data
- ❌ Don't violate Terms of Service

### SMTP Security
- ✅ Use App Passwords for Gmail (not main password)
- ✅ Enable 2FA on email accounts
- ✅ Store credentials in .env (never in code)
- ✅ Use TLS/SSL for connections
- ✅ Monitor failed login attempts
- ❌ Don't share credentials
- ❌ Don't log passwords

### Email Deliverability
- ✅ Warm up IP address with low volume first
- ✅ Use authenticated domain (SPF, DKIM, DMARC)
- ✅ Avoid spam trigger words
- ✅ Include unsubscribe link
- ✅ Monitor bounce rates
- ❌ Don't send to invalid emails
- ❌ Don't spam

---

## 🔧 Troubleshooting

### SMTP Not Working

**Problem**: "Authentication failed"
```
Solution: Check SMTP credentials and enable 2FA if using Gmail
```

**Problem**: "Connection timeout"
```
Solution: Check SMTP_HOST and SMTP_PORT values
Verify firewall allows outbound 465/587
```

**Problem**: "Emails going to spam"
```
Solution: 
1. Set up SPF/DKIM/DMARC for your domain
2. Use authenticated sender
3. Reduce email frequency
4. Include unsubscribe link
```

### LinkedIn Scraping Issues

**Problem**: "Account temporarily locked"
```
Solution: LinkedIn blocks aggressive scraping
→ Use Apify or unofficial API instead
→ Add delays between requests
→ Don't scrape too many profiles/posts
```

**Problem**: "Selenium driver fails"
```
Solution: 
1. Reinstall webdriver-manager: pip install --upgrade webdriver-manager
2. Clear cache: rm -rf ~/.wdm/
3. Update Selenium: pip install --upgrade selenium
```

### Apify Rate Limiting

**Problem**: "Request limit exceeded"
```
Solution:
1. Check Apify dashboard for rate limits
2. Use cheaper actors (Google Search vs LinkedIn)
3. Schedule scrapes during off-peak hours
4. Request higher limits from Apify
```

---

## 📈 Performance Optimization

### Concurrent Scraping

```python
# Scrape all sources at once (3-5x faster)
import asyncio

async def fast_scrape():
    tasks = [
        scrape_reddit(),
        scrape_linkedin(),
        scrape_apify(),
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### Database Bulk Insert

```python
# Insert many leads at once (faster than one-by-one)
from sqlalchemy import insert

async def bulk_save_leads(leads: List[dict], db: AsyncSession):
    stmt = insert(Lead).values(leads)
    await db.execute(stmt)
    await db.commit()
```

### Caching

```python
# Cache scraping results to avoid re-scraping
from datetime import timedelta
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_cached_leads(source: str, max_age: timedelta = timedelta(hours=6)):
    # Cache for 6 hours
    pass
```

---

## 📞 Support & Resources

- **Apify Docs**: https://docs.apify.com
- **Selenium Docs**: https://www.selenium.dev/documentation/
- **PRAW Docs**: https://praw.readthedocs.io
- **FastAPI WebSocket**: https://fastapi.tiangolo.com/advanced/websockets/
- **Gmail App Passwords**: https://myaccount.google.com/apppasswords

---

## 🎯 Next Steps

1. **Implement SMTP** → Test with Gmail first
2. **Add LinkedIn Scraping** → Start with unofficial API
3. **Set up Apify** → Use free tier for testing
4. **Deploy Scrapers** → Use task queue (Celery/RQ)
5. **Monitor & Optimize** → Track open rates, click rates, etc.

---

**Happy Scraping! 🎉**
