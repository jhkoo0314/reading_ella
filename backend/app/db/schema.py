"""SQLite schema definitions for Reading ELLA."""

from typing import Final


SCHEMA_STATEMENTS: Final[tuple[str, ...]] = (
    """
    CREATE TABLE IF NOT EXISTS attempts (
        attempt_id TEXT PRIMARY KEY,
        pack_id TEXT NOT NULL,
        started_at TEXT NOT NULL,
        finished_at TEXT NOT NULL,
        raw_score INTEGER NOT NULL,
        total_score INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS attempt_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id TEXT NOT NULL,
        question_id TEXT NOT NULL,
        skill TEXT NOT NULL,
        chosen_index INTEGER NOT NULL,
        is_correct INTEGER NOT NULL CHECK (is_correct IN (0, 1)),
        FOREIGN KEY (attempt_id) REFERENCES attempts (attempt_id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS follow_up_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id TEXT NOT NULL,
        pack_id TEXT NOT NULL,
        question_id TEXT NOT NULL,
        skill TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        reason TEXT NOT NULL,
        FOREIGN KEY (attempt_id) REFERENCES attempts (attempt_id) ON DELETE CASCADE
    )
    """,
)


INDEX_STATEMENTS: Final[tuple[str, ...]] = (
    """
    CREATE INDEX IF NOT EXISTS idx_attempt_answers_attempt_id
    ON attempt_answers (attempt_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_follow_up_items_attempt_id
    ON follow_up_items (attempt_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_follow_up_items_pack_question
    ON follow_up_items (pack_id, question_id)
    """,
)
