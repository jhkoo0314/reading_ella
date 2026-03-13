"""Routes for deterministic grading and result storage."""

from fastapi import APIRouter, HTTPException

from backend.app.schemas.submit import SubmitRequest, SubmitResponse
from backend.app.services.grading import grade_submission
from backend.app.services.pack_loader import PackNotFoundError, PackRequestError, PackServiceError, PackValidationError


router = APIRouter(prefix="/submissions")


@router.post("", response_model=SubmitResponse, summary="Submit answers and get graded result")
def submit_answers(submit_request: SubmitRequest) -> SubmitResponse:
    try:
        return grade_submission(submit_request)
    except PackRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PackNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PackValidationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except PackServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
