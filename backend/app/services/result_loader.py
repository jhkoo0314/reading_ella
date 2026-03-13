"""Load stored result and review data from SQLite and pack JSON files."""

from __future__ import annotations

from typing import Any

from backend.app.db.database import get_db_connection
from backend.app.schemas.result import AttemptResultResponse, ReviewListResponse, ReviewQuestionItem
from backend.app.schemas.submit import ScoreSummary, SkillScore
from backend.app.services.pack_loader import PackValidationError, get_validated_pack_payload_by_id


SKILL_ORDER = ("main_idea", "detail", "inference", "vocab_in_context")


class ResultLoadError(Exception):
    """Base error for stored result loading."""


class AttemptNotFoundError(ResultLoadError):
    """Raised when the requested attempt does not exist."""


def _extract_meta(payload: dict[str, Any]) -> dict[str, Any]:
    meta = payload.get("meta")
    if not isinstance(meta, dict):
        raise PackValidationError("pack meta 정보가 없습니다.")
    return meta


def _extract_passage(payload: dict[str, Any]) -> dict[str, Any]:
    passage = payload.get("passage")
    if not isinstance(passage, dict):
        raise PackValidationError("pack passage 정보가 없습니다.")
    return passage


def _extract_questions(payload: dict[str, Any]) -> list[dict[str, Any]]:
    questions = payload.get("questions")
    if not isinstance(questions, list):
        raise PackValidationError("pack questions 정보가 없습니다.")
    return questions


def _build_question_lookup(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}

    for question_number, question in enumerate(_extract_questions(payload), start=1):
        question_id = str(question.get("id") or "").strip()
        if not question_id:
            continue

        choices = [str(choice or "") for choice in question.get("choices", [])]
        correct_index = int(question["answer_index"])
        correct_text = choices[correct_index] if 0 <= correct_index < len(choices) else ""

        lookup[question_id] = {
            "question_number": question_number,
            "skill": str(question.get("skill") or ""),
            "prompt": str(question.get("prompt") or ""),
            "choices": choices,
            "correct_index": correct_index,
            "correct_text": correct_text,
        }

    return lookup


def _fetch_attempt_row(attempt_id: str) -> Any:
    with get_db_connection() as connection:
        row = connection.execute(
            """
            SELECT attempt_id, pack_id, started_at, finished_at, raw_score, total_score
            FROM attempts
            WHERE attempt_id = ?
            LIMIT 1
            """,
            (attempt_id,),
        ).fetchone()

    if row is None:
        raise AttemptNotFoundError(f"attempt_id={attempt_id} 에 해당하는 결과가 없습니다.")
    return row


def _fetch_attempt_answers(attempt_id: str) -> list[Any]:
    with get_db_connection() as connection:
        rows = connection.execute(
            """
            SELECT question_id, skill, chosen_index, is_correct
            FROM attempt_answers
            WHERE attempt_id = ?
            ORDER BY id ASC
            """,
            (attempt_id,),
        ).fetchall()

    return list(rows)


def _fetch_pending_review_rows(limit: int) -> list[Any]:
    with get_db_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                follow_up_items.attempt_id,
                follow_up_items.pack_id,
                follow_up_items.question_id,
                follow_up_items.skill,
                follow_up_items.status,
                follow_up_items.created_at,
                follow_up_items.reason,
                attempts.finished_at,
                attempt_answers.chosen_index
            FROM follow_up_items
            INNER JOIN attempts
                ON attempts.attempt_id = follow_up_items.attempt_id
            INNER JOIN attempt_answers
                ON attempt_answers.attempt_id = follow_up_items.attempt_id
               AND attempt_answers.question_id = follow_up_items.question_id
            WHERE follow_up_items.status = 'pending'
            ORDER BY follow_up_items.created_at DESC, follow_up_items.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return list(rows)


def _build_score_summary(raw_score: int, total_score: int, answer_rows: list[Any]) -> ScoreSummary:
    by_skill_counts: dict[str, dict[str, int]] = {
        skill: {"correct": 0, "total": 0} for skill in SKILL_ORDER
    }

    for row in answer_rows:
        skill = str(row["skill"])
        if skill not in by_skill_counts:
            by_skill_counts[skill] = {"correct": 0, "total": 0}

        by_skill_counts[skill]["correct"] += int(row["is_correct"])
        by_skill_counts[skill]["total"] += 1

    return ScoreSummary(
        raw=raw_score,
        total=total_score,
        by_skill={
            skill: SkillScore(correct=counts["correct"], total=counts["total"])
            for skill, counts in by_skill_counts.items()
        },
    )


def _build_review_item(
    *,
    pack_id: str,
    level: str,
    topic: str,
    passage_title: str,
    question_details: dict[str, Any],
    chosen_index: int,
    attempt_id: str,
    finished_at: str,
    created_at: str | None = None,
    status: str | None = None,
    reason: str | None = None,
) -> ReviewQuestionItem:
    choices = list(question_details["choices"])
    chosen_text = choices[chosen_index] if 0 <= chosen_index < len(choices) else ""

    return ReviewQuestionItem(
        attempt_id=attempt_id,
        pack_id=pack_id,
        level=level,
        topic=topic,
        passage_title=passage_title,
        question_id=str(question_details["question_id"]),
        question_number=int(question_details["question_number"]),
        skill=str(question_details["skill"]),
        prompt=str(question_details["prompt"]),
        choices=choices,
        chosen_index=chosen_index,
        correct_index=int(question_details["correct_index"]),
        chosen_text=chosen_text,
        correct_text=str(question_details["correct_text"]),
        finished_at=finished_at,
        created_at=created_at,
        status=status,
        reason=reason,
    )


def get_attempt_result(attempt_id: str) -> AttemptResultResponse:
    attempt_row = _fetch_attempt_row(attempt_id)
    answer_rows = _fetch_attempt_answers(attempt_id)
    payload = get_validated_pack_payload_by_id(str(attempt_row["pack_id"]))

    meta = _extract_meta(payload)
    passage = _extract_passage(payload)
    question_lookup = _build_question_lookup(payload)

    wrong_questions: list[ReviewQuestionItem] = []
    for answer_row in answer_rows:
        if int(answer_row["is_correct"]) == 1:
            continue

        question_id = str(answer_row["question_id"])
        question_details = question_lookup.get(question_id)
        if question_details is None:
            raise PackValidationError(f"pack에 question_id={question_id} 가 없습니다.")

        wrong_questions.append(
            _build_review_item(
                pack_id=str(attempt_row["pack_id"]),
                level=str(meta.get("level") or ""),
                topic=str(meta.get("topic") or ""),
                passage_title=str(passage.get("title") or ""),
                question_details={
                    **question_details,
                    "question_id": question_id,
                },
                chosen_index=int(answer_row["chosen_index"]),
                attempt_id=str(attempt_row["attempt_id"]),
                finished_at=str(attempt_row["finished_at"]),
            )
        )

    wrong_questions.sort(key=lambda item: item.question_number)

    return AttemptResultResponse(
        attempt_id=str(attempt_row["attempt_id"]),
        pack_id=str(attempt_row["pack_id"]),
        level=str(meta.get("level") or ""),
        topic=str(meta.get("topic") or ""),
        passage_title=str(passage.get("title") or ""),
        started_at=str(attempt_row["started_at"]),
        finished_at=str(attempt_row["finished_at"]),
        score=_build_score_summary(
            int(attempt_row["raw_score"]),
            int(attempt_row["total_score"]),
            answer_rows,
        ),
        wrong_questions=wrong_questions,
    )


def get_review_list(*, limit: int = 50) -> ReviewListResponse:
    rows = _fetch_pending_review_rows(limit)
    pack_cache: dict[str, dict[str, Any]] = {}
    question_lookup_cache: dict[str, dict[str, dict[str, Any]]] = {}
    meta_cache: dict[str, dict[str, Any]] = {}
    passage_cache: dict[str, dict[str, Any]] = {}
    items: list[ReviewQuestionItem] = []

    for row in rows:
        pack_id = str(row["pack_id"])
        if pack_id not in pack_cache:
            pack_cache[pack_id] = get_validated_pack_payload_by_id(pack_id)
            meta_cache[pack_id] = _extract_meta(pack_cache[pack_id])
            passage_cache[pack_id] = _extract_passage(pack_cache[pack_id])
            question_lookup_cache[pack_id] = _build_question_lookup(pack_cache[pack_id])

        question_id = str(row["question_id"])
        question_details = question_lookup_cache[pack_id].get(question_id)
        if question_details is None:
            raise PackValidationError(f"pack에 question_id={question_id} 가 없습니다.")

        items.append(
            _build_review_item(
                pack_id=pack_id,
                level=str(meta_cache[pack_id].get("level") or ""),
                topic=str(meta_cache[pack_id].get("topic") or ""),
                passage_title=str(passage_cache[pack_id].get("title") or ""),
                question_details={
                    **question_details,
                    "question_id": question_id,
                },
                chosen_index=int(row["chosen_index"]),
                attempt_id=str(row["attempt_id"]),
                finished_at=str(row["finished_at"]),
                created_at=str(row["created_at"]),
                status=str(row["status"]),
                reason=str(row["reason"]),
            )
        )

    return ReviewListResponse(items=items)
