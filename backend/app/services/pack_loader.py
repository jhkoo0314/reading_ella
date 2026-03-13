"""Load public pack responses from local JSON content files."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from backend.app.core.config import get_settings
from backend.app.schemas.pack import (
    AssistInfo,
    ExplanationAssist,
    PackLoadResponse,
    PublicPassage,
    PublicQuestion,
    TranslationAssist,
    TtsAssist,
)
from scripts.validate_packs import validate_pack

VALID_LEVELS = {"GT", "S", "MGT"}


class PackServiceError(Exception):
    """Base error for pack-loading failures."""


class PackNotFoundError(PackServiceError):
    """Raised when no pack file can be found."""


class PackValidationError(PackServiceError):
    """Raised when a pack file has blocking validation errors."""


class PackRequestError(PackServiceError):
    """Raised when the request inputs are invalid."""


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _get_pack_path(pack_id: str) -> Path:
    return get_settings().packs_dir / f"{pack_id}.json"


def _list_pack_files() -> list[Path]:
    packs_dir = get_settings().packs_dir
    return sorted(path for path in packs_dir.glob("*.json") if path.is_file())


def _load_translation(pack_id: str, lang: str) -> dict[str, Any] | None:
    translation_path = get_settings().translations_dir / lang / f"{pack_id}.json"
    if not translation_path.exists():
        return None
    return _read_json(translation_path)


def _ensure_pack_is_valid(path: Path) -> None:
    validation = validate_pack(path)
    if validation.errors:
        joined = "; ".join(validation.errors)
        raise PackValidationError(f"{path.name} pack 형식이 잘못되었습니다: {joined}")


def _is_pack_valid(path: Path) -> bool:
    validation = validate_pack(path)
    return not validation.errors


def _extract_meta(payload: dict[str, Any]) -> dict[str, Any]:
    meta = payload.get("meta")
    if not isinstance(meta, dict):
        raise PackValidationError("pack meta 정보가 없습니다.")
    return meta


def _extract_translation_assist(pack_id: str, translation_payload: dict[str, Any] | None, lang: str) -> TranslationAssist:
    if translation_payload is None:
        return TranslationAssist(
            lang=lang,
            passage_available=False,
            question_prompt_ids=[],
            question_choice_ids=[],
        )

    passage = translation_payload.get("passage")
    questions = translation_payload.get("questions")
    passage_available = False
    prompt_ids: list[str] = []
    choice_ids: list[str] = []

    if isinstance(passage, dict):
        title_translated = str(passage.get("title_translated") or "").strip()
        text_translated = str(passage.get("text_translated") or "").strip()
        passage_available = bool(title_translated or text_translated)

    if isinstance(questions, list):
        for question in questions:
            if not isinstance(question, dict):
                continue
            question_id = str(question.get("id") or "").strip()
            if not question_id:
                continue
            prompt_translated = str(question.get("prompt_translated") or "").strip()
            if prompt_translated:
                prompt_ids.append(question_id)
            choices = question.get("choices_translated")
            if isinstance(choices, list) and any(str(choice or "").strip() for choice in choices):
                choice_ids.append(question_id)

    return TranslationAssist(
        lang=lang,
        passage_available=passage_available,
        question_prompt_ids=prompt_ids,
        question_choice_ids=choice_ids,
    )


def _build_response(payload: dict[str, Any], *, lang: str) -> PackLoadResponse:
    settings = get_settings()
    meta = _extract_meta(payload)
    pack_id = str(meta.get("pack_id"))
    topic = str(meta.get("topic"))

    passage_payload = payload["passage"]
    questions_payload = payload["questions"]
    translation_payload = _load_translation(pack_id, lang)

    public_questions = [
        PublicQuestion(
            id=str(question["id"]),
            skill=str(question["skill"]),
            prompt=str(question["prompt"]),
            choices=[str(choice) for choice in question["choices"]],
        )
        for question in questions_payload
    ]

    local_rationale_available = any(str(question.get("rationale") or "").strip() for question in questions_payload)

    return PackLoadResponse(
        pack_id=pack_id,
        topic=topic,
        passage=PublicPassage(
            title=str(passage_payload["title"]),
            text=str(passage_payload["text"]),
            word_count=int(passage_payload["word_count"]),
        ),
        questions=public_questions,
        assist=AssistInfo(
            translation=_extract_translation_assist(pack_id, translation_payload, lang),
            explanation=ExplanationAssist(
                local_rationale_available=local_rationale_available,
                api_available=settings.explanation_api_available,
                available_depths=["short", "deep"],
            ),
            tts=TtsAssist(browser_available=True, api_available=settings.tts_api_available),
        ),
    )


def get_translation_overlay(pack_id: str, lang: str) -> dict[str, Any] | None:
    return _load_translation(pack_id, lang)


def get_validated_pack_payload_by_id(pack_id: str) -> dict[str, Any]:
    pack_path = _get_pack_path(pack_id)
    if not pack_path.exists():
        raise PackNotFoundError(f"pack_id={pack_id} 에 해당하는 pack 파일이 없습니다.")

    _ensure_pack_is_valid(pack_path)
    return _read_json(pack_path)


def get_public_pack_by_id(pack_id: str, *, lang: str = "ko") -> PackLoadResponse:
    payload = get_validated_pack_payload_by_id(pack_id)
    return _build_response(payload, lang=lang)


def get_random_public_pack(level: str, *, lang: str = "ko") -> PackLoadResponse:
    normalized_level = level.strip().upper()
    if normalized_level not in VALID_LEVELS:
        raise PackRequestError("level은 GT, S, MGT 중 하나여야 합니다.")

    matching_paths: list[Path] = []
    for path in _list_pack_files():
        payload = _read_json(path)
        meta = payload.get("meta")
        if isinstance(meta, dict) and str(meta.get("level") or "").upper() == normalized_level:
            if _is_pack_valid(path):
                matching_paths.append(path)

    if not matching_paths:
        raise PackNotFoundError(f"level={normalized_level} 에 해당하는 배포 가능한 pack 파일이 없습니다.")

    selected_path = random.choice(matching_paths)
    payload = _read_json(selected_path)
    return _build_response(payload, lang=lang)
