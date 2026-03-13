"""Routes for loading pending review items."""

from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas.result import ReviewListResponse
from backend.app.services.pack_loader import PackNotFoundError, PackValidationError
from backend.app.services.result_loader import ResultLoadError, get_review_list


router = APIRouter(prefix="/review-items")


@router.get("", response_model=ReviewListResponse, summary="Load pending review items")
def read_review_items(limit: int = Query(default=50, ge=1, le=200)) -> ReviewListResponse:
    try:
        return get_review_list(limit=limit)
    except PackNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PackValidationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ResultLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
