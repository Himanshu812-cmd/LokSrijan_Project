"""Aggregate router for all `/api` endpoints.

Feature modules register their routers here as they are built. Nothing is
wired yet — the module packages exist but expose no endpoints.

Planned groups (see docs/api-contract.md). These are NOT implemented:

    /api/challenges   citizen reports, clusters, validation
    /api/matching     university / NGO / industry recommendations
    /api/projects     project lifecycle
    /api/impact       baseline, target, actual, verification
    /api/dashboard    role-scoped aggregates
    /api/auth         authentication (deliberately deferred)
    /api/users        user + role management

When a module is ready, add it as:

    from app.modules.challenges.routes import router as challenges_router
    api_router.include_router(challenges_router, prefix="/challenges", tags=["challenges"])
"""

from fastapi import APIRouter

api_router = APIRouter()
