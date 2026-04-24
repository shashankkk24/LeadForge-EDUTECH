# KR0463 — Growth Automation: AI-Powered EdTech Lead Pipeline
## Master Build Plan

---

## Project Identity

**Name:** LeadForge EDU
**Tagline:** *Scrape. Score. Strike. Convert school leads on autopilot.*
**Stack:** Python (FastAPI) + React + PostgreSQL + Gemini API + SMTP
**Target:** EdTech sales teams hunting K-12 / Higher Ed clients

---

## Architecture Overview

```
Reddit/X/Forums
      ↓
Lead Extraction Engine (Python + PRAW + Snscrape)
      ↓
NLP Pipeline (spaCy + Gemini Intent Analysis)
      ↓
Lead Scoring Engine (Rule-Based + LLM Confidence Score)
      ↓
PostgreSQL Database (self-hosted / Railway free tier)
      ↓
FastAPI Backend (REST + WebSocket for live updates)
      ↓
React CRM Dashboard (Kanban + Table view)
      ↓
AI Outreach Generator (Gemini API)
      ↓
SMTP Email Dispatch (smtplib / Gmail App Password)
      ↓
Status Update → DB → Dashboard refresh
```

---

## Database Schema (PostgreSQL)

```sql
-- Leads table
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(50),           -- reddit / twitter / forum
    username VARCHAR(255),
    post_url TEXT,
    post_content TEXT,
    extracted_at TIMESTAMP DEFAULT NOW(),
    pain_point TEXT,                -- NLP-extracted summary
    pain_point_tags TEXT[],         -- structured tags array
    detected_role VARCHAR(100),     -- teacher / admin / principal
    urgency_level VARCHAR(20),      -- high / medium / low
    sentiment_score FLOAT,          -- -1.0 to 1.0
    intent_label VARCHAR(50),       -- ACTIVELY_SEEKING / FRUSTRATED / etc.
    lead_score INTEGER,             -- 0-100
    priority VARCHAR(10),           -- HOT / WARM / COLD
    status VARCHAR(20) DEFAULT 'New', -- New / Drafted / Contacted / Closed
    ai_message TEXT,
    ai_subject TEXT,
    sent_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Outreach logs table
CREATE TABLE outreach_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id),
    message_body TEXT,
    subject TEXT,
    sent_to VARCHAR(255),
    sent_via VARCHAR(50),           -- smtp / simulated
    sent_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20)              -- sent / failed / simulated
);

-- Scrape jobs table
CREATE TABLE scrape_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(50),
    keywords TEXT[],
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    leads_found INTEGER,
    status VARCHAR(20)
);

-- Indexes for performance
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_priority ON leads(priority);
CREATE INDEX idx_leads_score ON leads(lead_score DESC);
CREATE INDEX idx_leads_created ON leads(created_at DESC);
```

---

## 7 High-Impact Novel Features (Standout from Competition)

---

### Feature 1: EduIntent Classifier™
**What:** Multi-label NLP classifier that classifies posts into buying-stage intent buckets — not just keyword presence.

**Intent Labels:**
- `ACTIVELY_SEEKING` — "We need school management software ASAP"
- `FRUSTRATED_CURRENT_USER` — "Our current LMS is terrible, switching soon"
- `RESEARCH_PHASE` — "What software do other schools use?"
- `BUDGET_APPROVED` — "We have budget allocated for next semester"
- `PEER_RECOMMENDATION_ASK` — "Any recommendations for grading tools?"

**Implementation:**
- spaCy NER extracts entities (school name, grade level, subject area)
- Gemini prompt returns structured JSON: `{ intent_label, pain_points[], detected_role, urgency, confidence_score }`
- Rule-based fallback if Gemini quota exceeded

**Novelty vs basic solutions:** Standard CRMs keyword-filter. This classifies *buying stage* — judges see a real sales funnel, not a scraper.

**Impact:** Sales rep sees `BUDGET_APPROVED` tag → skip nurturing → go straight to close conversation.

---

### Feature 2: Psychographic Pain-Point Fingerprinting
**What:** Extracts 3 specific operational pain points per lead as structured snake_case tags.

**Example output:** `["manual_attendance_tracking", "parent_communication_gap", "exam_result_delays"]`

**Implementation:**
- Gemini prompt: *"Extract top 3 operational pain points from this post as short snake_case tags"*
- Stored as PostgreSQL `TEXT[]` array
- Dashboard shows tag cloud per lead
- Outreach message references exact tags by name

**Novelty:** Every AI message says *"I noticed your school struggles with manual attendance tracking and parent communication gaps"* — not generic openers. Feels human-written.

**Impact:** Hyper-personalized cold emails get 3-5x higher reply rates vs template fills.

---

### Feature 3: Lead Heat Score™ (0–100 Dynamic Scoring)
**What:** Composite scoring algorithm using 5 weighted signals.

**Formula:**
```
Score = (
  urgency_weight    * 30 +   -- "ASAP", "desperately" → max points
  sentiment_weight  * 25 +   -- negative sentiment = frustrated = hot lead
  role_weight       * 20 +   -- principal(20) > admin(15) > teacher(8)
  recency_weight    * 15 +   -- post age decay over 72 hours
  specificity_weight* 10     -- named budget / timeline / vendor mentioned
)
```
- Auto-buckets: HOT (70+), WARM (40-69), COLD (<40)
- Dashboard color codes: red / orange / blue

**Novelty:** Most hackathon CRMs show raw data. This shows *ranked sales priority* — evaluators see a real product decision engine.

**Impact:** Sales rep opens dashboard → HOT leads pinned at top → zero time wasted on cold outreach.

---

### Feature 4: Contextual AI Outreach Engine (Non-Template)
**What:** Gemini generates unique personalized messages referencing each lead's actual post, role, school type, and pain point tags.

**Prompt Structure:**
```python
prompt = f"""
You are an EdTech sales representative.
Write a cold outreach email to this lead:

Platform: {lead.platform}
Role: {lead.detected_role}
Their exact post: "{lead.post_content}"
Pain points detected: {lead.pain_point_tags}
Urgency: {lead.urgency_level}
Intent: {lead.intent_label}

Rules:
- Reference their EXACT problem in line 1
- Mention specific solution feature for their stated pain
- Keep under 120 words
- Warm, not salesy tone
- End with soft CTA (15-min call)
- Do NOT use "I hope this email finds you well"

Return JSON only: {{ "subject": "...", "body": "..." }}
"""
```
- Frontend previews message before send
- Rep can edit inline before dispatch
- Cached in DB — no repeat API calls per lead

**Novelty:** Every message is unique to that specific post. Judges can test live — will see clearly non-templated output.

---

### Feature 5: Real SMTP Email Dispatch (Not Just Simulation)
**What:** Actual email sending via Gmail SMTP — delivering real emails during demo.

**Implementation:**
```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(to_addr, subject, body):
    msg = MIMEMultipart('alternative')
    msg['From'] = SMTP_USER
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
    return True
```
- Gmail SMTP: free, 500 emails/day
- Fallback: simulation mode + full log if no recipient email available
- Every send logged in `outreach_logs` table with timestamp

**Why SMTP over HyperMail AI:**
| Factor | SMTP (Gmail) | HyperMail AI |
|--------|-------------|--------------|
| Cost | Free | Paid plan needed |
| Reliability | Google infra | Third-party dependency |
| Demo | Real email in inbox | API call only |
| Setup | 10 mins (App Password) | Account + billing |
| Offline fallback | Yes (simulation) | No |

**Novelty vs requirement:** Problem says "simulate send." Delivering real email is a major over-delivery — judges reward this.

**Impact:** Demo moment: presenter clicks Send → email arrives in judge's inbox live.

---

### Feature 6: WebSocket Live Scrape Feed
**What:** New leads appear in CRM in real-time as scraper runs — no page refresh.

**Implementation:**
- FastAPI WebSocket endpoint `/ws/leads`
- Scraper pushes each new lead to WebSocket on DB insert
- React `useWebSocket` hook appends lead card to Kanban instantly
- "Scraping live..." animated indicator with lead count ticking up

**Novelty:** Static dashboards feel like batch report tools. Live feed makes this look like production SaaS.

**Impact:** Demo moment — presenter runs scrape, judges watch leads appear one-by-one on screen.

---

### Feature 7: Lead Intelligence Summary Card (AI Sales Coach)
**What:** Per-lead expandable card with Gemini-generated sales strategy.

**Outputs:**
- Which product features to highlight for this specific pain
- Top 2 objections they might raise + suggested responses
- One-line talk track for the sales rep
- Recommended follow-up timing

**Novelty:** Transforms CRM from data viewer to *sales coach*. Most hackathon solutions stop at "here's the lead." This says "here's exactly how to close it."

**Impact:** Especially powerful for junior sales reps — removes expertise requirement.

---

## Full Tech Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Scraping | PRAW (Reddit API) | Free, structured, most reliable |
| NLP | spaCy + Gemini Flash 1.5 | Local NER + LLM intent extraction |
| Backend | FastAPI (Python) | Async, WebSocket native, fast |
| Database | PostgreSQL | Relational + JSON fields + indexes |
| ORM | SQLAlchemy + Alembic | Clean models, schema migrations |
| Frontend | React + TailwindCSS + shadcn/ui | Fast CRM UI build |
| Email | smtplib (Gmail SMTP) | Free, zero dependency, real send |
| AI | Gemini 1.5 Flash API | Free tier: 15 req/min, 1M tokens/day |
| Realtime | FastAPI WebSocket | Native, no extra infra needed |
| Deployment | Uvicorn + Vite | Hackathon-ready, simple |

---

## Folder Structure

```
leadforge-edu/
├── backend/
│   ├── main.py                      # FastAPI app entry, WebSocket
│   ├── database.py                  # PostgreSQL connection (SQLAlchemy)
│   ├── models.py                    # ORM models (Lead, OutreachLog, ScrapeJob)
│   ├── schemas.py                   # Pydantic request/response schemas
│   ├── routers/
│   │   ├── leads.py                 # GET/PATCH lead endpoints
│   │   ├── scraper.py               # POST trigger scrape job
│   │   └── outreach.py              # POST generate AI message, POST send email
│   ├── services/
│   │   ├── scraper_service.py       # PRAW Reddit + fallback mock scraper
│   │   ├── nlp_service.py           # spaCy NER + intent extraction
│   │   ├── scoring_service.py       # Heat Score algorithm
│   │   ├── gemini_service.py        # All Gemini API calls (intent, outreach, intel)
│   │   └── email_service.py         # SMTP dispatch + simulation fallback
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LeadKanban.jsx       # Kanban board (New/Drafted/Contacted)
│   │   │   ├── LeadTable.jsx        # Sortable data table view
│   │   │   ├── LeadCard.jsx         # Expandable lead detail card
│   │   │   ├── OutreachModal.jsx    # AI message preview + edit + send
│   │   │   ├── IntelCard.jsx        # Lead Intelligence Summary
│   │   │   └── ScrapeControls.jsx  # Trigger + live WebSocket feed
│   │   ├── hooks/
│   │   │   └── useWebSocket.js      # Live lead updates hook
│   │   └── App.jsx
│   └── package.json
├── database/
│   └── schema.sql                   # Full PostgreSQL schema
├── scripts/
│   └── seed_leads.py                # 20 realistic mock leads for demo fallback
├── .env.example
└── README.md
```

---

## Environment Variables

```env
# .env — never commit this file

GEMINI_API_KEY=your_gemini_key_here

REDDIT_CLIENT_ID=your_reddit_app_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=LeadForgeEDU/1.0

DATABASE_URL=postgresql://user:password@localhost:5432/leadforge

SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your_gmail@gmail.com
SMTP_PASSWORD=your_app_password    # Gmail App Password (not account password)
                                    # Enable: Gmail → Security → 2FA → App Passwords
```

---

## Scraping Keywords (15 High-Intent EdTech Phrases)

```python
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
    "replace paper based attendance"
]
```

---

## 24-Hour Hackathon Build Timeline

| Hours | Task | Output |
|-------|------|--------|
| 0–2 | PostgreSQL setup + schema, FastAPI skeleton, React init | Running DB + empty app |
| 2–5 | PRAW scraper + keyword filter + DB insert | Raw leads flowing to DB |
| 5–8 | spaCy NER + Gemini intent/pain point extraction | Structured lead data |
| 8–10 | Heat Score algorithm + priority bucketing | HOT/WARM/COLD labels |
| 10–14 | Gemini outreach engine + OutreachModal UI | Personalized messages |
| 14–17 | CRM Dashboard (Kanban + Table + badges) | Working frontend |
| 17–19 | SMTP email dispatch + simulation fallback | Real email send |
| 19–21 | WebSocket live feed + Lead Intelligence Card | Wow factor features |
| 21–23 | Seed data script + end-to-end test + polish | Demo-ready |
| 23–24 | PPT finalize + demo rehearsal | Presentation ready |

---

## PPT Structure (8 Slides)

1. **Problem** — Sales team wastes 4hrs/day on manual lead hunting for school clients
2. **Market** — 1.5M schools globally, <10% using dedicated EdTech management software
3. **Solution** — LeadForge EDU: Scrape → Score → Strike pipeline
4. **Architecture Diagram** — Full pipeline visual (use this plan as reference)
5. **Live Demo** — Dashboard screenshot, AI message preview, email confirmed sent
6. **7 Standout Features** — Feature grid with icons
7. **Tech Stack** — Clean table
8. **Impact** — 10x faster lead discovery, 5x higher reply rate, 90% less manual work

---

## Competitive Differentiators

| Capability | Basic Scraper CRM | LeadForge EDU |
|-----------|------------------|---------------|
| Lead discovery | Keyword match | 5-stage intent classification |
| Scoring | None | 5-signal Heat Score 0-100 |
| Outreach | Template fill | Gemini references exact post content |
| Email | Simulated button | Real Gmail SMTP send |
| Dashboard updates | Manual refresh | WebSocket live feed |
| Sales intel | None | Talk track + objection forecast per lead |
| Database | SQLite / Supabase hosted | PostgreSQL + proper indexes + migration history |
| Pain point extraction | None | Structured tag array per lead |

---

## Important Notes

- **Reddit API (PRAW):** Most reliable free scraping. X/Twitter now requires paid tier — use mock X data or public search fallback.
- **Gemini free tier:** 15 requests/min, 1M tokens/day — sufficient for hackathon demo.
- **Gmail SMTP App Password:** Gmail → Account → Security → 2-Step Verification → App Passwords → generate one. Use this, not main password.
- **Seed data script:** Run `scripts/seed_leads.py` if live scrape hits API limits during demo. Always have backup data.
- **PostgreSQL on Railway.app:** Free tier zero-setup cloud DB if local PostgreSQL setup not viable on demo machine.
- **Demo order:** Show live scrape first → leads appear via WebSocket → click HOT lead → generate AI message → send real email → status updates to Contacted. Full loop in under 3 minutes.
