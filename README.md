# Trend.ai by Aloe

> What's trending in the Philippines, summarized by AI.

An experimental ETL + AI pipeline that aggregates Philippine news and social
signals (Reddit, Google Trends), then uses AI to summarize, cluster, and
generate daily trending briefings — all served through a web dashboard.

This project is built **experimentation-first**: instead of building the full
pipeline blind, each risky assumption is validated with a small throwaway
script before any database, API, or UI work begins. This README doubles as a
build log — check off phases as you complete them.

---

## Why build it this way

News aggregation looks simple but has several real unknowns:

- Are Philippine news RSS feeds clean and consistently formatted?
- Can an LLM summarize Taglish/local-context headlines well?
- Does embedding similarity actually cluster the same story across outlets?
- Is Reddit + Google Trends data even interesting enough to show?

Rather than build the full schema → pipeline → API → UI stack and discover
these answers late, each assumption gets a fast, disposable experiment first.
Once an experiment passes, its logic gets promoted into the real pipeline.

---

## Tech Stack

| Layer      | Choice                                   |
|------------|-------------------------------------------|
| Backend    | Python (FastAPI)                          |
| Frontend   | Next.js (React)                           |
| Database   | PostgreSQL + pgvector (hosted on Supabase — free tier, doesn't expire) |
| Scheduler  | APScheduler (cron-based polling), run via Fly.io/Railway background worker |
| AI         | Gemini API (free tier) — summarization, clustering, digest |
| Social/Trend signals | Reddit API (r/Philippines), Google Trends PH (pytrends) |
| Hosting    | Frontend: Vercel · Backend/Scheduler: Fly.io or Railway · DB: Supabase |

---

## Project Phases

### Phase 0 — Experimentation (validate before building)

Each experiment is a standalone script in `/experiments`. No DB, no API, no
UI — just run it, read the output, decide keep / tweak / cut.

- [ ] **Experiment 1 — RSS data quality check**
  Pull raw RSS from Rappler, Inquirer, GMA News. Print title, summary,
  timestamp, source. Check for encoding issues, missing fields, inconsistent
  formats.
  → `experiments/01_rss_quality_check.py`

- [ ] **Experiment 2 — AI summarization quality**
  Take 5 real articles from Experiment 1, summarize with Gemini (free tier).
  Check handling of Taglish/local terms, tone, accuracy, length.
  → `experiments/02_summarization_check.py`

- [ ] **Experiment 3 — Clustering feasibility**
  Find 3 outlets covering the same real event. Generate embeddings, compute
  cosine similarity. Verify same-story articles score high and unrelated
  articles score low.
  → `experiments/03_clustering_check.py`

- [ ] **Experiment 4 — Trending signal check**
  Pull Reddit r/Philippines hot posts + Google Trends PH side by side.
  Assess whether this data is genuinely useful trending signal or just noise.
  → `experiments/04_trending_signal_check.py`

- [ ] **Experiment 5 — Daily digest generation**
  Feed Gemini 5–8 summarized stories from the day, generate a written daily
  briefing. Check tone, length, and usefulness.
  → `experiments/05_digest_check.py`

**Exit criteria for Phase 0:** all 5 experiments produce output good enough
to build on. Any experiment that fails gets reworked or cut from scope here
— before any real infrastructure is built.

---

### Phase 1 — Foundation (data layer)

- [ ] Define PostgreSQL schema (`articles`, `sources`, `categories`,
      `trending_terms`, `clusters`)
- [ ] Enable `pgvector` extension for embedding storage
- [ ] Build RSS ingestion script (promote from Experiment 1)
- [ ] Build Reddit + Google Trends ingestion script (promote from Experiment 4)
- [ ] Run ingestion manually, confirm data lands correctly in Postgres

### Phase 2 — Automate the pipeline

- [ ] Wrap ingestion in APScheduler (runs every 15–30 min)
- [ ] Add transform logic: HTML stripping, dedupe, timestamp normalization

### Phase 3 — Backend API

- [ ] `GET /articles` — paginated, filterable by category/source/date
- [ ] `GET /trending` — current trending terms/topics
- [ ] `GET /digest` — latest daily digest
- [ ] **First demoable milestone:** real data flowing through a live,
      automated pipeline, queryable via API

### Phase 4 — AI enrichment layer

- [ ] Auto-summarization on ingest (promote from Experiment 2)
- [ ] Category classification (Politics, Business, Showbiz, Sports,
      Weather/Disaster, Metro/Local)
- [ ] Embedding-based clustering (promote from Experiment 3)
- [ ] Scheduled daily digest generation (promote from Experiment 5)

### Phase 5 — Frontend

- [ ] Feed view (article cards with AI summary, source, category filter)
- [ ] Story cluster view (same event, multiple sources)
- [ ] Trending sidebar (Reddit + Google Trends terms)
- [ ] Daily digest page
- [ ] Deploy: frontend on Vercel, backend + scheduler on Fly.io/Railway,
      database on Supabase (avoids Render's free-tier DB expiry and
      service-sleep issues for an always-on scheduled pipeline)

### Phase 6 — Polish

- [ ] Architecture diagram
- [ ] Screenshots / demo GIF
- [ ] Scope notes (e.g., Twitter/X API intentionally excluded due to cost;
      Facebook Graph API excluded because Meta removed public trending-topic
      access and general Page-independent data requires Business
      Verification + App Review; YouTube Trending PH considered but left out
      of v1 to keep signal scope tight — documented as deliberate tradeoffs,
      not oversights)
- [ ] Deployed live link

---

## Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (with `pgvector` extension available) — locally via
  Docker/Postgres.app for development, or a free
  [Supabase](https://supabase.com) project for a persistent hosted DB
- A Gemini API key (free tier) — [aistudio.google.com](https://aistudio.google.com)
- A Reddit API app (client ID/secret) — free at
  [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)

### 1. Clone and set up the backend

```bash
git clone https://github.com/<your-username>/trend-ai-by-aloe.git
cd trend-ai-by-aloe

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/trendai
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=trendai-by-aloe/0.1
```

### 3. Run Phase 0 experiments

```bash
python experiments/01_rss_quality_check.py
python experiments/02_summarization_check.py
python experiments/03_clustering_check.py
python experiments/04_trending_signal_check.py
python experiments/05_digest_check.py
```

Review each script's output before moving to Phase 1.

### 4. Database setup (Phase 1+)

```bash
createdb trendai
psql trendai -c "CREATE EXTENSION IF NOT EXISTS vector;"
alembic upgrade head   # once migrations exist
```

### 5. Run the backend (Phase 3+)

```bash
uvicorn app.main:app --reload
```

### 6. Run the frontend (Phase 5+)

```bash
cd frontend
npm install
npm run dev
```

---

## Project Structure (target)

```
trend-ai-by-aloe/
├── experiments/          # Phase 0 throwaway validation scripts
├── app/                  # FastAPI backend
│   ├── main.py
│   ├── models/
│   ├── routers/
│   ├── ingestion/        # RSS, Reddit, Google Trends scripts
│   ├── ai/                # Summarization, clustering, digest logic
│   └── scheduler.py
├── frontend/              # Next.js app
├── requirements.txt
├── .env.example
└── README.md
```

---

## Deployment

Free-tier stack, chosen specifically because this project needs an
**always-on backend with a scheduled background job** and a **persistent
database** — which Render's free tier doesn't reliably support (services
sleep after 15 min idle; free Postgres DBs expire after 30 days).

| Component | Host | Why |
|-----------|------|-----|
| Frontend (Next.js) | **Vercel** | Free Hobby tier, auto-deploy from GitHub, custom domain |
| Backend + Scheduler (FastAPI + APScheduler) | **Fly.io** or **Railway** | Free allowance supports small always-on services/workers, unlike Render's free tier |
| Database (Postgres + pgvector) | **Supabase** | Free tier, doesn't expire, pgvector built in |

### Deployment steps

1. **Database (Supabase)**
   - Create a free project at [supabase.com](https://supabase.com)
   - Enable the `vector` extension from the Supabase SQL editor:
     `CREATE EXTENSION IF NOT EXISTS vector;`
   - Copy the connection string into `DATABASE_URL`

2. **Backend + Scheduler (Fly.io)**
   ```bash
   fly launch          # from the project root, follow prompts
   fly secrets set GEMINI_API_KEY=... DATABASE_URL=... REDDIT_CLIENT_ID=... REDDIT_CLIENT_SECRET=...
   fly deploy
   ```
   Railway is a drop-in alternative if you prefer its dashboard-first
   workflow: connect the GitHub repo, set the same env vars, deploy.

3. **Frontend (Vercel)**
   ```bash
   cd frontend
   vercel               # follow prompts, link to GitHub repo for auto-deploy
   ```
   Set `NEXT_PUBLIC_API_URL` in Vercel's project settings to your deployed
   backend URL from step 2.

4. **Verify the scheduler is running**
   Check Fly.io/Railway logs to confirm the ingestion job fires on its
   interval and articles are landing in the Supabase table.

---

## Roadmap Beyond v1

- Twitter/X trending integration (pending affordable API access)
- Facebook signal integration (pending Business Verification / App Review,
  or a viable public-data workaround)
- YouTube Trending PH as an additional signal source
- Multi-language support (Filipino-first summaries)
- Personalized digest based on reading history
- Push notifications for breaking/trending stories

---

## Author

Built by **Aloe** as part of an ongoing series of AI-powered product
experiments — see also: **Knowledge Index** (FAQ RAG Chatbot).
