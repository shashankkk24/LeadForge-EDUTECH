# LeadForge EDU
### *Scrape. Score. Strike. Convert school leads on autopilot.*

An AI-powered EdTech lead generation and outreach platform built for sales teams hunting K-12 and Higher Ed clients. LeadForge EDU automates the entire pipeline — from discovering frustrated school administrators on Reddit, to scoring their buying intent, to sending a hyper-personalized email — all in under 3 minutes.

---

## The Problem

EdTech sales teams waste 4+ hours a day manually scrolling Reddit threads, forums, and social posts looking for school administrators who are actively frustrated with their current tools. By the time a lead is found, a cold email written, and sent — the window has closed. The signal was there. The speed wasn't.

The deeper problem isn't just discovery — it's **prioritization and personalization at scale**. A generic cold email to a principal who just vented about manual attendance tracking gets ignored. Every time.

---

## The Solution

LeadForge EDU is a full-stack CRM that runs the complete **Scrape → Score → Strike** pipeline automatically:

1. Scrapes high-intent posts from Reddit using 15 EdTech-specific keyword searches
2. Runs each post through an NLP + Gemini AI pipeline to extract pain points and classify buying intent
3. Scores every lead 0–100 using the proprietary **Heat Score™** algorithm
4. Surfaces HOT leads in real-time on a Kanban dashboard via WebSocket
5. Generates a fully personalized outreach email referencing the lead's exact post content
6. Dispatches the email via real Gmail SMTP — not simulated

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) — async/await throughout |
| Database | PostgreSQL via NeonDB + SQLAlchemy async ORM |
| AI / NLP | Google Gemini 1.5 Flash + spaCy NER |
| Scraping | PRAW (Reddit API) + Apify + Selenium |
| Email | smtplib Gmail SMTP + simulation fallback |
| Realtime | FastAPI native WebSocket |
| Frontend | React 19 + TailwindCSS + Vite |
| Validation | Pydantic v2 |
| Testing | pytest + pytest-asyncio (31 tests) |

---

## Architecture

```
Reddit / Forums / LinkedIn
         ↓
  Lead Extraction Engine
  (PRAW + Apify + Selenium)
         ↓
    NLP Pipeline
  (spaCy NER + Gemini Intent Analysis)
         ↓
  Lead Scoring Engine
  (Heat Score™ — 5-signal algorithm)
         ↓
  PostgreSQL Database (NeonDB)
         ↓
  FastAPI Backend (REST + WebSocket)
         ↓
  React CRM Dashboard
  (Kanban + Table + Analytics)
         ↓
  AI Outreach Generator (Gemini)
         ↓
  SMTP Email Dispatch (Gmail)
         ↓
  Status Update → DB → Dashboard refresh
```

---

## Full Workflow

### Step 1 — Lead Discovery
The scraper hits Reddit using 15 high-intent keyword searches:
- `"looking for school management software"`
- `"tired of manual grading"`
- `"need better attendance system"`
- `"school ERP recommendation"` *(and 11 more)*

Each matching post is saved as a raw lead in PostgreSQL with the platform, username, post URL, and full content.

### Step 2 — NLP Enrichment
Every lead runs through two layers of analysis:

**spaCy (local NER):**
- Extracts named entities — school names, locations, organizations
- Detects role from text: `principal > admin > teacher > staff`
- Classifies urgency: `high / medium / low` based on trigger words like *"ASAP"*, *"desperately"*, *"before semester"*
- Calculates sentiment score from `-1.0` (frustrated) to `+1.0` (positive)

**Gemini 1.5 Flash (LLM):**
- Classifies buying stage into one of 5 intent labels:
  - `ACTIVELY_SEEKING` — "We need school management software ASAP"
  - `FRUSTRATED_CURRENT_USER` — "Our current LMS is terrible, switching soon"
  - `RESEARCH_PHASE` — "What software do other schools use?"
  - `BUDGET_APPROVED` — "We have budget allocated for next semester"
  - `PEER_RECOMMENDATION_ASK` — "Any recommendations for grading tools?"
- Extracts top 3 pain points as structured `snake_case` tags:
  - e.g. `["manual_attendance_tracking", "parent_communication_gap", "exam_result_delays"]`

### Step 3 — Heat Score™ Calculation
Every lead is scored 0–100 using 5 weighted signals:

```
Score = (
  urgency_signal    × 30  +   ← "ASAP", "urgent", "immediately" → max points
  sentiment_signal  × 25  +   ← more negative = more frustrated = hotter lead
  role_signal       × 20  +   ← principal(20) > admin(15) > teacher(8) > staff(5)
  recency_signal    × 15  +   ← linear decay over 72 hours; stale posts score 0
  specificity_signal × 10     ← mentions of budget, demo, pricing, timeline
) ÷ 100 × 100
```

Auto-bucketed into:
- 🔴 **HOT** — score ≥ 70
- 🟠 **WARM** — score 40–69
- 🔵 **COLD** — score < 40

### Step 4 — Real-Time Dashboard
New leads are broadcast to the frontend via WebSocket (`/ws/leads`) the moment they're saved to the database. The React dashboard appends lead cards to the Kanban board live — no page refresh needed.

The Kanban has 4 columns: **New → Drafted → Contacted → Closed**, with leads sorted HOT first within each column.

### Step 5 — AI Outreach Generation
One click on any lead opens the **AI Outreach Engine** modal. Gemini generates a unique email that:
- References the lead's **exact post content** in line 1
- Mentions their **specific pain point tags** by name
- Adapts tone to their **role and urgency level**
- Stays under 120 words
- Ends with a soft CTA (15-min call)
- Never uses generic openers like *"I hope this email finds you well"*

The rep can edit the subject and body inline before sending.

### Step 6 — Email Dispatch
Clicking **Send Email** dispatches via real Gmail SMTP. Every send is logged in the `outreach_logs` table with timestamp, recipient, and status. The lead's Kanban status automatically moves to **Contacted**.

If no SMTP credentials are configured, the system falls back to simulation mode — the email is logged as `simulated` and the full workflow still completes.

### Step 7 — Lead Intelligence Card
Clicking any lead card opens the **Lead Intelligence** panel — a Gemini-generated sales coach card showing:
- One-line opening talk track tailored to their pain
- Key product features to highlight for this specific lead
- Top objections they might raise + suggested responses
- Recommended follow-up timing

---

## Project Structure

```
Hackathon/
├── backend/
│   ├── main.py                    # FastAPI app entry, WebSocket, CORS
│   ├── config.py                  # Settings + env management
│   ├── database.py                # Async SQLAlchemy + NeonDB connection
│   ├── models.py                  # ORM models: Lead, OutreachLog, ScrapeJob
│   ├── schemas.py                 # 12 Pydantic request/response schemas
│   ├── routers/
│   │   ├── leads.py               # 6 endpoints (list, hot, stats, get, patch, delete)
│   │   ├── scraper.py             # 2 endpoints + background task processing
│   │   └── outreach.py            # 4 endpoints (generate, send, intel, logs)
│   ├── services/
│   │   ├── scraper_service.py     # PRAW Reddit + mock fallback
│   │   ├── nlp_service.py         # spaCy NER + pain points + sentiment
│   │   ├── scoring_service.py     # Heat Score™ algorithm
│   │   ├── gemini_service.py      # All Gemini API calls + mock responses
│   │   ├── email_service.py       # Gmail SMTP + simulation fallback
│   │   ├── enhanced_email_service.py  # Async SMTP + batch + attachments
│   │   ├── multi_scraper_service.py   # LinkedIn + Apify + Selenium scrapers
│   │   └── linkedin_scraper_service.py
│   ├── socket_manager/
│   │   └── manager.py             # WebSocket connection management
│   ├── utils/
│   │   └── helpers.py             # Weight functions, recency decay, formatting
│   ├── scripts/
│   │   └── seed_leads.py          # 20 realistic mock leads for demo
│   ├── tests/
│   │   ├── test_leads.py          # 15 tests — CRUD, scoring, pain points
│   │   ├── test_scraper.py        # 8 tests — mock scrape, DB save, jobs
│   │   └── test_outreach.py       # 8 tests — email, logs, Gemini mocks
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── App.jsx                # Root — state, routing, WebSocket handling
    │   ├── components/
    │   │   ├── KanbanBoard.jsx    # 4-column Kanban, HOT-first sort
    │   │   ├── LeadCard.jsx       # Lead card with score badge + priority color
    │   │   ├── OutreachModal.jsx  # AI generate + edit + send email
    │   │   ├── IntelCard.jsx      # Lead Intelligence overlay panel
    │   │   ├── Sidebar.jsx        # Nav + pipeline list + WebSocket status
    │   │   ├── TopNavBar.jsx      # Scrape Now button + live indicator
    │   │   └── Views.jsx          # Scraper, Intelligence, Outreach, Analytics views
    │   ├── hooks/
    │   │   └── useWebSocket.js    # WS connect + auto-reconnect + message queue
    │   └── services/
    │       └── api.js             # Axios API client for all backend calls
    ├── package.json
    └── vite.config.js
```

---

## Database Schema

**leads** — core table
| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| platform | VARCHAR | reddit / twitter / forum |
| username | VARCHAR | Post author |
| post_url | TEXT | Source URL |
| post_content | TEXT | Full post text |
| pain_point | TEXT | NLP summary |
| pain_point_tags | TEXT | JSON-encoded tag array |
| detected_role | VARCHAR | principal / admin / teacher |
| urgency_level | VARCHAR | high / medium / low |
| sentiment_score | FLOAT | -1.0 to 1.0 |
| intent_label | VARCHAR | ACTIVELY_SEEKING / FRUSTRATED / etc. |
| lead_score | INTEGER | 0–100 Heat Score™ |
| priority | VARCHAR | HOT / WARM / COLD |
| status | VARCHAR | New / Drafted / Contacted / Closed |
| ai_subject | TEXT | Generated email subject |
| ai_message | TEXT | Generated email body |

**outreach_logs** — every email sent or simulated

**scrape_jobs** — job tracking with status, lead count, timestamps

---

## API Endpoints

### Leads
| Method | Endpoint | Description |
|---|---|---|
| GET | `/leads` | List all leads (filter by status, priority) |
| GET | `/leads/hot` | HOT priority leads only |
| GET | `/leads/stats` | Dashboard statistics |
| GET | `/leads/{id}` | Single lead detail |
| PATCH | `/leads/{id}` | Update status / notes |
| DELETE | `/leads/{id}` | Delete lead |

### Scraper
| Method | Endpoint | Description |
|---|---|---|
| POST | `/scrape` | Trigger scrape job (background task) |
| GET | `/scrape/jobs/{id}` | Check job status |

### Outreach
| Method | Endpoint | Description |
|---|---|---|
| POST | `/outreach/generate-message/{id}` | Generate AI email |
| POST | `/outreach/send-email/{id}` | Dispatch via SMTP |
| GET | `/outreach/intelligence/{id}` | Sales intelligence card |
| GET | `/outreach/logs/{id}` | Outreach history |

---

## Setup & Running

### Prerequisites
- Python 3.10+
- Node.js 18+
- A NeonDB (or any PostgreSQL) connection string
- Google Gemini API key (free tier: 15 req/min, 1M tokens/day)

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and GEMINI_API_KEY

# Seed demo data (optional)
python scripts/seed_leads.py

# Start server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at: `http://localhost:8000`
Swagger docs at: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend

# Install dependencies (already done if node_modules exists)
npm install

# Start dev server
npm run dev
```

Frontend runs at: `http://localhost:5173`

### Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname

# AI
GEMINI_API_KEY=your_gemini_key_here

# Reddit scraping (optional — uses mock data if blank)
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=LeadForgeEDU/1.0

# Email (optional — uses simulation mode if blank)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password

# Apify (optional — for LinkedIn/web scraping)
APIFY_API_TOKEN=your_apify_token
```

> All external services are optional. The system uses mock/simulation fallbacks for every one of them — the full demo works with just a database URL.

---

## 7 Standout Features

### 1. EduIntent Classifier™
5-stage buying intent classification via Gemini — not just keyword matching. Sales reps see `BUDGET_APPROVED` and skip straight to close.

### 2. Psychographic Pain-Point Fingerprinting
Structured `snake_case` tag arrays per lead. Every outreach email says *"I noticed your school struggles with manual attendance tracking"* — not a generic opener.

### 3. Heat Score™ Algorithm
0–100 composite score using urgency, sentiment, role seniority, recency decay, and specificity signals. HOT leads pin to the top automatically.

### 4. Contextual AI Outreach Engine
Gemini generates unique emails referencing each lead's exact post content. No template fills. Every message is different.

### 5. Real Gmail SMTP Dispatch
Actual emails land in inboxes during demo. Not simulated. Logged in the database with full audit trail.

### 6. WebSocket Live Scrape Feed
Leads appear on the Kanban board in real-time as the scraper runs. No refresh. Animated live indicator in the sidebar.

### 7. Lead Intelligence Summary Card
Per-lead AI sales coach — talk track, feature highlights, objection responses, and follow-up timing. Removes the expertise requirement for junior reps.

---

## Demo Flow (Under 3 Minutes)

1. Open dashboard → click **Scrape Now**
2. Watch leads appear live on the Kanban board via WebSocket
3. Click a 🔴 HOT lead → Intelligence Card opens with talk track + objections
4. Click **Generate Outreach Email** → Gemini writes a personalized email in seconds
5. Edit if needed → enter recipient email → click **Send Email**
6. Lead status moves to **Contacted** automatically
7. Check **Analytics** tab for pipeline stats

---

## Testing

```bash
cd backend

# Run all 31 tests
pytest

# Verbose output
pytest -v

# With coverage
pytest --cov=.

# Specific file
pytest tests/test_leads.py
```

Test coverage: Lead CRUD, Heat Score bucketing, scrape job lifecycle, email simulation, Gemini mock responses.

---

## Competitive Edge

| Capability | Basic Scraper CRM | LeadForge EDU |
|---|---|---|
| Lead discovery | Keyword match | 5-stage intent classification |
| Scoring | None | 5-signal Heat Score™ 0–100 |
| Outreach | Template fill | Gemini references exact post content |
| Email | Simulated button | Real Gmail SMTP send |
| Dashboard updates | Manual refresh | WebSocket live feed |
| Sales intel | None | Talk track + objection forecast per lead |
| Pain point extraction | None | Structured tag array per lead |
| Database | SQLite / hosted | PostgreSQL + indexes + async ORM |
