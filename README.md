# CV Screener — Role-Based AI Pipeline

> **Screen and rank candidates automatically.** Upload a job description and a batch of CVs; an LLM pipeline understands the JD, parses each CV, scores candidate-to-job fit, and returns a ranked shortlist with reasoning.

![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT-412991?logo=openai&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)

**▶️ Live demo:** _paste your URL here after deploy_ · 🚀 **Deploy guide:** [DEPLOY.md](./DEPLOY.md) (Render + Vercel, free)

---

## Why it's interesting

Most "AI resume screeners" are a single prompt. This one decomposes screening into **three distinct LLM-driven roles** — JD understanding, CV parsing, and fit scoring — so each step is isolated, debuggable, and easy to tune (swap the fit-scoring prompt/model without touching CV parsing). Today these roles run **in-process inside one FastAPI service**; the backend is laid out (`gateway/` + per-role `*_agent/` dirs) so any role can be split into its own service later without changing callers.

## Features

- 🧩 **Role decomposition** — separate JD-understanding, CV-parsing, and fit-scoring steps orchestrated by one gateway app
- 📊 **Ranked shortlist** — candidates scored and ordered against the role with per-candidate reasoning
- 🖱️ **Interactive UI** — drag-and-drop CV upload and results dashboard (`@dnd-kit`)
- 🔌 **Split-ready seam** — per-role base URLs are env-configurable and default to in-process; flesh out an `*_agent/` dir into its own FastAPI app and it can be mounted/deployed separately, no caller changes
- 🗃️ **Persistent** — results stored via SQLAlchemy

## Architecture

```
backend/
  ├─ app_combined.py   single deployable entry point (re-exports the gateway app)
  ├─ gateway/          the FastAPI app — runs JD / CV / Fit logic in-process, calls OpenAI
  ├─ cv_agent/         scaffold for splitting CV parsing into its own service (future)
  ├─ jd_agent/         scaffold for splitting JD understanding into its own service (future)
  └─ fit_agent/        scaffold for splitting fit scoring into its own service (future)
frontend/              Next.js 15 UI (upload, results, dashboards)
```

> Note: the `*_agent/` directories are currently placeholders — all logic lives in `gateway/`. They mark the intended seam for a future microservice split (see [DEPLOY.md](./DEPLOY.md), Option B).

## Tech Stack

- **Backend:** Python, FastAPI (single service via `app_combined.py`), SQLAlchemy
- **AI:** OpenAI (GPT) for JD parsing, CV parsing & fit scoring
- **Frontend:** Next.js 15 + React 19 + TypeScript, `@dnd-kit`

## Getting Started

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=your_key            # required for analysis
uvicorn app_combined:app --reload         # http://localhost:8000  (/healthz to check)
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev                               # http://localhost:3000
```

## Configuration

All secrets (API keys, DB URLs) load from environment / `.env` files, which are git-ignored. `OPENAI_API_KEY` is required for analysis; `ALLOWED_ORIGINS` controls CORS for your frontend URL. Real keys are never committed.
