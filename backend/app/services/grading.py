"""Deterministic grading and submission persistence."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from backend.app.db.database import get_db_connection, initialize_database
from backend.app.db.repository import (
    AttemptAnswerRecord,
    AttemptRecord,
    FollowUpItemRecord,
    save_attempt_bundle,
)
from backend.app.schemas.submit import ScoreSummary, SkillScore, SubmitAnswerResult, SubmitRequest, SubmitResponse
from backend.app.services.pack_loader import (
    PackNotFoundError,
    PackRequestError,
    PackValidationError,
    get_validated_pack_payload_by_id,
)


SEOUL = ZoneInfo("Asia/Seoul")
EXPECTED_OFFSET = timedelta(hours=9)
SKILL_ORDER = ("main_idea", "detail", "inference", "vocab_in_context")


def _parse_kst_timestamp(raw_value: str, *, field_name: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(raw_value)
    except ValueError as exc:
        raise PackRequestError(f"{field_name}는 ISO8601 시간 문자열이어야 합니다.") from exc

    if parsed.tzinfo is None or parsed.utcoffset() != EXPECTED_OFFSET:
        raise PackRequestError(f"{field_name}의 타임존은 반드시 +09:00 이어야 합니다.")
    return parsed


def _normalize_timestamp(value: datetime) -> str:
    return value.astimezone(SEOUL).isoformat(timespec="seconds")


def _attempt_id_exists(attempt_id: str) -> bool:
    with get_db_connection() as connection:
        row = connection.execute(
            "SELECT 1 AS found FROM attempts WHERE attempt_id = ? LIMIT 1",
            (attempt_id,),
        ).fetchone()
    return row is not None


def _generate_attempt_id(pack_id: str, finished_at: datetime) -> str:
    base_id = f"att_{finished_at.strftime('%Y%m%d_%H%M%S')}_{pack_id}"
    if not _attempt_id_exists(base_id):
        return base_id

    suffix = 2
    while True:
        candidate = f"{base_id}_{suffix}"
        if not _attempt_id_exists(candidate):
            return candidate
        suffix += 1


def _extract_questions(payload: dict[str, Any]) -> list[dict[str, Any]]:
    questions = payload.get("questions")
    if not isinstance(questions, list):
        raise PackValidationError("pack questions 정보가 없습니다.")
    return questions


def _build_answer_lookup(submit_request: SubmitRequest, expected_question_ids: list[str]) -> dict[str, int]:
    if len(submit_request.answers) != len(expected_question_ids):
        raise PackRequestError(f"answers는 반드시 {len(expected_question_ids)}개여야 합니다.")

    answer_lookup: dict[str, int] = {}
    for answer in submit_request.answers:
        if answer.question_id in answer_lookup:
            raise PackRequestError(f"question_id={answer.question_id} 가 중복 제출되었습니다.")
        answer_lookup[answer.question_id] = answer.chosen_index

    missing = [question_id for question_id in expected_question_ids if question_id not in answer_lookup]
    extra = [question_id for question_id in answer_lookup if question_id not in expected_question_ids]

    if missing:
        raise PackRequestError(f"답이 빠진 문항이 있습니다: {', '.join(missing)}")
    if extra:
        raise PackRequestError(f"pack에 없는 question_id가 포함되어 있습니다: {', '.join(extra)}")

    return answer_lookup


def grade_submission(submit_request: SubmitRequest) -> SubmitResponse:
    initialize_database()
    payload = get_validated_pack_payload_by_id(submit_request.pack_id)
    questions = _extract_questions(payload)

    started_at = _parse_kst_timestamp(submit_request.started_at, field_name="started_at")
    finished_at = datetime.now(SEOUL)
    if started_at > finished_at:
        raise PackRequestError("started_at이 finished_at보다 미래일 수는 없습니다.")

    expected_question_ids = [str(question["id"]) for question in questions]
    answer_lookup = _build_answer_lookup(submit_request, expected_question_ids)

    by_skill: dict[str, SkillScore] = {
        skill: SkillScore(correct=0, total=0) for skill in SKILL_ORDER
    }
    answer_results: list[SubmitAnswerResult] = []
    answer_records: list[AttemptAnswerRecord] = []
    follow_up_items: list[FollowUpItemRecord] = []
    wrong_question_ids: list[str] = []
    raw_score = 0

    finished_at_text = _normalize_timestamp(finished_at)
    started_at_text = _normalize_timestamp(started_at)
    attempt_id = _generate_attempt_id(submit_request.pack_id, finished_at)

    for question in questions:
        question_id = str(question["id"])
        skill = str(question["skill"])
        chosen_index = answer_lookup[question_id]
        answer_index = int(question["answer_index"])
        is_correct = chosen_index == answer_index

        current_skill_score = by_skill[skill]
        by_skill[skill] = SkillScore(
            correct=current_skill_score.correct + int(is_correct),
            total=current_skill_score.total + 1,
        )

        if is_correct:
            raw_score += 1
        else:
            wrong_question_ids.append(question_id)
            follow_up_items.append(
                FollowUpItemRecord(
                    attempt_id=attempt_id,
                    pack_id=submit_request.pack_id,
                    question_id=question_id,
                    skill=skill,
                    status="pending",
                    created_at=finished_at_text,
                    reason="wrong_answer",
                )
            )

        answer_results.append(
            SubmitAnswerResult(
                question_id=question_id,
                chosen_index=chosen_index,
                is_correct=is_correct,
            )
        )
        answer_records.append(
            AttemptAnswerRecord(
                attempt_id=attempt_id,
                question_id=question_id,
                skill=skill,
                chosen_index=chosen_index,
                is_correct=is_correct,
            )
        )

    save_attempt_bundle(
        attempt=AttemptRecord(
            attempt_id=attempt_id,
            pack_id=submit_request.pack_id,
            started_at=started_at_text,
            finished_at=finished_at_text,
            raw_score=raw_score,
            total_score=len(questions),
        ),
        answers=answer_records,
        follow_up_items=follow_up_items,
    )

    return SubmitResponse(
        attempt_id=attempt_id,
        pack_id=submit_request.pack_id,
        started_at=started_at_text,
        finished_at=finished_at_text,
        answers=answer_results,
        score=ScoreSummary(
            raw=raw_score,
            total=len(questions),
            by_skill=by_skill,
        ),
        wrong_question_ids=wrong_question_ids,
    )
