"""Schemas for submission and grading responses."""

from pydantic import BaseModel, Field


class SubmitAnswerItem(BaseModel):
    question_id: str
    chosen_index: int = Field(ge=0, le=3)


class SubmitRequest(BaseModel):
    pack_id: str
    started_at: str
    answers: list[SubmitAnswerItem]


class SubmitAnswerResult(BaseModel):
    question_id: str
    chosen_index: int
    is_correct: bool


class SkillScore(BaseModel):
    correct: int
    total: int


class ScoreSummary(BaseModel):
    raw: int
    total: int
    by_skill: dict[str, SkillScore]


class SubmitResponse(BaseModel):
    attempt_id: str
    pack_id: str
    started_at: str
    finished_at: str
    answers: list[SubmitAnswerResult]
    score: ScoreSummary
    wrong_question_ids: list[str]
