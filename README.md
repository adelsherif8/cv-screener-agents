# CV Screener — Multi-Agent AI

> **Screen and rank candidates automatically.** Upload a job description and a batch of CVs; a team of cooperating LLM agents parses each one, scores candidate-to-job fit, and returns a ranked shortlist with reasoning.

![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-multi--agent-009688?logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT-412991?logo=openai&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)

**▶️ Live demo:** _deploying — see [Run locally](#getting-started) for now_

---

## Why it's interesting

Most "AI resume screeners" are a single prompt. This one is a **multi-agent system**: each agent owns one job and exposes its own FastAPI service behind a gateway, so the pipeline is modular, debuggable, and easy to extend (swap the fit-scoring model without touching CV parsing).

## Features

- 🧩 **Specialized agents** — separate JD-understanding, CV-parsing, and fit-scoring agents orchestrated by a gateway
- 📊 **Ranked shortlist** — candidates scored and ordered against the role with per-candidate reasoning
- 🖱️ **Interactive UI** — drag-and-drop CV upload and results dashboard (`@dnd-kit`)
- 🔌 **Service-oriented** — each agent is an independent FastAPI app, swappable in isolation
- 🗃️ **Persistent** — results stored via SQLAlchemy + Alembic migrations

## Architecture

```
backend/
  ├─ gateway/     API gateway / orchestration  (FastAPI)
  ├─ jd_agent/    parses & structures the job description
  ├─ cv_agent/    parses & structures the candidate CV
  ├─ fit_agent/   scores candidate ↔ job fit
  └─ shared_libs/ common utilities
alembic/          database migrations
frontend/         Next.js 15 UI (upload, results, dashboards)
```

## Tech Stack

- **Backend:** Python, FastAPI (multi-agent services), SQLAlchemy + Alembic
- **AI:** OpenAI (GPT) for parsing & fit scoring
- **Frontend:** Next.js 15 + React 19 + TypeScript, `@dnd-kit`

## Getting Started

**Backend** (run each agent service, or the gateway):
```bash
cd backend/gateway          # or backend/<agent>
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env         # add OPENAI_API_KEY
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev                  # http://localhost:3000
```

## Configuration

All secrets (API keys, DB URLs) load from `.env` files, which are git-ignored. Copy each `.env.example` and fill in your own values — real keys are never committed.
