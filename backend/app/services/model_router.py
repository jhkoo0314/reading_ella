"""Select assist models from request purpose instead of from the frontend."""

from __future__ import annotations

from backend.app.core.config import get_settings


def select_translation_model(*, scope: str) -> str:
    settings = get_settings()
    return settings.assist_model_default


def select_explanation_model(*, detail_level: str, question_skill: str | None = None) -> str:
    settings = get_settings()
    if detail_level == "deep":
        return settings.assist_model_deep
    return settings.assist_model_default
