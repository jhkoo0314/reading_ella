"""Minimal Gemini REST client for translation and explanation helpers."""

from __future__ import annotations

import json
from typing import Any
from urllib import error, request

from backend.app.core.config import get_settings
from backend.app.services.assist_common import (
    AssistProviderRequestError,
    AssistProviderUnavailableError,
    AssistServiceError,
)


def _extract_text(response_payload: dict[str, Any]) -> str:
    candidates = response_payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise AssistServiceError("Gemini 응답에 candidates가 없습니다.")

    first_candidate = candidates[0]
    if not isinstance(first_candidate, dict):
        raise AssistServiceError("Gemini candidate 형식이 잘못되었습니다.")

    content = first_candidate.get("content")
    if not isinstance(content, dict):
        raise AssistServiceError("Gemini 응답에 content가 없습니다.")

    parts = content.get("parts")
    if not isinstance(parts, list) or not parts:
        raise AssistServiceError("Gemini 응답에 text parts가 없습니다.")

    texts: list[str] = []
    for part in parts:
        if not isinstance(part, dict):
            continue
        text = part.get("text")
        if isinstance(text, str) and text.strip():
            texts.append(text)

    if not texts:
        raise AssistServiceError("Gemini 응답 text가 비어 있습니다.")
    return "".join(texts).strip()


def _strip_json_fence(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```JSON").removeprefix("```").strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    return cleaned


def generate_json_response(
    *,
    model: str,
    system_instruction: str,
    user_prompt: str,
    temperature: float = 0.2,
) -> Any:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise AssistProviderUnavailableError("GEMINI_API_KEY가 설정되지 않았습니다.")

    endpoint = f"{settings.gemini_api_base_url}/models/{model}:generateContent"
    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction}],
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_prompt}],
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "responseMimeType": "application/json",
        },
    }

    raw_body = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        endpoint,
        data=raw_body,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": settings.gemini_api_key,
        },
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=settings.gemini_timeout_seconds) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        try:
            error_payload = json.loads(exc.read().decode("utf-8"))
            message = error_payload.get("error", {}).get("message") or str(exc)
        except Exception:  # pragma: no cover - defensive parsing
            message = str(exc)
        raise AssistProviderRequestError(f"Gemini API 요청이 실패했습니다: {message}") from exc
    except error.URLError as exc:
        raise AssistProviderRequestError(f"Gemini API 연결에 실패했습니다: {exc.reason}") from exc

    if not isinstance(response_payload, dict):
        raise AssistServiceError("Gemini 응답 형식이 잘못되었습니다.")

    text = _extract_text(response_payload)
    try:
        return json.loads(_strip_json_fence(text))
    except json.JSONDecodeError as exc:
        raise AssistServiceError("Gemini 응답 JSON을 해석하지 못했습니다.") from exc
