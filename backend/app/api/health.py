"""Health / liveness endpoints.

Mounted at the application root (not under `/api`) so that infrastructure
probes stay stable even if the API prefix or version changes.
"""

from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.schemas.common import DatabaseHealthResponse, HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Report that the API process is up. Does not touch the database."""
    return HealthResponse(status="healthy", service=settings.app_name)


@router.get("/health/db", response_model=DatabaseHealthResponse)
def health_db() -> DatabaseHealthResponse:
    """Report whether PostgreSQL is reachable.

    Intentionally returns HTTP 200 even when the database is down; the
    caller inspects `connected`. This keeps the developer status page
    simple and makes a missing database obvious rather than fatal.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return DatabaseHealthResponse(connected=True, detail="PostgreSQL reachable")
    except Exception as exc:  # noqa: BLE001 - report any driver/connection error
        return DatabaseHealthResponse(
            connected=False,
            detail=f"{type(exc).__name__}: database not reachable",
        )
