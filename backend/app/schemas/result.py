"""Schemas for result and review screens."""

from pydantic import BaseModel

from backend.app.schemas.submit import ScoreSummary


class ReviewQuestionItem(BaseModel):
    attempt_id: str
    pack_id: str
    level: str
    topic: str
    passage_title: str
    question_id: str
    question_number: int
    skill: str
    prompt: str
    choices: list[str]
    chosen_index: int
    correct_index: int
    chosen_text: str
    correct_text: str
    finished_at: str
    created_at: str | None = None
    status: str | None = None
    reason: str | None = None


class AttemptResultResponse(BaseModel):
    attempt_id: str
    pack_id: str
    level: str
    topic: str
    passage_title: str
    started_at: str
    finished_at: str
    score: ScoreSummary
    wrong_questions: list[ReviewQuestionItem]


class ReviewListResponse(BaseModel):
    items: list[ReviewQuestionItem]
