"""Shared helpers for optional assist APIs."""

from __future__ import annotations

from typing import Any

from backend.app.services.pack_loader import get_translation_overlay, get_validated_pack_payload_by_id


class AssistServiceError(Exception):
    """Base error for assist APIs."""


class AssistRequestError(AssistServiceError):
    """Raised when an assist request is malformed."""


class AssistExternalApiDisabledError(AssistServiceError):
    """Raised when a request would need an external API but the toggle is off."""


class AssistProviderUnavailableError(AssistServiceError):
    """Raised when an external provider is missing or not wired."""


class AssistProviderRequestError(AssistServiceError):
    """Raised when an upstream provider request fails after connection was attempted."""


def get_pack_payload(pack_id: str) -> dict[str, Any]:
    return get_validated_pack_payload_by_id(pack_id)


def get_translation_payload(pack_id: str, target_lang: str) -> dict[str, Any] | None:
    return get_translation_overlay(pack_id, target_lang)


def get_pack_meta(payload: dict[str, Any]) -> dict[str, Any]:
    meta = payload.get("meta")
    if not isinstance(meta, dict):
        raise AssistRequestError("pack meta 정보가 없습니다.")
    return meta


def get_pack_level(payload: dict[str, Any]) -> str:
    meta = get_pack_meta(payload)
    return str(meta.get("level") or "").upper()


def get_questions(payload: dict[str, Any]) -> list[dict[str, Any]]:
    questions = payload.get("questions")
    if not isinstance(questions, list):
        raise AssistRequestError("pack questions 정보가 없습니다.")
    return questions


def get_question(payload: dict[str, Any], question_id: str) -> dict[str, Any]:
    normalized_question_id = question_id.strip()
    if not normalized_question_id:
        raise AssistRequestError("question_id는 비워 둘 수 없습니다.")

    for question in get_questions(payload):
        if str(question.get("id") or "").strip() == normalized_question_id:
            return question
    raise AssistRequestError(f"question_id={question_id} 에 해당하는 문항이 없습니다.")


def get_translation_question_entry(translation_payload: dict[str, Any] | None, question_id: str) -> dict[str, Any] | None:
    if translation_payload is None:
        return None

    questions = translation_payload.get("questions")
    if not isinstance(questions, list):
        return None

    for question in questions:
        if not isinstance(question, dict):
            continue
        if str(question.get("id") or "").strip() == question_id:
            return question
    return None
