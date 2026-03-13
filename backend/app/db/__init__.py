"""Database helpers for Reading ELLA."""

from backend.app.db.database import create_connection, get_db_connection, initialize_database, list_table_names
from backend.app.db.repository import (
    AttemptAnswerRecord,
    AttemptRecord,
    FollowUpItemRecord,
    get_table_counts,
    save_attempt_bundle,
)

__all__ = [
    "AttemptAnswerRecord",
    "AttemptRecord",
    "FollowUpItemRecord",
    "create_connection",
    "get_db_connection",
    "get_table_counts",
    "initialize_database",
    "list_table_names",
    "save_attempt_bundle",
]
