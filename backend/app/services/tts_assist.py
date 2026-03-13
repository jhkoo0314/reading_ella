"""Browser-first TTS assist service."""

from __future__ import annotations

from backend.app.core.config import get_settings
from backend.app.schemas.assist import TtsRequest, TtsResponse
from backend.app.services.assist_common import AssistProviderUnavailableError, AssistRequestError, get_pack_payload, get_question


DEFAULT_VOICE_LOCALE = "en-US"


def _require_question_id(request: TtsRequest) -> str:
    if request.scope == "passage":
        return ""
    if request.question_id is None or not request.question_id.strip():
        raise AssistRequestError("question_prompt 또는 question_choices 범위는 question_id가 필요합니다.")
    return request.question_id.strip()


def _build_text(request: TtsRequest) -> tuple[str, str | None]:
    payload = get_pack_payload(request.pack_id)
    question_id = _require_question_id(request)

    if request.scope == "passage":
        passage = payload.get("passage")
        if not isinstance(passage, dict):
            raise AssistRequestError("pack passage 정보가 없습니다.")
        return str(passage.get("text") or ""), None

    question = get_question(payload, question_id)
    if request.scope == "question_prompt":
        return str(question.get("prompt") or ""), question_id

    raw_choices = question.get("choices")
    if not isinstance(raw_choices, list) or len(raw_choices) != 4:
        raise AssistRequestError("문항 choices 정보가 잘못되었습니다.")

    text = " ".join(f"{index + 1}. {str(choice)}" for index, choice in enumerate(raw_choices))
    return text, question_id


def get_tts_response(request: TtsRequest) -> TtsResponse:
    text, question_id = _build_text(request)
    settings = get_settings()

    if not request.allow_external_api:
        return TtsResponse(
            source="browser_tts",
            pack_id=request.pack_id,
            scope=request.scope,
            question_id=question_id,
            playback_mode="browser",
            voice_locale=DEFAULT_VOICE_LOCALE,
            text=text,
        )

    if not settings.tts_api_available:
        raise AssistProviderUnavailableError("외부 TTS provider가 설정되지 않았습니다. 브라우저 TTS를 기본으로 사용하세요.")

    provider = settings.tts_provider
    if provider != "mock":
        raise AssistProviderUnavailableError(f"tts provider={provider} 는 아직 연결되지 않았습니다.")

    return TtsResponse(
        source="api_live",
        provider_used=provider,
        voice_used=settings.tts_voice_default,
        pack_id=request.pack_id,
        scope=request.scope,
        question_id=question_id,
        playback_mode="external",
        voice_locale=DEFAULT_VOICE_LOCALE,
        text=text,
        audio_url=f"mock://tts/{request.pack_id}/{request.scope}/{question_id or 'passage'}",
    )
