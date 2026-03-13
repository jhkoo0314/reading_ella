"""Schemas for public pack-loading responses."""

from pydantic import BaseModel


class PublicPassage(BaseModel):
    title: str
    text: str
    word_count: int


class PublicQuestion(BaseModel):
    id: str
    skill: str
    prompt: str
    choices: list[str]


class TranslationAssist(BaseModel):
    lang: str
    passage_available: bool
    question_prompt_ids: list[str]
    question_choice_ids: list[str]


class ExplanationAssist(BaseModel):
    local_rationale_available: bool
    api_available: bool
    available_depths: list[str]


class TtsAssist(BaseModel):
    browser_available: bool
    api_available: bool


class AssistInfo(BaseModel):
    translation: TranslationAssist
    explanation: ExplanationAssist
    tts: TtsAssist


class PackLoadResponse(BaseModel):
    pack_id: str
    topic: str
    passage: PublicPassage
    questions: list[PublicQuestion]
    assist: AssistInfo
