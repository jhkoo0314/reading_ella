"""Local-first explanation assist service."""

from __future__ import annotations

import json

from backend.app.core.config import get_settings
from backend.app.schemas.assist import ExplanationRequest, ExplanationResponse
from backend.app.services.assist_common import (
    AssistExternalApiDisabledError,
    AssistProviderUnavailableError,
    AssistRequestError,
    get_pack_payload,
    get_question,
)
from backend.app.services.gemini_client import generate_json_response
from backend.app.services.model_router import select_explanation_model


def _build_local_response(request: ExplanationRequest) -> ExplanationResponse | None:
    question = get_question(get_pack_payload(request.pack_id), request.question_id)
    rationale = str(question.get("rationale") or "").strip()
    if not rationale:
        return None
    return ExplanationResponse(
        source="local_rationale",
        pack_id=request.pack_id,
        question_id=request.question_id,
        target_lang=request.target_lang,
        detail_level=request.detail_level,
        explanation=rationale,
    )


def _build_mock_explanation(request: ExplanationRequest) -> str:
    payload = get_pack_payload(request.pack_id)
    question = get_question(payload, request.question_id)
    choices = question.get("choices")
    if not isinstance(choices, list) or len(choices) != 4:
        raise AssistRequestError("문항 choices 정보가 잘못되었습니다.")

    correct_index = int(question.get("answer_index"))
    correct_choice = str(choices[correct_index])
    chosen_choice = str(choices[request.chosen_index])

    if request.detail_level == "deep":
        return (
            f"[mock-{request.target_lang}] 정답은 '{correct_choice}' 입니다. "
            f"학생이 고른 '{chosen_choice}' 는 지문 근거와 덜 맞습니다. "
            "정답 선택지는 글에서 직접 보이거나 두 정보를 자연스럽게 연결합니다."
        )

    return (
        f"[mock-{request.target_lang}] 정답은 '{correct_choice}' 입니다. "
        f"'{chosen_choice}' 는 글의 핵심 근거와 맞지 않습니다."
    )


def _build_api_response(request: ExplanationRequest) -> ExplanationResponse:
    payload = get_pack_payload(request.pack_id)
    question = get_question(payload, request.question_id)
    settings = get_settings()
    question_skill = str(question.get("skill") or "").strip() or None
    model_used = select_explanation_model(detail_level=request.detail_level, question_skill=question_skill)

    if not request.allow_external_api:
        raise AssistExternalApiDisabledError("로컬 해설이 없고 allow_external_api=false 이므로 외부 해설을 호출할 수 없습니다.")

    if not settings.explanation_api_available:
        raise AssistProviderUnavailableError(
            f"외부 해설 provider가 설정되지 않았습니다. 선택 모델은 {model_used} 입니다."
        )

    provider = settings.explanation_provider
    if provider == "gemini":
        raw_choices = question.get("choices")
        if not isinstance(raw_choices, list) or len(raw_choices) != 4:
            raise AssistRequestError("문항 choices 정보가 잘못되었습니다.")

        correct_index = int(question.get("answer_index"))
        correct_choice = str(raw_choices[correct_index])
        chosen_choice = str(raw_choices[request.chosen_index])
        rationale = str(question.get("rationale") or "").strip()

        translated = generate_json_response(
            model=model_used,
            system_instruction=(
                "You explain English reading multiple-choice questions for Korean elementary learners. "
                "Use simple Korean. Keep the explanation concrete and tied to the passage. "
                "Return JSON only."
            ),
            user_prompt=(
                f"Explain this question in {request.target_lang}.\n"
                'Return exactly this JSON shape: {"explanation":"..."}\n'
                f"DETAIL_LEVEL: {request.detail_level}\n"
                f"QUESTION: {str(question.get('prompt') or '')}\n"
                f"CHOICES: {json.dumps([str(choice or '') for choice in raw_choices], ensure_ascii=False)}\n"
                f"CORRECT_CHOICE: {correct_choice}\n"
                f"STUDENT_CHOICE: {chosen_choice}\n"
                f"LOCAL_RATIONALE: {rationale or '(none)'}\n"
                "If detail_level is short, answer in 2-3 short sentences. "
                "If detail_level is deep, answer in 4-6 short sentences with clearer reasoning."
            ),
            temperature=0.3 if request.detail_level == "deep" else 0.2,
        )
        if not isinstance(translated, dict):
            raise AssistRequestError("Gemini 해설 응답 형식이 잘못되었습니다.")

        return ExplanationResponse(
            source="api_live",
            provider_used=provider,
            model_used=model_used,
            pack_id=request.pack_id,
            question_id=request.question_id,
            target_lang=request.target_lang,
            detail_level=request.detail_level,
            explanation=str(translated.get("explanation") or "").strip(),
        )

    if provider != "mock":
        raise AssistProviderUnavailableError(
            f"explanation provider={provider} 는 아직 연결되지 않았습니다. 선택 모델은 {model_used} 입니다."
        )

    return ExplanationResponse(
        source="api_live",
        provider_used=provider,
        model_used=model_used,
        pack_id=request.pack_id,
        question_id=request.question_id,
        target_lang=request.target_lang,
        detail_level=request.detail_level,
        explanation=_build_mock_explanation(request),
    )


def get_explanation_response(request: ExplanationRequest) -> ExplanationResponse:
    if request.detail_level == "deep" and request.allow_external_api:
        return _build_api_response(request)

    local_response = _build_local_response(request)
    if local_response is not None:
        return local_response
    return _build_api_response(request)
