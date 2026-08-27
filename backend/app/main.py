"""LokSrijan API — application entrypoint.

Run locally with:

    uvicorn app.main:app --reload --port 8000

Interactive docs: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health
from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title="LokSrijan API",
    description=(
        "Backend for LokSrijan — an AI-assisted societal innovation "
        "collaboration platform. SIH / internal hackathon MVP."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None,
)

# CORS — allows the Next.js dev server to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health probes live at the root so they stay stable across API versions.
app.include_router(health.router)

# All feature endpoints live under /api (none registered yet).
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    """Point developers at the docs."""
    return {
        "service": settings.app_name,
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health",
    }
