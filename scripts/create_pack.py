"""Create a level-aware Reading ELLA pack template."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from .level_profiles import LEVEL_PROFILES
except ImportError:
    from level_profiles import LEVEL_PROFILES


SEOUL = ZoneInfo("Asia/Seoul")
DEFAULT_VERSION = "0.1"


def normalize_grade(grade: str) -> str:
    normalized = grade.strip().upper()
    if normalized != "G1":
        raise ValueError("v1에서는 grade가 G1만 허용됩니다.")
    return normalized


def normalize_level(level: str) -> str:
    normalized = level.strip().upper()
    if normalized not in LEVEL_PROFILES:
        raise ValueError("level은 GT, S, MGT 중 하나여야 합니다.")
    return normalized


def normalize_number(number: str) -> str:
    cleaned = number.strip()
    if not cleaned.isdigit():
        raise ValueError("number는 숫자만 입력해야 합니다. 예: 0001")
    if len(cleaned) > 4:
        raise ValueError("number는 최대 4자리까지 허용합니다.")
    return cleaned.zfill(4)


def build_pack_id(grade: str, level: str, number: str) -> str:
    return f"{grade.lower()}_{level.lower()}_{number}"


def build_question_template(index: int, skill: str, explanation_depth: str) -> dict[str, object]:
    readable_skill = skill.replace("_", " ")
    return {
        "id": f"q{index}",
        "skill": skill,
        "prompt": f"TODO: Write a {readable_skill} question for this passage.",
        "choices": [
            "TODO: Choice A",
            "TODO: Choice B",
            "TODO: Choice C",
            "TODO: Choice D",
        ],
        "answer_index": 0,
        "rationale": f"TODO: Add a {explanation_depth} rationale.",
    }


def build_passage_placeholder(topic: str, sentence_count: int) -> str:
    return " ".join(
        f"TODO sentence {index} about {topic.strip()}."
        for index in range(1, sentence_count + 1)
    )


def build_pack_template(
    *,
    grade: str,
    level: str,
    number: str,
    topic: str,
    version: str = DEFAULT_VERSION,
    created_at: str | None = None,
) -> dict[str, object]:
    normalized_grade = normalize_grade(grade)
    normalized_level = normalize_level(level)
    normalized_number = normalize_number(number)
    profile = LEVEL_PROFILES[normalized_level]

    skills = profile["skills"]
    if not isinstance(skills, list) or len(skills) != 6:
        raise ValueError(f"{normalized_level} 레벨 skills 설정이 잘못되었습니다.")

    pack_id = build_pack_id(normalized_grade, normalized_level, normalized_number)
    created_value = created_at or datetime.now(SEOUL).date().isoformat()
    target_word_count = (int(profile["word_count_min"]) + int(profile["word_count_max"])) // 2
    target_sentence_count = int(profile["sentence_count_min"])
    set_number = int(normalized_number)

    return {
        "meta": {
            "pack_id": pack_id,
            "level": normalized_level,
            "topic": topic.strip(),
            "created_at": created_value,
            "version": version,
        },
        "passage": {
            "title": f"{normalized_level} Set #{set_number}",
            "text": build_passage_placeholder(topic, target_sentence_count),
            "word_count": target_word_count,
        },
        "questions": [
            build_question_template(index=index, skill=skill, explanation_depth=str(profile["explanation_depth"]))
            for index, skill in enumerate(skills, start=1)
        ],
    }


def write_json(path: Path, payload: dict[str, object], *, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"이미 파일이 있습니다: {path}. 덮어쓰려면 --force를 사용하세요.")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reading ELLA pack 템플릿 생성기")
    parser.add_argument("--grade", default="G1", help="학년 코드. v1에서는 G1만 사용합니다.")
    parser.add_argument("--level", required=True, choices=sorted(LEVEL_PROFILES.keys()))
    parser.add_argument("--number", required=True, help="세트 번호. 예: 0001")
    parser.add_argument("--topic", required=True, help="문제 주제")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="pack 버전")
    parser.add_argument("--created-at", help="생성일. 비우면 오늘 날짜를 사용합니다. 예: 2026-03-13")
    parser.add_argument("--output-dir", default="packs", help="출력 폴더. 기본값: packs")
    parser.add_argument("--force", action="store_true", help="같은 파일이 있어도 덮어씁니다.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pack = build_pack_template(
        grade=args.grade,
        level=args.level,
        number=args.number,
        topic=args.topic,
        version=args.version,
        created_at=args.created_at,
    )
    output_path = Path(args.output_dir) / f"{pack['meta']['pack_id']}.json"
    write_json(output_path, pack, force=args.force)
    print(f"Pack template created: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
