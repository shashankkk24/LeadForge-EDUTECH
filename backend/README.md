# LeadForge EDU Backend

Production-grade FastAPI backend for AI-powered EdTech lead generation and sales automation.

## Features

✅ **Lead Extraction** - Scrape Reddit and mock sources for EdTech leads  
✅ **NLP Analysis** - Extract pain points, detect roles, classify intent  
✅ **AI Scoring** - Heat Score™ algorithm (0-100) with 5-signal weighting  
✅ **Gemini Integration** - Personalized message generation with fallback mocks  
✅ **SMTP Email** - Real Gmail SMTP with simulation mode fallback  
✅ **WebSocket** - Real-time lead updates via WebSocket  
✅ **Full Test Coverage** - 30+ tests using pytest with TDD approach  

## Project Structure

```
backend/
├── main.py                    # FastAPI app entry point
├── config.py                  # Configuration management
├── database.py                # SQLAlchemy async setup
├── models.py                  # ORM models (Lead, OutreachLog, ScrapeJob)
├── schemas.py                 # Pydantic request/response schemas
├── routers/
│   ├── leads.py              # Lead CRUD endpoints
│   ├── scraper.py            # Scraping job endpoints
│   └── outreach.py           # Message gen + email endpoints
├── services/
│   ├── scraper_service.py    # Reddit scraping + mock data
│   ├── nlp_service.py        # spaCy NLP + sentiment
│   ├── scoring_service.py    # Heat Score algorithm
│   ├── gemini_service.py     # Gemini API calls + mocks
│   └── email_service.py      # SMTP + simulation
├── websocket/
│   └── manager.py            # WebSocket connection management
├── utils/
│   └── helpers.py            # Utility functions
├── tests/
│   ├── test_leads.py         # Lead CRUD tests
│   ├── test_scraper.py       # Scraper tests
│   └── test_outreach.py      # Outreach + email tests
├── scripts/
│   └── seed_leads.py         # Demo data seeding
├── requirements.txt          # Python dependencies
└── .env.example             # Example environment file
```

## Quick Start

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 13+ (or use NeonDB free tier)
- Gmail account (for SMTP)

### 2. Setup Environment

```bash
# Clone repository
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model (optional, but recommended)
python -m spacy download en_core_web_sm
```

### 3. Configure Environment

Create `.env` file:

```env
# Database (NeonDB provided)
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_hVuBbD1yM7cL@ep-lively-frost-ae2m0s7o-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require

# Gemini API (optional - will use mocks if missing)
GEMINI_API_KEY=your_gemini_api_key

# Gmail SMTP (optional - will use simulation mode if missing)
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # Gmail App Password, not account password

# Reddit API (optional - will use mocks if missing)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret

# Other
DEBUG=true
```

### 4. Initialize Database

```bash
# Database tables are auto-created on startup
# Or seed with sample data:
python scripts/seed_leads.py
```

### 5. Run Server

```bash
# Development server with hot reload
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Server will be available at: http://localhost:8000

Interactive API docs: http://localhost:8000/docs

## API Endpoints

### Health & Info

```
GET  /health              # Health check
GET  /                    # API info
```

### Leads

```
GET    /api/leads                    # List leads (with filters)
GET    /api/leads/hot               # Get HOT priority leads
GET    /api/leads/stats             # Dashboard statistics
GET    /api/leads/{lead_id}         # Get lead details
PATCH  /api/leads/{lead_id}         # Update lead
DELETE /api/leads/{lead_id}         # Delete lead
```

**List Query Parameters:**
- `status`: Filter by status (New, Drafted, Contacted, Closed)
- `priority`: Filter by priority (HOT, WARM, COLD)
- `skip`: Pagination offset (default: 0)
- `limit`: Page size (default: 20, max: 100)

**Example:**
```bash
curl "http://localhost:8000/api/leads?priority=HOT&limit=10"
```

### Scraper

```
POST   /api/scrape              # Trigger scraping job
GET    /api/scrape/jobs/{job_id}  # Get scrape job status
```

**Request Body:**
```json
{
  "platform": "reddit",
  "keywords": ["school management software", "grading system"]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "reddit",
    "keywords": ["school management software"]
  }'
```

### Outreach

```
POST   /api/outreach/generate-message/{lead_id}    # Generate AI message
POST   /api/outreach/send-email/{lead_id}          # Send email
GET    /api/outreach/intelligence/{lead_id}        # Get sales intelligence
GET    /api/outreach/logs/{lead_id}                # Get outreach logs
```

**Generate Message Example:**
```bash
curl -X POST http://localhost:8000/api/outreach/generate-message/lead-uuid
```

**Send Email Example:**
```bash
curl -X POST http://localhost:8000/api/outreach/send-email/lead-uuid \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "principal@school.edu"
  }'
```

### WebSocket

```
WS     /ws/leads          # Real-time lead updates
```

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/leads');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'new_lead') {
    console.log('New lead:', message.data);
  } else if (message.type === 'job_status') {
    console.log('Job status:', message);
  }
};
```

## Testing

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_leads.py -v

# Run specific test
pytest tests/test_leads.py::test_should_create_lead_in_database -v
```

### Test Structure

All tests follow **TDD (Test-Driven Development)** principles:
- **AAA Pattern**: Arrange, Act, Assert
- **Naming**: `should_[action]_when_[condition]`
- **Coverage**: 30+ tests across CRUD, scoring, scraping, email, AI

**Example Test:**
```python
def test_should_score_hot_lead_with_high_urgency_and_negative_sentiment():
    # Arrange
    lead = Lead(
        urgency_level="high",
        sentiment_score=-0.9,
        detected_role="principal"
    )
    
    # Act
    score, priority = ScoringService.calculate_lead_score(lead)
    
    # Assert
    assert priority == "HOT"
    assert score >= 70
```

## Configuration

### Database Connection

Uses **SQLAlchemy with async/await** support:
- Default: NeonDB (provided)
- Local: `postgresql://user:password@localhost:5432/leadforge`
- Testing: SQLite in-memory

### API Authentication

Currently **no authentication** (demo mode). For production:
1. Add FastAPI Security
2. Implement JWT tokens
3. Add API key validation

### Logging

Structured logging to console:
- Level: INFO (configurable)
- Format: `timestamp - module - level - message`

View logs for debugging:
```bash
# Start with debug logging
DEBUG=true python -m uvicorn main:app --reload
```

## Demo Workflow

1. **Start Server**
   ```bash
   python -m uvicorn main:app --reload
   ```

2. **Seed Sample Data**
   ```bash
   python scripts/seed_leads.py
   ```

3. **Trigger Scrape** (creates leads in real-time)
   ```bash
   curl -X POST http://localhost:8000/api/scrape \
     -H "Content-Type: application/json" \
     -d '{"platform": "reddit", "keywords": ["school management"]}'
   ```

4. **Get HOT Leads** (prioritized by Heat Score)
   ```bash
   curl http://localhost:8000/api/leads/hot
   ```

5. **Generate Message** (personalized by Gemini)
   ```bash
   curl -X POST http://localhost:8000/api/outreach/generate-message/{lead_id}
   ```

6. **Send Email** (real SMTP or simulated)
   ```bash
   curl -X POST http://localhost:8000/api/outreach/send-email/{lead_id} \
     -H "Content-Type: application/json" \
     -d '{"recipient_email": "principal@school.edu"}'
   ```

7. **Watch WebSocket** (real-time updates)
   ```javascript
   // In browser console
   const ws = new WebSocket('ws://localhost:8000/ws/leads');
   ws.onmessage = (e) => console.log(JSON.parse(e.data));
   ```

## Key Features Explained

### Heat Score™ Algorithm

Calculates lead priority (0-100) using 5 signals:

```
Score = (
  Urgency (30 weight) +
  Sentiment (25 weight) +  
  Role (20 weight) +
  Recency (15 weight) +
  Specificity (10 weight)
) / 100

Buckets:
  HOT (70+)   → Immediate outreach
  WARM (40-69) → Nurture sequence
  COLD (<40)  → Long-term nurture
```

### NLP Pipeline

1. **Pain Point Extraction** - Regex patterns + Gemini
2. **Role Detection** - Principal > Admin > Teacher
3. **Urgency Classification** - ASAP, soon, eventual
4. **Sentiment Analysis** - -1.0 to 1.0 scale
5. **Intent Classification** - 5 buying stage labels

### AI Features

**Feature 1**: EduIntent Classifier™ - Multi-label intent classification  
**Feature 2**: Pain-Point Fingerprinting - Structured tag extraction  
**Feature 3**: Lead Heat Score™ - 5-signal dynamic scoring  
**Feature 4**: Contextual Outreach - Non-template AI messages  
**Feature 5**: Real SMTP Dispatch - Gmail SMTP with fallback  
**Feature 6**: WebSocket Live Feed - Real-time lead updates  
**Feature 7**: Sales Intelligence Card - Talk tracks + objection handling  

## Troubleshooting

### Database Connection Failed

```
# Check connection string
echo $DATABASE_URL

# Test connection
psql postgresql://user:password@host/db

# Use NeonDB console instead
```

### Gemini API Errors

- Missing API key? Service will auto-fallback to mocks
- Rate limited? Check `google-generativeai` documentation
- JSON parsing errors? Check response format in logs

### Email Not Sending

- SMTP config missing? Uses simulation mode automatically
- Gmail blocked? Enable "Less secure app access" or use App Password
- Logs show: `[SIMULATED]`? Check `.env` SMTP_USER and SMTP_PASSWORD

### Tests Failing

```bash
# Run with verbose output
pytest -vv

# Run specific test
pytest tests/test_leads.py::test_name -vv

# Check test database
# Uses in-memory SQLite - no cleanup needed
```

## Production Deployment

### Environment Variables

```env
DEBUG=false
DATABASE_URL=postgresql+asyncpg://prod_user:password@prod-host/prod_db
GEMINI_API_KEY=your_production_key
SMTP_USER=noreply@company.com
SMTP_PASSWORD=your_smtp_password
```

### Start Server

```bash
# Using Uvicorn with production settings
python -m uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info

# Or with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]
```

## API Response Examples

### List Leads
```json
{
  "total": 42,
  "page": 1,
  "page_size": 20,
  "leads": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "platform": "reddit",
      "username": "principal_johnson",
      "post_url": "https://reddit.com/r/education/...",
      "pain_point_tags": ["manual_attendance_tracking"],
      "detected_role": "principal",
      "urgency_level": "high",
      "lead_score": 85,
      "priority": "HOT",
      "status": "New",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Generate Message
```json
{
  "subject": "Automate Attendance Tracking - 3 Hour Daily Savings",
  "body": "Hi Principal Johnson,\n\nI noticed your school is struggling with manual attendance tracking consuming 3 hours daily. We've helped 500+ schools reduce this to 5 minutes...",
  "confidence": 0.95
}
```

### Scrape Job Status
```json
{
  "id": "job-123",
  "platform": "reddit",
  "keywords": ["school management software"],
  "status": "completed",
  "leads_found": 15,
  "started_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T10:05:30Z"
}
```

## License

Hackathon Project - MIT License

## Support

For issues or questions:
1. Check logs: `tail -f logs/app.log`
2. Review API docs: http://localhost:8000/docs
3. Check tests for usage examples
4. Review configuration in `config.py`
