"""Schemas for health-check endpoints."""

from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
