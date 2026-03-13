"""Top-level API router."""

from fastapi import APIRouter

from backend.app.api.routes.assist import router as assist_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.packs import router as packs_router
from backend.app.api.routes.results import router as results_router
from backend.app.api.routes.review import router as review_router
from backend.app.api.routes.submissions import router as submissions_router


api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(packs_router, tags=["packs"])
api_router.include_router(submissions_router, tags=["submissions"])
api_router.include_router(results_router, tags=["results"])
api_router.include_router(review_router, tags=["review"])
api_router.include_router(assist_router, tags=["assist"])
