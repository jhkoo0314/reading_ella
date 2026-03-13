"""Schemas for optional assist APIs such as translation, explanation, and TTS."""

from typing import Literal

from pydantic import BaseModel, Field


TranslationScope = Literal["passage", "question_prompt", "question_choices"]
ExplanationDetailLevel = Literal["short", "deep"]
TtsScope = Literal["passage", "question_prompt", "question_choices"]


class TranslationRequest(BaseModel):
    pack_id: str
    target_lang: str = "ko"
    scope: TranslationScope
    question_id: str | None = None
    allow_external_api: bool = False


class TranslationResponse(BaseModel):
    source: Literal["local_overlay", "api_live"]
    provider_used: str | None = None
    model_used: str | None = None
    pack_id: str
    target_lang: str
    scope: TranslationScope
    question_id: str | None = None
    translated_title: str | None = None
    translated_text: str | None = None
    translated_prompt: str | None = None
    translated_choices: list[str] | None = None


class ExplanationRequest(BaseModel):
    pack_id: str
    question_id: str
    chosen_index: int = Field(ge=0, le=3)
    target_lang: str = "ko"
    detail_level: ExplanationDetailLevel
    allow_external_api: bool = False


class ExplanationResponse(BaseModel):
    source: Literal["local_rationale", "api_live"]
    provider_used: str | None = None
    model_used: str | None = None
    pack_id: str
    question_id: str
    target_lang: str
    detail_level: ExplanationDetailLevel
    explanation: str


class TtsRequest(BaseModel):
    pack_id: str
    scope: TtsScope
    question_id: str | None = None
    allow_external_api: bool = False


class TtsResponse(BaseModel):
    source: Literal["browser_tts", "api_live"]
    provider_used: str | None = None
    voice_used: str | None = None
    pack_id: str
    scope: TtsScope
    question_id: str | None = None
    playback_mode: Literal["browser", "external"]
    voice_locale: str
    text: str
    audio_url: str | None = None
