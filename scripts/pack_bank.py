"""Shared helpers for Step 5 pack-bank planning."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Final

try:
    from .create_pack import build_pack_id, normalize_number
    from .level_profiles import LEVEL_PROFILES
except ImportError:
    from create_pack import build_pack_id, normalize_number
    from level_profiles import LEVEL_PROFILES


PACKS_PER_LEVEL_TARGET: Final[int] = 100
DEFAULT_PLAN_PATH: Final[Path] = Path("packs") / "pack_bank_plan.csv"
PLAN_COLUMNS: Final[list[str]] = [
    "grade",
    "level",
    "number",
    "pack_id",
    "topic",
    "topic_slug",
    "topic_group",
    "status",
    "notes",
]
LEVEL_TOPIC_GROUPS: Final[dict[str, list[str]]] = {
    "GT": [
        "school",
        "classroom",
        "family",
        "home",
        "weather",
        "animals",
        "food",
        "play",
        "community",
        "nature",
    ],
    "S": [
        "school-life",
        "study-habits",
        "family-jobs",
        "home-routines",
        "health",
        "science",
        "travel",
        "hobby",
        "community",
        "nature",
    ],
    "MGT": [
        "school-projects",
        "community-events",
        "science",
        "environment",
        "history",
        "art",
        "travel",
        "technology",
        "teamwork",
        "problem-solving",
    ],
}


def title_from_group(topic_group: str, slot: int) -> str:
    label = topic_group.replace("-", " ").title()
    return f"{label} Topic {slot:02d}"


def slug_from_group(level: str, topic_group: str, slot: int) -> str:
    return f"{level.lower()}-{topic_group}-{slot:02d}"


def build_plan_rows(*, packs_per_level: int = PACKS_PER_LEVEL_TARGET) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if packs_per_level <= 0:
        raise ValueError("packs_per_level은 1 이상이어야 합니다.")

    for level in LEVEL_PROFILES:
        groups = LEVEL_TOPIC_GROUPS[level]
        for sequence in range(1, packs_per_level + 1):
            number = normalize_number(str(sequence))
            topic_group = groups[(sequence - 1) % len(groups)]
            slot = ((sequence - 1) // len(groups)) + 1
            rows.append(
                {
                    "grade": "G1",
                    "level": level,
                    "number": number,
                    "pack_id": build_pack_id("G1", level, number),
                    "topic": title_from_group(topic_group, slot),
                    "topic_slug": slug_from_group(level, topic_group, slot),
                    "topic_group": topic_group,
                    "status": "planned",
                    "notes": "Replace placeholder topic text with reviewed content before student release.",
                }
            )

    return rows


def write_plan_csv(path: Path, rows: list[dict[str, str]], *, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"이미 파일이 있습니다: {path}. 덮어쓰려면 --force를 사용하세요.")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=PLAN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def load_plan_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError("CSV 헤더가 없습니다.")

        missing = [column for column in PLAN_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"CSV 헤더에 필요한 칼럼이 없습니다: {', '.join(missing)}")

        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]
