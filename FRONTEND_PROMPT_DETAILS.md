# LeadForge EDU - Frontend Architecture & Flow Details

This document outlines the entire frontend flow, state management, component architecture, and specific UI fields for the LeadForge EDU application. It is designed to be used as a comprehensive prompt context for AI development or further iterations.

## 1. High-Level Architecture
- **Framework:** React (Single Page Application via Vite)
- **Styling:** Tailwind CSS (utility classes, specific color themes per priority and status)
- **State Management:** React `useState` / `useEffect` at the `App.jsx` root level, passed down via props.
- **Real-time Engine:** Custom `useWebSocket` hook connecting to FastAPI backend (`ws://localhost:8000/ws/leads`).
- **API Client:** Axios (`services/api.js`) to interact with REST endpoints.

---

## 2. Global State & App Flow (`App.jsx`)
`App.jsx` acts as the single source of truth for the application's data.

### Global State Variables:
- `activeTab` (string): Controls which view is rendered (`dashboard`, `scraper`, `intelligence`, `outreach`, `analytics`).
- `leads` (array): The master list of all scraped leads.
- `stats` (object): Dashboard metrics.
- `selectedLeadForIntel` (object | null): Lead selected to view the AI Intelligence Card.
- `selectedLeadForOutreach` (object | null): Lead selected to view the Outreach Email Editor.
- `isScraping` (boolean): Global scraping execution state.
- `scrapeCount` (number): Real-time counter of leads fetched in the current scrape job.

### WebSocket Flow:
Listens to `ws://localhost:8000/ws/leads`.
- **`JOB_STARTED`**: Sets `isScraping` to true, resets `scrapeCount`.
- **`NEW_LEAD`**: Appends the new lead to `leads` array, increments `scrapeCount` (live UI update).
- **`JOB_COMPLETED`**: Sets `isScraping` to false, triggers a fresh fetch of all leads via REST.
- **`LEAD_UPDATED`**: Replaces the matching lead in the `leads` array with updated data (e.g., after email sent).

---

## 3. The 5 Main Views (`Views.jsx` & `KanbanBoard.jsx`)

### A. Dashboard View (`KanbanBoard.jsx`)
- **Purpose:** Primary CRM view.
- **Sorting Logic:** Sorts leads by `priority` (HOT > WARM > COLD), then by `lead_score` (Descending).
- **Columns (4):**
  1. **New** (Indigo styling)
  2. **Drafted** (Purple styling)
  3. **Contacted** (Emerald styling)
  4. **Closed** (Slate styling)
- **Interaction:** Clicking a `LeadCard` sets `selectedLeadForIntel`, opening the `IntelCard`.

### B. Scraper View (`ScraperView`)
- **Fields & Elements:**
  - **Platform Select:** Dropdown to choose scrape source (default: Reddit).
  - **Scrape Button:** Triggers `POST /scrape`. Disabled while `isScraping` is true.
  - **Live Counter UI:** Shows `scrapeCount` with a bouncing green pulse animation when active.
  - **Recent Leads Table:** Columns: `Username`, `Role`, `Priority`, `Score` (visual progress bar), `Intent`, `Post` (External link).

### C. Intelligence View (`IntelligenceView`)
- **Purpose:** Grid view of only "enriched" leads (leads with `pain_point_tags` or `intent_label`).
- **Card Fields shown:** Username, Role, Priority badge, Heat Score, Intent badge, Pain Point tags (max 3), truncated post content.
- **Interaction:** Clicking opens the `IntelCard`.

### D. Outreach View (`OutreachView`)
- **Purpose:** List view of leads currently in `Drafted` or `Contacted` status.
- **Fields shown:** Username, Platform, Role, generated `ai_subject` (truncated), Status badge.
- **Interaction:** "Review & Send" or "View Email" buttons open the `OutreachModal`.

### E. Analytics View (`AnalyticsView`)
- **Fields & Metrics:**
  - **Total Leads**, **HOT Leads**, **Avg HeatScore**, **Contacted**, **Conversion Rate** (Contacted / Total), **Closed**.
  - **Priority Breakdown:** Progress bars showing % of HOT, WARM, COLD leads.
  - **Intent Distribution:** Tally of intent labels (`ACTIVELY_SEEKING`, `FRUSTRATED_CURRENT_USER`, etc.) sorted descending.

---

## 4. Key Components & Modals

### A. Lead Card (`LeadCard.jsx`)
Displayed inside the Kanban Board columns.
- **Header:** Platform icon (e.g., Reddit orange), Platform Name, Priority Badge (`HOT`/`WARM`/`COLD`).
- **Body:** Username, Truncated Post Content (line-clamp-2).
- **Tags:** Intent Label (colored background depending on intent type), up to 3 Pain Point Tags (e.g., `#manual grading`).
- **Heat Score Bar:** Visual progress bar (0-100), color changes based on priority (Red/Orange/Blue).
- **Footer:** Detected Role, Urgency Level (High/Medium/Low), Time Ago (extracted_at).

### B. Intelligence Card (`IntelCard.jsx`)
Fixed bottom-right overlay representing deep AI analysis.
- **Header Fields:** Username, Detected Role, Priority, Score.
- **Link:** Direct hyperlink to original Reddit post.
- **Pain Points:** Full list of extracted tags.
- **AI Generated Sections (Loaded via `getLeadIntelligence` API):**
  - **Opening Line (`talk_track`):** Suggested intro for the sales rep.
  - **Key Features to Highlight (`feature_highlights`):** Bulleted list.
  - **Handle Objections (`objection_responses`):** Key-value pairs of possible objections and how to counter them.
  - **Follow-up Timing (`follow_up_timing`):** e.g., "In 2 days".
- **Action Button:** "Generate Outreach Email" (closes IntelCard, opens OutreachModal).

### C. Outreach Modal (`OutreachModal.jsx`)
Central modal for AI email generation and dispatch.
- **Lead Summary Header:** Username, Platform, Role, Urgency, Priority, Heat Score, Pain point tags.
- **Form Fields:**
  - **Recipient Email** (`recipientEmail`): Input field (type="email"). If blank, defaults to a simulation address.
  - **Subject Line** (`subject`): Input field populated by AI generation.
  - **Message Body** (`body`): Textarea (min-h-[180px]) populated by AI generation.
- **Actions & API Calls:**
  1. **Generate with AI:** Calls `generateMessage(lead.id)`. Returns AI Subject and Body, sets lead status to `Drafted`.
  2. **Send Email:** Calls `sendEmail(...)`. Updates lead status to `Contacted`.
- **UI States:** `isGenerating` (loading spinner/pulse), `isSending`, Error banner, Success banner.

---

## 5. Styling Rules & Enums
- **Priority Logic:**
  - `HOT`: Score > 70. (Red colors: `bg-red-50`, `text-red-600`)
  - `WARM`: Score 40-70. (Orange colors)
  - `COLD`: Score < 40. (Blue colors)
- **Intent Types:**
  - `ACTIVELY_SEEKING`, `FRUSTRATED_CURRENT_USER`, `BUDGET_APPROVED`, `PEER_RECOMMENDATION_ASK`, `RESEARCH_PHASE`.

## 6. Backend Integration Map
- `GET /leads`: Fetches initial Kanban board and table data.
- `POST /scrape`: Triggered from ScraperView.
- `ws://localhost:8000/ws/leads`: Provides live websocket pipeline.
- `GET /outreach/intelligence/{id}`: Triggered when opening `IntelCard`.
- `POST /outreach/generate-message/{id}`: Triggered inside `OutreachModal`.
- `POST /outreach/send-email/{id}`: Triggered on dispatch inside `OutreachModal`.
