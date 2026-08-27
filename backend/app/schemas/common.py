"""Shared response schemas.

Module-specific schemas live in `app/modules/<module>/schemas.py`.
Only genuinely cross-cutting shapes belong here.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Liveness response for `GET /health`."""

    status: str = Field(examples=["healthy"])
    service: str = Field(examples=["loksrijan-api"])


class DatabaseHealthResponse(BaseModel):
    """Database reachability report for `GET /health/db`.

    Always returns HTTP 200 so the development status page can render the
    result instead of handling an error. Read the `connected` flag.
    """

    connected: bool
    detail: str
