# CV Screener — Multi-Agent AI

An AI-powered CV screening platform that evaluates candidates against a job
description using a set of cooperating **agents**, each responsible for one part
of the pipeline (JD understanding, CV parsing, fit scoring) behind an API
gateway.

## Architecture

```
backend/
  ├─ gateway/     API gateway / orchestration
  ├─ jd_agent/    parses & structures the job description
  ├─ cv_agent/    parses & structures the candidate CV
  ├─ fit_agent/   scores candidate ↔ job fit
  └─ shared_libs/ common utilities
db/  alembic/     database + migrations
frontend/         Next.js UI (upload, results, dashboards)
infrastructure/   deployment config
```

## Tech Stack

- **Backend:** Python, FastAPI (multi-agent services), Alembic migrations
- **Frontend:** Next.js + React + TypeScript, `@dnd-kit`
- **AI:** LLM-based parsing & scoring

## Getting Started

**Backend** (per agent service):
```bash
cd backend/<agent>
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # add API keys
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Configuration

All secrets (API keys, DB URLs) load from `.env` files, which are git-ignored.
Copy any `.env.example` and fill in your own values.
