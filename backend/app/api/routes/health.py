"""Health-check endpoints."""

from fastapi import APIRouter

from backend.app.core.config import get_settings
from backend.app.schemas.health import HealthCheckResponse


router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse, summary="Backend health check")
def read_health() -> HealthCheckResponse:
    settings = get_settings()
    return HealthCheckResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )
