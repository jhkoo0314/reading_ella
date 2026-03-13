"""Local-first translation assist service."""

from __future__ import annotations

import json

from typing import Any

from backend.app.core.config import get_settings
from backend.app.schemas.assist import TranslationRequest, TranslationResponse
from backend.app.services.assist_common import (
    AssistExternalApiDisabledError,
    AssistProviderUnavailableError,
    AssistRequestError,
    get_pack_payload,
    get_question,
    get_translation_payload,
    get_translation_question_entry,
)
from backend.app.services.gemini_client import generate_json_response
from backend.app.services.model_router import select_translation_model


def _require_question_id(request: TranslationRequest) -> str:
    if request.scope == "passage":
        return ""
    if request.question_id is None or not request.question_id.strip():
        raise AssistRequestError("question_full 범위는 question_id가 필요합니다.")
    return request.question_id.strip()


def _normalize_choices(raw_choices: Any) -> list[str] | None:
    if not isinstance(raw_choices, list):
        return None
    normalized = [str(choice or "").strip() for choice in raw_choices]
    if not any(normalized):
        return None
    return normalized


def _build_local_response(request: TranslationRequest) -> TranslationResponse | None:
    question_id = _require_question_id(request)
    translation_payload = get_translation_payload(request.pack_id, request.target_lang)
    if translation_payload is None:
        return None

    if request.scope == "passage":
        passage = translation_payload.get("passage")
        if not isinstance(passage, dict):
            return None

        translated_title = str(passage.get("title_translated") or "").strip() or None
        translated_text = str(passage.get("text_translated") or "").strip() or None
        if translated_title is None and translated_text is None:
            return None

        return TranslationResponse(
            source="local_overlay",
            pack_id=request.pack_id,
            target_lang=request.target_lang,
            scope=request.scope,
            translated_title=translated_title,
            translated_text=translated_text,
        )

    question_entry = get_translation_question_entry(translation_payload, question_id)
    if question_entry is None:
        return None

    translated_prompt = str(question_entry.get("prompt_translated") or "").strip() or None
    translated_choices = _normalize_choices(question_entry.get("choices_translated"))
    if translated_prompt is None and translated_choices is None:
        return None
    return TranslationResponse(
        source="local_overlay",
        pack_id=request.pack_id,
        target_lang=request.target_lang,
        scope=request.scope,
        question_id=question_id,
        translated_prompt=translated_prompt,
        translated_choices=translated_choices,
    )


def _mock_translate_text(value: str, *, target_lang: str) -> str:
    return f"[mock-{target_lang}] {value}"


def _build_gemini_translation_response(request: TranslationRequest, *, provider: str, model_used: str) -> TranslationResponse:
    question_id = _require_question_id(request)
    payload = get_pack_payload(request.pack_id)
    target_lang = request.target_lang

    if request.scope == "passage":
        passage = payload.get("passage")
        if not isinstance(passage, dict):
            raise AssistRequestError("pack passage 정보가 없습니다.")

        translated = generate_json_response(
            model=model_used,
            system_instruction=(
                "You translate English reading materials for young learners. "
                "Keep the meaning accurate, simple, and natural. "
                "Return JSON only."
            ),
            user_prompt=(
                f"Translate the following title and passage into {target_lang}.\n"
                "Return exactly this JSON shape:\n"
                '{"translated_title":"...","translated_text":"..."}\n'
                f"TITLE: {str(passage.get('title') or '')}\n"
                f"TEXT: {str(passage.get('text') or '')}"
            ),
            temperature=0.2,
        )
        if not isinstance(translated, dict):
            raise AssistRequestError("Gemini 번역 응답 형식이 잘못되었습니다.")
        return TranslationResponse(
            source="api_live",
            provider_used=provider,
            model_used=model_used,
            pack_id=request.pack_id,
            target_lang=target_lang,
            scope=request.scope,
            translated_title=str(translated.get("translated_title") or "").strip() or None,
            translated_text=str(translated.get("translated_text") or "").strip() or None,
        )

    question = get_question(payload, question_id)
    raw_choices = question.get("choices")
    if not isinstance(raw_choices, list):
        raise AssistRequestError("문항 choices 정보가 없습니다.")

    translated = generate_json_response(
        model=model_used,
        system_instruction=(
            "You translate English reading questions for young learners. "
            "Translate the question and all answer choices together. "
            "Preserve the subtle difference between choices. "
            "Return JSON only."
        ),
        user_prompt=(
            f"Translate this question and its answer choices into {target_lang}.\n"
            'Return exactly this JSON shape: {"translated_prompt":"...","translated_choices":["...", "..."]}\n'
            f"QUESTION: {str(question.get('prompt') or '')}\n"
            f"CHOICES: {json.dumps([str(choice or '') for choice in raw_choices], ensure_ascii=False)}"
        ),
        temperature=0.2,
    )
    if not isinstance(translated, dict):
        raise AssistRequestError("Gemini 문항 번역 응답 형식이 잘못되었습니다.")

    translated_choices = translated.get("translated_choices")
    if not isinstance(translated_choices, list):
        raise AssistRequestError("Gemini 문항 번역 목록 형식이 잘못되었습니다.")

    normalized_choices = [str(choice or "").strip() for choice in translated_choices]
    if len(normalized_choices) != len(raw_choices):
        raise AssistRequestError("Gemini 문항 번역 수가 원본 보기 수와 다릅니다.")

    return TranslationResponse(
        source="api_live",
        provider_used=provider,
        model_used=model_used,
        pack_id=request.pack_id,
        target_lang=target_lang,
        scope=request.scope,
        question_id=question_id,
        translated_prompt=str(translated.get("translated_prompt") or "").strip() or None,
        translated_choices=normalized_choices,
    )


def _build_api_response(request: TranslationRequest) -> TranslationResponse:
    question_id = _require_question_id(request)
    payload = get_pack_payload(request.pack_id)
    settings = get_settings()
    model_used = select_translation_model(scope=request.scope)

    if not request.allow_external_api:
        raise AssistExternalApiDisabledError("로컬 번역이 없고 allow_external_api=false 이므로 외부 번역을 호출할 수 없습니다.")

    if not settings.translation_api_available:
        raise AssistProviderUnavailableError(
            f"외부 번역 provider가 설정되지 않았습니다. 선택 모델은 {model_used} 입니다."
        )

    provider = settings.translation_provider
    if provider == "gemini":
        return _build_gemini_translation_response(request, provider=provider, model_used=model_used)

    if provider != "mock":
        raise AssistProviderUnavailableError(
            f"translation provider={provider} 는 아직 연결되지 않았습니다. 선택 모델은 {model_used} 입니다."
        )

    if request.scope == "passage":
        passage = payload.get("passage")
        if not isinstance(passage, dict):
            raise AssistRequestError("pack passage 정보가 없습니다.")

        translated_title = _mock_translate_text(str(passage.get("title") or ""), target_lang=request.target_lang)
        translated_text = _mock_translate_text(str(passage.get("text") or ""), target_lang=request.target_lang)
        return TranslationResponse(
            source="api_live",
            provider_used=provider,
            model_used=model_used,
            pack_id=request.pack_id,
            target_lang=request.target_lang,
            scope=request.scope,
            translated_title=translated_title,
            translated_text=translated_text,
        )

    question = get_question(payload, question_id)
    raw_choices = question.get("choices")
    if not isinstance(raw_choices, list):
        raise AssistRequestError("문항 choices 정보가 없습니다.")

    translated_prompt = _mock_translate_text(str(question.get("prompt") or ""), target_lang=request.target_lang)
    translated_choices = [
        _mock_translate_text(str(choice or ""), target_lang=request.target_lang)
        for choice in raw_choices
    ]
    return TranslationResponse(
        source="api_live",
        provider_used=provider,
        model_used=model_used,
        pack_id=request.pack_id,
        target_lang=request.target_lang,
        scope=request.scope,
        question_id=question_id,
        translated_prompt=translated_prompt,
        translated_choices=translated_choices,
    )


def get_translation_response(request: TranslationRequest) -> TranslationResponse:
    local_response = _build_local_response(request)
    if local_response is not None:
        return local_response
    return _build_api_response(request)
