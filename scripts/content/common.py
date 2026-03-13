"""Shared helpers for level-based content generation."""

from __future__ import annotations

import json
import re
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

try:
    from ..create_pack import DEFAULT_VERSION, build_pack_id, normalize_grade, normalize_level, normalize_number
except ImportError:
    from create_pack import DEFAULT_VERSION, build_pack_id, normalize_grade, normalize_level, normalize_number


SEOUL = ZoneInfo("Asia/Seoul")
WORD_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
SLOT_PATTERN = re.compile(r"-(\d{2})$")
DATA_DIR = Path(__file__).resolve().parent / "data"


@lru_cache(maxsize=None)
def load_json_data(file_name: str) -> dict[str, Any]:
    path = DATA_DIR / file_name
    return json.loads(path.read_text(encoding="utf-8"))


def count_words(text: str) -> int:
    return len(WORD_PATTERN.findall(text))


def pick(options: list[str], slot: int, offset: int = 0) -> str:
    return options[(slot - 1 + offset) % len(options)]


def parse_slot(row: dict[str, str]) -> int:
    topic_slug = row.get("topic_slug", "")
    match = SLOT_PATTERN.search(topic_slug)
    if match:
        return int(match.group(1))
    return max(1, int(normalize_number(row["number"])))


def distinct_choices(correct: str, pool: list[str], count: int) -> list[str]:
    results: list[str] = []
    seen = {correct}
    for item in pool:
        if item in seen:
            continue
        results.append(item)
        seen.add(item)
        if len(results) == count:
            break
    if len(results) != count:
        raise ValueError(f"보기를 {count}개 만들 수 없습니다: {correct}")
    return results


def build_choices(correct: str, distractors: list[str], seed: int) -> tuple[list[str], int]:
    options = [correct, *distractors[:3]]
    shift = seed % len(options)
    rotated = options[shift:] + options[:shift]
    return rotated, rotated.index(correct)


def build_question(
    *,
    question_id: str,
    skill: str,
    prompt: str,
    correct: str,
    distractors: list[str],
    rationale: str,
    seed: int,
) -> dict[str, Any]:
    choices, answer_index = build_choices(correct, distractors, seed)
    return {
        "id": question_id,
        "skill": skill,
        "prompt": prompt,
        "choices": choices,
        "answer_index": answer_index,
        "rationale": rationale,
    }


def join_sentences(sentences: list[str]) -> str:
    return " ".join(sentence.strip() for sentence in sentences if sentence.strip())


def format_time_phrase(raw: str) -> str:
    cleaned = raw.strip()
    lowered = cleaned.lower()
    if lowered == "morning":
        return "in the morning"
    if lowered == "evening":
        return "in the evening"
    if lowered == "afternoon":
        return "in the afternoon"
    if lowered.endswith("morning") and lowered != "morning":
        return f"on {cleaned}"
    if lowered.startswith("after ") or lowered.startswith("before ") or lowered.startswith("on "):
        return cleaned
    return f"during {cleaned}"


def selected(config: dict[str, list[str]], key: str, slot: int, offset: int = 0) -> str:
    values = config[key]
    return pick(values, slot, offset)


def load_level_data(level: str) -> dict[str, Any]:
    normalized = normalize_level(level).lower()
    return load_json_data(f"{normalized}_content.json")


def load_common_data() -> dict[str, Any]:
    return load_json_data("common.json")


def build_pack_payload(
    *,
    row: dict[str, str],
    title: str,
    passage_text: str,
    questions: list[dict[str, Any]],
    version: str = DEFAULT_VERSION,
    created_at: str | None = None,
) -> dict[str, Any]:
    normalized_grade = normalize_grade(row["grade"])
    normalized_level = normalize_level(row["level"])
    normalized_number = normalize_number(row["number"])
    return {
        "meta": {
            "pack_id": build_pack_id(normalized_grade, normalized_level, normalized_number),
            "level": normalized_level,
            "topic": title,
            "created_at": created_at or datetime.now(SEOUL).date().isoformat(),
            "version": version,
        },
        "passage": {
            "title": title,
            "text": passage_text,
            "word_count": count_words(passage_text),
        },
        "questions": questions,
    }
