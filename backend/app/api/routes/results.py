"""Routes for loading stored result details."""

from fastapi import APIRouter, HTTPException

from backend.app.schemas.result import AttemptResultResponse
from backend.app.services.pack_loader import PackNotFoundError, PackValidationError
from backend.app.services.result_loader import AttemptNotFoundError, ResultLoadError, get_attempt_result


router = APIRouter(prefix="/results")


@router.get("/{attempt_id}", response_model=AttemptResultResponse, summary="Load one stored result by attempt_id")
def read_result(attempt_id: str) -> AttemptResultResponse:
    try:
        return get_attempt_result(attempt_id)
    except AttemptNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PackNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PackValidationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ResultLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
