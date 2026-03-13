"""Routes for optional translation, explanation, and TTS helpers."""

from fastapi import APIRouter, HTTPException

from backend.app.schemas.assist import (
    ExplanationRequest,
    ExplanationResponse,
    TranslationRequest,
    TranslationResponse,
    TtsRequest,
    TtsResponse,
)
from backend.app.services.assist_common import (
    AssistExternalApiDisabledError,
    AssistProviderUnavailableError,
    AssistRequestError,
    AssistServiceError,
)
from backend.app.services.explanation_assist import get_explanation_response
from backend.app.services.pack_loader import PackNotFoundError, PackValidationError
from backend.app.services.translation_assist import get_translation_response
from backend.app.services.tts_assist import get_tts_response


router = APIRouter(prefix="/assist")


@router.post("/translation", response_model=TranslationResponse, summary="Load local translation or call external translation")
def translate_content(request: TranslationRequest) -> TranslationResponse:
    try:
        return get_translation_response(request)
    except AssistRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AssistExternalApiDisabledError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except PackNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AssistProviderUnavailableError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except PackValidationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except AssistServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/explanation", response_model=ExplanationResponse, summary="Load local rationale or call external explanation")
def explain_wrong_answer(request: ExplanationRequest) -> ExplanationResponse:
    try:
        return get_explanation_response(request)
    except AssistRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AssistExternalApiDisabledError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except PackNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AssistProviderUnavailableError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except PackValidationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except AssistServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/tts", response_model=TtsResponse, summary="Return browser-first TTS plan or call external TTS")
def prepare_tts(request: TtsRequest) -> TtsResponse:
    try:
        return get_tts_response(request)
    except AssistRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PackNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AssistProviderUnavailableError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except PackValidationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except AssistServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
