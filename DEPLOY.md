# Deploying CV Screener (free tier)

> ⚠️ **Honest heads-up:** this is a *multi-service* system — an API gateway plus
> separate `cv_agent`, `jd_agent`, and `fit_agent` FastAPI services, plus a Next.js
> frontend. A free tier can host **one** of these comfortably; running all of them
> end-to-end realistically needs paid instances or consolidation into one process.
> For a quick public demo, **cv-analyzer** is the easier win. Use this when you want
> to showcase the full architecture.

## Option A — Gateway + frontend (partial demo)
1. **Backend (gateway) → Render:** New + → Blueprint → this repo → **Apply** (reads [`render.yaml`](./render.yaml), root `backend/gateway`). Set `OPENAI_API_KEY`.
2. **Frontend → Vercel:** import repo → **Root Directory** = `frontend` → add `NEXT_PUBLIC_API_BASE_URL` = gateway URL → Deploy.
3. Set `ALLOWED_ORIGINS` on Render to the Vercel URL.

## Option B — Full multi-agent (recommended path if you invest more)
Deploy each agent as its own Render web service (root dirs `backend/cv_agent`,
`backend/jd_agent`, `backend/fit_agent`), then give the gateway their URLs via env
vars so it can call them. Duplicate the `render.yaml` service block per agent.

### Consolidation alternative
To fit free tier, merge the agents into the gateway process (import their routers
into one FastAPI app) so it's a single deployable service.
