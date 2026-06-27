# Deploying CV Screener (free tier)

This is shipped as a **single FastAPI service** plus a Next.js frontend. Although
the repo is laid out like a multi-agent system (gateway + `cv_agent` / `jd_agent`
/ `fit_agent`), all CV/JD/Fit logic runs **in-process** inside the gateway app
today (the per-agent directories are empty placeholders). The unified entry point
[`backend/app_combined.py`](./backend/app_combined.py) re-exports that app, so the
whole backend fits comfortably on one free-tier instance.

## Option A — Single backend service + frontend (recommended)
1. **Backend → Render:** New + → **Blueprint** → this repo → **Apply**. It reads
   [`render.yaml`](./render.yaml), which deploys one service from root `backend`
   with start command `uvicorn app_combined:app --host 0.0.0.0 --port $PORT` and
   build `pip install -r requirements.txt`. Health check path is `/healthz`.
   - Set **`OPENAI_API_KEY`** (required) in the Render dashboard.
2. **Frontend → Vercel:** import repo → **Root Directory** = `frontend` → add
   **`NEXT_PUBLIC_API_BASE_URL`** = the Render service URL → Deploy.
3. Back on Render, set **`ALLOWED_ORIGINS`** to your Vercel URL (comma-separated
   if more than one) so CORS allows the frontend.

That's it — one Render service + one Vercel project, both on free tiers.

### Verifying the deploy
- `GET /healthz` → `{"status":"ok", ...}` (lightweight, no external calls).
- `GET /health` → gateway's own health payload.
- `GET /openapi.json` → lists all backend routes.

## Option B — Multi-service (alternative, only if you split the agents out)
The unified app reads per-agent base URLs from env vars that **default to the
in-process localhost mounts**, so single-service works out of the box and you can
override them later without code changes:

| Env var         | Default                          |
| --------------- | -------------------------------- |
| `CV_AGENT_URL`  | `http://127.0.0.1:$PORT/cv-agent`  |
| `JD_AGENT_URL`  | `http://127.0.0.1:$PORT/jd-agent`  |
| `FIT_AGENT_URL` | `http://127.0.0.1:$PORT/fit-agent` |

If you later flesh out `backend/cv_agent` / `jd_agent` / `fit_agent` into real
FastAPI apps (each exposing `app`), `app_combined.py` will auto-mount any that are
non-empty at `/cv-agent`, `/jd-agent`, `/fit-agent`. To run them as separate
Render services instead, deploy each (root dirs `backend/<agent>`) and point the
env vars above at their public URLs. Note this needs paid instances or multiple
free services and is **not** required for a working demo.
