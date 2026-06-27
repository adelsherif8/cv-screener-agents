"""
Unified single-service entry point for the CV Screener.

WHY THIS EXISTS
---------------
The repo is structured as if it were a multi-agent system (a gateway plus
``cv_agent`` / ``jd_agent`` / ``fit_agent`` services). In the *current* code,
however, the per-agent directories contain only empty placeholder files
(``main.py`` is 0 bytes). All CV / JD / Fit logic already lives **in-process**
inside the gateway app (``backend/gateway/main.py``), which talks to OpenAI
directly. There are no inter-service HTTP calls and no ``*_AGENT_URL`` env vars
in the codebase.

So "consolidating 4 services into 1" reduces to: expose the gateway app as the
single deployable FastAPI service, with the import paths set up correctly and
CORS made configurable. That is exactly what this module does.

DESIGN
------
* We add ``backend/gateway`` to ``sys.path`` so the gateway's non-package
  imports (e.g. ``from enhanced_cv_analyzer import ...`` and its sibling
  modules ``database``/``models``/``crud``/``auth``/``ai_service``) resolve the
  same way they do when running ``uvicorn main:app`` from inside that dir.
* We import the gateway's ``app`` and re-export it as ``app`` so the start
  command ``uvicorn app_combined:app`` works.
* If/when real agent sub-apps are added under ``backend/<agent>/main.py`` (each
  exposing a FastAPI ``app``), they will be auto-mounted at ``/<agent>`` below.
  Until then those mounts are simply skipped. The base URLs the gateway would
  use to reach them are read from env vars that DEFAULT to the in-process
  localhost mounts, so a single-service deploy works out of the box while a
  multi-service deploy still works if the URLs are overridden.
"""

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup: make the gateway package importable exactly like it expects.
# ---------------------------------------------------------------------------
_BACKEND_DIR = Path(__file__).resolve().parent
_GATEWAY_DIR = _BACKEND_DIR / "gateway"

for _p in (str(_BACKEND_DIR), str(_GATEWAY_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------------------------------------------------------------------
# Import the real application. The gateway IS the single consolidated service.
# ---------------------------------------------------------------------------
# Imported after the sys.path tweak above so the gateway's module-style imports
# (``from enhanced_cv_analyzer import ...`` etc.) resolve.
from main import app as app  # noqa: E402  (gateway FastAPI app, re-exported)

# ---------------------------------------------------------------------------
# Per-agent base URLs.
#
# These default to the in-process mounts on localhost so a single-service
# deploy needs no configuration. They can be overridden via env vars to point
# at separately deployed agent services (multi-service deploy) without code
# changes. The current gateway does not call these (the logic is in-process),
# but the contract is here for future split-outs.
# ---------------------------------------------------------------------------
_PORT = os.getenv("PORT", "8000")
_SELF = f"http://127.0.0.1:{_PORT}"

CV_AGENT_URL = os.getenv("CV_AGENT_URL", f"{_SELF}/cv-agent")
JD_AGENT_URL = os.getenv("JD_AGENT_URL", f"{_SELF}/jd-agent")
FIT_AGENT_URL = os.getenv("FIT_AGENT_URL", f"{_SELF}/fit-agent")

# ---------------------------------------------------------------------------
# Optionally mount real agent sub-apps if they exist (each must expose ``app``).
# Today these are empty placeholders, so nothing is mounted.
# ---------------------------------------------------------------------------
def _try_mount_agent(mount_path: str, module_name: str) -> None:
    """Mount ``backend/<agent>/main.py:app`` at ``mount_path`` if importable."""
    agent_main = _BACKEND_DIR / module_name / "main.py"
    if not agent_main.exists() or agent_main.stat().st_size == 0:
        return  # empty placeholder — nothing to mount
    try:
        import importlib

        mod = importlib.import_module(f"{module_name}.main")
        sub_app = getattr(mod, "app", None)
        if sub_app is not None:
            app.mount(mount_path, sub_app)
    except Exception:  # pragma: no cover - best-effort optional mount
        # Never let an optional agent break the unified service boot.
        pass


for _mount, _module in (
    ("/cv-agent", "cv_agent"),
    ("/jd-agent", "jd_agent"),
    ("/fit-agent", "fit_agent"),
):
    _try_mount_agent(_mount, _module)


# ---------------------------------------------------------------------------
# Configurable CORS.
#
# The gateway hardcodes ``allow_origins=["*"]``. For a real deploy we honor an
# ``ALLOWED_ORIGINS`` env var (comma-separated) when provided, and add a second,
# explicit CORS middleware layer. If unset we keep the permissive default so
# nothing breaks. Note: with credentialed requests, "*" is treated as no-origin
# by browsers; set ALLOWED_ORIGINS to your frontend URL in production.
# ---------------------------------------------------------------------------
_allowed = os.getenv("ALLOWED_ORIGINS", "").strip()
if _allowed:
    from fastapi.middleware.cors import CORSMiddleware

    origins = [o.strip() for o in _allowed.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ---------------------------------------------------------------------------
# Lightweight unified health endpoint.
#
# The gateway already exposes ``GET /health``. We add ``GET /healthz`` (a
# distinct path) so platform health checks have a guaranteed, dependency-free
# probe on the unified app regardless of the gateway's internals.
# ---------------------------------------------------------------------------
@app.get("/healthz", tags=["health"])
async def healthz():
    return {
        "status": "ok",
        "service": "cv-screener-unified",
        "agents": {
            "cv_agent_url": CV_AGENT_URL,
            "jd_agent_url": JD_AGENT_URL,
            "fit_agent_url": FIT_AGENT_URL,
        },
    }
