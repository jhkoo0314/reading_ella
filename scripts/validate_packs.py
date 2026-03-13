"""Validate Reading ELLA pack files against schema and level rules."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from .level_profiles import LEVEL_PROFILES
except ImportError:
    from level_profiles import LEVEL_PROFILES


PACK_ID_PATTERN = re.compile(r"^g1_(gt|s|mgt)_\d{4}$")
WORD_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
SENTENCE_SPLIT_PATTERN = re.compile(r"[.!?]+")
CHOICE_WORD_WARNING_LIMIT = 12
DEFAULT_INPUTS = ("packs",)
ALLOWED_SKILLS = sorted({skill for profile in LEVEL_PROFILES.values() for skill in profile["skills"]})
PLACEHOLDER_PATTERN = re.compile(r"\bTODO\b")


@dataclass
class ValidationResult:
    path: Path
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.errors:
            return "ERROR"
        if self.warnings:
            return "WARN"
        return "OK"

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


def count_words(text: str) -> int:
    return len(WORD_PATTERN.findall(text))


def count_sentences(text: str) -> int:
    return len([part for part in SENTENCE_SPLIT_PATTERN.split(text) if part.strip()])


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require_dict(value: Any, field_name: str, result: ValidationResult) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        result.add_error(f"{field_name}는 객체(dict)여야 합니다.")
        return None
    return value


def require_list(value: Any, field_name: str, result: ValidationResult) -> list[Any] | None:
    if not isinstance(value, list):
        result.add_error(f"{field_name}는 배열(list)이어야 합니다.")
        return None
    return value


def require_string(container: dict[str, Any], key: str, field_name: str, result: ValidationResult) -> str | None:
    value = container.get(key)
    if not isinstance(value, str):
        result.add_error(f"{field_name}는 문자열이어야 합니다.")
        return None
    if not value.strip():
        result.add_error(f"{field_name}는 비어 있으면 안 됩니다.")
        return None
    return value.strip()


def require_int(container: dict[str, Any], key: str, field_name: str, result: ValidationResult) -> int | None:
    value = container.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        result.add_error(f"{field_name}는 정수여야 합니다.")
        return None
    return value


def contains_placeholder_text(value: str) -> bool:
    normalized = value.strip()
    if not normalized:
        return False
    return PLACEHOLDER_PATTERN.search(normalized) is not None


def validate_meta(meta: dict[str, Any], result: ValidationResult) -> tuple[str | None, str | None]:
    pack_id = require_string(meta, "pack_id", "meta.pack_id", result)
    level = require_string(meta, "level", "meta.level", result)
    topic = require_string(meta, "topic", "meta.topic", result)
    require_string(meta, "created_at", "meta.created_at", result)
    require_string(meta, "version", "meta.version", result)

    if pack_id and not PACK_ID_PATTERN.fullmatch(pack_id):
        result.add_warning("meta.pack_id는 권장 형식 g1_{level}_{number}와 다릅니다. 예: g1_gt_0001")

    if level and level not in LEVEL_PROFILES:
        result.add_error("meta.level은 GT, S, MGT 중 하나여야 합니다.")
    elif pack_id and level and not pack_id.startswith(f"g1_{level.lower()}_"):
        result.add_warning("meta.pack_id 안의 level 표기와 meta.level 값이 서로 다릅니다.")

    if topic and contains_placeholder_text(topic):
        result.add_error("meta.topic에 TODO 같은 템플릿 문구가 남아 있습니다.")

    return pack_id, level


def validate_passage(
    passage: dict[str, Any],
    result: ValidationResult,
    profile: dict[str, Any] | None,
) -> None:
    title = require_string(passage, "title", "passage.title", result)
    text = require_string(passage, "text", "passage.text", result)
    word_count = require_int(passage, "word_count", "passage.word_count", result)

    if word_count is not None and word_count < 0:
        result.add_error("passage.word_count는 0 이상이어야 합니다.")

    if title and contains_placeholder_text(title):
        result.add_error("passage.title에 TODO 같은 템플릿 문구가 남아 있습니다.")
    if text and contains_placeholder_text(text):
        result.add_error("passage.text에 TODO 같은 템플릿 문구가 남아 있습니다.")

    if text is None or profile is None:
        return

    sentence_count = count_sentences(text)
    validator = profile.get("validator", {})
    warn_word_count = isinstance(validator, dict) and validator.get("warn_if_word_count_outside_range", False)
    warn_sentence_count = isinstance(validator, dict) and validator.get("warn_if_sentence_count_outside_range", False)

    if word_count is not None and warn_word_count:
        min_words = int(profile["word_count_min"])
        max_words = int(profile["word_count_max"])
        if not min_words <= word_count <= max_words:
            result.add_warning(
                f"passage.word_count={word_count} 는 {profile['level']} 권장 범위 {min_words}-{max_words}를 벗어납니다."
            )

    if warn_sentence_count:
        min_sentences = int(profile["sentence_count_min"])
        max_sentences = int(profile["sentence_count_max"])
        if not min_sentences <= sentence_count <= max_sentences:
            result.add_warning(
                f"지문 문장 수={sentence_count} 는 {profile['level']} 권장 범위 {min_sentences}-{max_sentences}를 벗어납니다."
            )


def validate_questions(
    questions: list[Any],
    result: ValidationResult,
    profile: dict[str, Any] | None,
) -> None:
    if len(questions) != 6:
        result.add_error(f"questions 길이는 반드시 6이어야 합니다. 현재 {len(questions)}개입니다.")

    seen_ids: set[str] = set()
    actual_skills: list[str] = []

    for index, question_value in enumerate(questions, start=1):
        field_prefix = f"questions[{index - 1}]"
        question = require_dict(question_value, field_prefix, result)
        if question is None:
            continue

        question_id = require_string(question, "id", f"{field_prefix}.id", result)
        skill = require_string(question, "skill", f"{field_prefix}.skill", result)
        prompt = require_string(question, "prompt", f"{field_prefix}.prompt", result)
        answer_index = require_int(question, "answer_index", f"{field_prefix}.answer_index", result)

        if question_id:
            if question_id in seen_ids:
                result.add_error(f"{field_prefix}.id={question_id} 가 중복되었습니다.")
            seen_ids.add(question_id)

        if skill:
            if skill not in ALLOWED_SKILLS:
                result.add_error(
                    f"{field_prefix}.skill={skill} 는 허용되지 않습니다. 허용값: {', '.join(ALLOWED_SKILLS)}"
                )
            else:
                actual_skills.append(skill)

        if prompt and contains_placeholder_text(prompt):
            result.add_error(f"{field_prefix}.prompt에 TODO 같은 템플릿 문구가 남아 있습니다.")

        choices_value = question.get("choices")
        choices = require_list(choices_value, f"{field_prefix}.choices", result)
        if choices is not None:
            if len(choices) != 4:
                result.add_error(f"{field_prefix}.choices 길이는 반드시 4여야 합니다. 현재 {len(choices)}개입니다.")

            cleaned_choices: list[str] = []
            for choice_index, choice in enumerate(choices, start=1):
                choice_field = f"{field_prefix}.choices[{choice_index - 1}]"
                if not isinstance(choice, str):
                    result.add_error(f"{choice_field}는 문자열이어야 합니다.")
                    continue
                if not choice.strip():
                    result.add_error(f"{choice_field}는 비어 있으면 안 됩니다.")
                    continue
                cleaned_choice = choice.strip()
                cleaned_choices.append(cleaned_choice)
                if contains_placeholder_text(cleaned_choice):
                    result.add_error(f"{choice_field}에 TODO 같은 템플릿 문구가 남아 있습니다.")
                if count_words(cleaned_choice) > CHOICE_WORD_WARNING_LIMIT:
                    result.add_warning(
                        f"{choice_field}가 너무 깁니다. 보기 문장을 더 짧게 다듬는 것을 권장합니다."
                    )

            if len(cleaned_choices) == len(choices) and len(set(cleaned_choices)) != len(cleaned_choices):
                result.add_warning(f"{field_prefix}.choices 안에 완전히 같은 보기가 있습니다.")

        if answer_index is not None and not 0 <= answer_index <= 3:
            result.add_error(f"{field_prefix}.answer_index는 0 이상 3 이하여야 합니다.")

        rationale = question.get("rationale")
        if rationale is not None and not isinstance(rationale, str):
            result.add_error(f"{field_prefix}.rationale은 문자열이어야 합니다.")
        elif isinstance(rationale, str) and contains_placeholder_text(rationale):
            result.add_error(f"{field_prefix}.rationale에 TODO 같은 템플릿 문구가 남아 있습니다.")

    if profile is None:
        return

    expected_skills = profile.get("skills")
    validator = profile.get("validator", {})
    if (
        isinstance(expected_skills, list)
        and len(questions) == len(expected_skills)
        and len(actual_skills) == len(expected_skills)
        and isinstance(validator, dict)
        and validator.get("enforce_skill_distribution", False)
        and actual_skills != expected_skills
    ):
        result.add_error(
            f"{profile['level']} 레벨 skill 순서가 다릅니다. 기대값={expected_skills}, 실제값={actual_skills}"
        )


def validate_pack(path: Path) -> ValidationResult:
    result = ValidationResult(path=path)

    try:
        payload = read_json(path)
    except FileNotFoundError:
        result.add_error("파일을 찾을 수 없습니다.")
        return result
    except json.JSONDecodeError as exc:
        result.add_error(f"JSON 형식이 잘못되었습니다. line={exc.lineno}, column={exc.colno}")
        return result

    root = require_dict(payload, "root", result)
    if root is None:
        return result

    meta = require_dict(root.get("meta"), "meta", result)
    passage = require_dict(root.get("passage"), "passage", result)
    questions = require_list(root.get("questions"), "questions", result)

    level: str | None = None
    profile: dict[str, Any] | None = None

    if meta is not None:
        _, level = validate_meta(meta, result)
        if level in LEVEL_PROFILES:
            profile = LEVEL_PROFILES[level]

    if passage is not None:
        validate_passage(passage, result, profile)

    if questions is not None:
        validate_questions(questions, result, profile)

    return result


def collect_pack_files(raw_paths: list[str], recursive: bool) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    errors: list[str] = []

    for raw_path in raw_paths:
        path = Path(raw_path)
        if not path.exists():
            errors.append(f"경로를 찾을 수 없습니다: {path}")
            continue

        if path.is_file():
            files.append(path)
            continue

        iterator = path.rglob("*.json") if recursive else path.glob("*.json")
        matched = sorted(item for item in iterator if item.is_file())
        if not matched:
            errors.append(f"검사할 JSON pack 파일이 없습니다: {path}")
            continue
        files.extend(matched)

    unique_files = sorted({file.resolve(): file for file in files}.values())
    return unique_files, errors


def print_result(result: ValidationResult) -> None:
    print(f"[{result.status}] {result.path}")
    for error in result.errors:
        print(f"  - ERROR: {error}")
    for warning in result.warnings:
        print(f"  - WARN: {warning}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reading ELLA pack 검증기")
    parser.add_argument(
        "paths",
        nargs="*",
        default=list(DEFAULT_INPUTS),
        help="검사할 pack 파일 또는 폴더. 비우면 packs 폴더를 검사합니다.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="폴더를 재귀적으로 검사합니다.",
    )
    parser.add_argument(
        "--strict-warnings",
        action="store_true",
        help="경고가 있어도 종료 코드를 1로 처리합니다.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    files, collection_errors = collect_pack_files(args.paths, recursive=args.recursive)

    for message in collection_errors:
        print(f"[ERROR] {message}")

    if not files:
        return 1

    results = [validate_pack(path) for path in files]
    for result in results:
        print_result(result)

    error_count = sum(len(result.errors) for result in results) + len(collection_errors)
    warning_count = sum(len(result.warnings) for result in results)
    ok_files = sum(1 for result in results if result.status == "OK")

    print(
        "Summary:"
        f" files={len(results)}, ok={ok_files},"
        f" files_with_errors={sum(1 for result in results if result.errors)},"
        f" warnings={warning_count}, errors={error_count}"
    )

    if error_count > 0:
        return 1
    if args.strict_warnings and warning_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
