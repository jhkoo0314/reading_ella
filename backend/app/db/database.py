"""SQLite connection and initialization helpers."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from backend.app.core.config import get_settings
from backend.app.db.schema import INDEX_STATEMENTS, SCHEMA_STATEMENTS


def resolve_database_path(database_path: Path | None = None) -> Path:
    if database_path is not None:
        return Path(database_path)
    return get_settings().database_path


def ensure_database_parent(database_path: Path | None = None) -> Path:
    resolved_path = resolve_database_path(database_path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_path


def create_connection(database_path: Path | None = None) -> sqlite3.Connection:
    resolved_path = ensure_database_parent(database_path)
    connection = sqlite3.connect(resolved_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def get_db_connection(database_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    connection = create_connection(database_path)
    try:
        yield connection
    finally:
        connection.close()


def initialize_database(database_path: Path | None = None) -> Path:
    resolved_path = ensure_database_parent(database_path)

    with get_db_connection(resolved_path) as connection:
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)
        for statement in INDEX_STATEMENTS:
            connection.execute(statement)
        connection.commit()

    return resolved_path


def list_table_names(database_path: Path | None = None) -> list[str]:
    with get_db_connection(database_path) as connection:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()
    return [str(row["name"]) for row in rows]
