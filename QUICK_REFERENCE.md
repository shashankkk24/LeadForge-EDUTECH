# ⚡ LeadForge EDU - Quick Reference Card

## 🔑 Your Credentials

```
Gemini API Key:     AIzaSyAtvoCvIvEwbKJFqNmiMbegs2sPPHtLrUk
PostgreSQL DB:      ep-lively-frost-ae2m0s7o-pooler.c-2.us-east-2.aws.neon.tech
DB User:            neondb_owner
DB Password:        npg_hVuBbD1yM7cL
```

## 📧 SMTP Setup (Choose One)

### **Gmail (Recommended)**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
```
👉 Get App Password: https://myaccount.google.com/apppasswords

### **Office365**
```env
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=your_email@company.com
SMTP_PASSWORD=your_password
```

## 🔗 LinkedIn Setup

### Option A: Unofficial API (Faster)
```env
LINKEDIN_EMAIL=your_linkedin_email@gmail.com
LINKEDIN_PASSWORD=your_linkedin_password
```

### Option B: Selenium Scraper (Safer)
```env
LINKEDIN_EMAIL=your_linkedin_email@gmail.com
LINKEDIN_PASSWORD=your_linkedin_password
SELENIUM_BROWSER=chrome
SELENIUM_HEADLESS=true
```

## 🤖 Apify Setup

```env
# 1. Sign up: https://apify.com (free $5/month)
# 2. Get token: https://console.apify.com/account/integrations
APIFY_API_TOKEN=your_token_here

# 3. Choose an Actor (pre-built scraper):
APIFY_ACTOR_ID=jbMR8dEWC5OmBWHJh  # Google Search (cheapest)
# or
APIFY_ACTOR_ID=61RPP7dywgAH6w8nL   # LinkedIn
# or
APIFY_ACTOR_ID=quQnARePidAH9w9fJ   # Website Scraper
```

## 📱 Reddit Setup

```env
# 1. Go to: https://www.reddit.com/prefs/apps
# 2. Create new 'script' app
REDDIT_CLIENT_ID=your_id_here
REDDIT_CLIENT_SECRET=your_secret_here
REDDIT_USER_AGENT=LeadForgeEDU/1.0
```

## 🚀 Quick Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run backend
python main.py

# Run tests
pytest tests/

# Send test email
python -c "from services.enhanced_email_service import EnhancedEmailService; ..."

# Scrape Reddit
python -c "from services.scraper_service import ScraperService; ..."
```

## 🎯 API Endpoints

```
# Email
POST   /outreach/send-email/{lead_id}
GET    /outreach/campaigns
GET    /outreach/logs/{id}

# Scraping
POST   /scrape
GET    /scrape/jobs/{id}

# Leads
GET    /leads
GET    /leads/{id}
PATCH  /leads/{id}
DELETE /leads/{id}

# Intelligence
GET    /intelligence/{id}
POST   /generate-message/{id}
```

## 🧪 Test Code

### Test Email
```python
from services.enhanced_email_service import EnhancedEmailService
import asyncio

async def test():
    service = EnhancedEmailService()
    success, msg = await service.send_email(
        to_addr="test@example.com",
        subject="Test",
        body="<h1>Test</h1>",
        html=True
    )
    print(f"Result: {success} - {msg}")

asyncio.run(test())
```

### Test Scraper
```python
from services.multi_scraper_service import ApifyScraper
import asyncio

async def test():
    scraper = ApifyScraper(api_token="your_token")
    results = await scraper.scrape_search_results(
        query="school management software",
        limit=10
    )
    print(f"Found {len(results)} results")

asyncio.run(test())
```

### Test LinkedIn
```python
from services.multi_scraper_service import LinkedInScraper
import asyncio

async def test():
    scraper = LinkedInScraper(
        email="your_email@gmail.com",
        password="your_password"
    )
    leads = await scraper.scrape_linkedin_unofficial(
        keywords=["school principal"],
        limit=5
    )
    print(f"Found {len(leads)} contacts")

asyncio.run(test())
```

## 🔧 Feature Flags

```env
ENABLE_REDDIT_SCRAPER=true
ENABLE_LINKEDIN_SCRAPER=true
ENABLE_APIFY_SCRAPER=false      # Requires paid token
ENABLE_SELENIUM_SCRAPER=false   # Resource intensive
ENABLE_SMART_ENRICHMENT=true
```

## 📊 Services Overview

| Service | File | Purpose | Config |
|---------|------|---------|--------|
| Email | `enhanced_email_service.py` | Send emails | SMTP_* |
| LinkedIn | `multi_scraper_service.py` | LinkedIn scraping | LINKEDIN_* |
| Apify | `multi_scraper_service.py` | Web scraping | APIFY_* |
| Selenium | `multi_scraper_service.py` | Browser automation | SELENIUM_* |
| Reddit | `scraper_service.py` | Reddit scraping | REDDIT_* |
| Gemini | `gemini_service.py` | AI messages | GEMINI_API_KEY |

## 🔒 Security

- ✅ Use App Passwords for Gmail (not main password)
- ✅ Enable 2FA on email account
- ✅ Store credentials in .env (never commit)
- ✅ Use HTTPS in production
- ✅ Implement rate limiting
- ✅ Monitor for suspicious activity

## 📖 Documentation

- **Full Setup**: `INTEGRATION_GUIDE.md` (200+ lines)
- **Summary**: `INTEGRATION_SUMMARY.md`
- **Setup Script**: `SETUP.sh`

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "SMTP Authentication failed" | Check email/password, enable 2FA, get App Password |
| "Connection timeout" | Check SMTP_HOST and SMTP_PORT |
| "LinkedIn scraper fails" | Try unofficial API instead of Selenium |
| "Apify limit exceeded" | Upgrade plan or use cheaper actors |
| "WebDriver error" | Update: `pip install --upgrade webdriver-manager selenium` |

## 🎯 Usage Examples

### Send Email with Template
```python
html = EnhancedEmailService.create_html_template(
    name="John Principal",
    company="ABC School",
    pain_point="manual grading taking 10 hours",
    solution="automated grading with AI",
    cta="Schedule 30-min demo"
)
await service.send_email(
    to_addr="john@school.edu",
    subject="Stop Spending 10 Hours on Grading",
    body=html,
    html=True,
    retry_count=3
)
```

### Scrape Multiple Sources
```python
from services.multi_scraper_service import MultiSourceScraperService

service = MultiSourceScraperService()
results = await service.scrape_all_sources(
    keywords=["school management", "EdTech"],
    limit=20,
    db=db_session
)
# Returns: {"linkedin": [...], "apify": [...], "web": [...]}
```

### Batch Email
```python
recipients = [
    {"to": "principal1@school.edu", "subject": "...", "body": "..."},
    {"to": "admin@school.edu", "subject": "...", "body": "..."}
]
results = await service.send_batch_emails(recipients, max_retries=3)
# Returns: {"sent": 2, "failed": 0, "errors": []}
```

## 💡 Tips

1. **Start with free tiers**: Reddit & Apify have free options
2. **Use simulation mode for testing**: Remove SMTP creds to use simulation
3. **Cache results**: Don't re-scrape frequently
4. **Batch operations**: Send emails in batches, not one-by-one
5. **Monitor costs**: Apify charges ~$0.05-0.20 per 1K results
6. **Test locally first**: Use .env without real credentials

---

**Last Updated**: 2024-04-24
**Version**: 1.0
**Status**: Production Ready ✅
