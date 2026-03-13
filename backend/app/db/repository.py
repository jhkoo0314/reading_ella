"""Simple SQLite repository helpers for attempts and follow-up items."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from backend.app.db.database import get_db_connection, initialize_database


@dataclass(frozen=True)
class AttemptRecord:
    attempt_id: str
    pack_id: str
    started_at: str
    finished_at: str
    raw_score: int
    total_score: int


@dataclass(frozen=True)
class AttemptAnswerRecord:
    attempt_id: str
    question_id: str
    skill: str
    chosen_index: int
    is_correct: bool


@dataclass(frozen=True)
class FollowUpItemRecord:
    attempt_id: str
    pack_id: str
    question_id: str
    skill: str
    status: str
    created_at: str
    reason: str


def save_attempt_bundle(
    *,
    attempt: AttemptRecord,
    answers: Sequence[AttemptAnswerRecord],
    follow_up_items: Sequence[FollowUpItemRecord],
    database_path: Path | None = None,
) -> None:
    resolved_path = initialize_database(database_path)

    with get_db_connection(resolved_path) as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO attempts (
                attempt_id,
                pack_id,
                started_at,
                finished_at,
                raw_score,
                total_score
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                attempt.attempt_id,
                attempt.pack_id,
                attempt.started_at,
                attempt.finished_at,
                attempt.raw_score,
                attempt.total_score,
            ),
        )
        connection.execute("DELETE FROM attempt_answers WHERE attempt_id = ?", (attempt.attempt_id,))
        connection.execute("DELETE FROM follow_up_items WHERE attempt_id = ?", (attempt.attempt_id,))

        connection.executemany(
            """
            INSERT INTO attempt_answers (
                attempt_id,
                question_id,
                skill,
                chosen_index,
                is_correct
            ) VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    answer.attempt_id,
                    answer.question_id,
                    answer.skill,
                    answer.chosen_index,
                    int(answer.is_correct),
                )
                for answer in answers
            ],
        )

        connection.executemany(
            """
            INSERT INTO follow_up_items (
                attempt_id,
                pack_id,
                question_id,
                skill,
                status,
                created_at,
                reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    item.attempt_id,
                    item.pack_id,
                    item.question_id,
                    item.skill,
                    item.status,
                    item.created_at,
                    item.reason,
                )
                for item in follow_up_items
            ],
        )

        connection.commit()


def get_table_counts(database_path: Path | None = None) -> dict[str, int]:
    table_names = ("attempts", "attempt_answers", "follow_up_items")
    counts: dict[str, int] = {}

    with get_db_connection(database_path) as connection:
        for table_name in table_names:
            row = connection.execute(f"SELECT COUNT(*) AS count FROM {table_name}").fetchone()
            counts[table_name] = int(row["count"]) if row is not None else 0

    return counts
