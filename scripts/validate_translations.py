"""Validate Reading ELLA translation overlay files."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_INPUTS = ("translations/ko",)


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


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def print_result(result: ValidationResult) -> None:
    print(f"[{result.status}] {result.path}")
    for error in result.errors:
        print(f"  - ERROR: {error}")
    for warning in result.warnings:
        print(f"  - WARN: {warning}")


def _require_dict(value: Any, field_name: str, result: ValidationResult) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        result.add_error(f"{field_name}는 객체(dict)여야 합니다.")
        return None
    return value


def _require_list(value: Any, field_name: str, result: ValidationResult) -> list[Any] | None:
    if not isinstance(value, list):
        result.add_error(f"{field_name}는 배열(list)이어야 합니다.")
        return None
    return value


def _require_string(container: dict[str, Any], key: str, field_name: str, result: ValidationResult) -> str | None:
    value = container.get(key)
    if not isinstance(value, str):
        result.add_error(f"{field_name}는 문자열이어야 합니다.")
        return None
    return value.strip()


def _pack_path_for_translation(path: Path, pack_id: str) -> Path:
    return Path("packs") / f"{pack_id}.json"


def validate_translation(path: Path) -> ValidationResult:
    result = ValidationResult(path=path)
    try:
        payload = read_json(path)
    except FileNotFoundError:
        result.add_error("파일을 찾을 수 없습니다.")
        return result
    except json.JSONDecodeError as exc:
        result.add_error(f"JSON 형식이 잘못되었습니다: {exc}")
        return result

    root = _require_dict(payload, "root", result)
    if root is None:
        return result

    meta = _require_dict(root.get("meta"), "meta", result)
    passage = _require_dict(root.get("passage"), "passage", result)
    questions = _require_list(root.get("questions"), "questions", result)
    if meta is None or passage is None or questions is None:
        return result

    pack_id = _require_string(meta, "pack_id", "meta.pack_id", result)
    lang = _require_string(meta, "lang", "meta.lang", result)
    version = _require_string(meta, "version", "meta.version", result)
    source = _require_string(meta, "source", "meta.source", result)

    if pack_id and path.stem != pack_id:
        result.add_error("파일명과 meta.pack_id가 다릅니다.")
    if lang and path.parent.name != lang:
        result.add_error("폴더명과 meta.lang이 다릅니다.")
    if source == "":
        result.add_warning("meta.source가 비어 있습니다.")

    title_translated = _require_string(passage, "title_translated", "passage.title_translated", result)
    text_translated = _require_string(passage, "text_translated", "passage.text_translated", result)
    if title_translated == "" and text_translated == "":
        result.add_warning("지문 번역이 비어 있습니다.")

    if not pack_id:
        return result

    pack_path = _pack_path_for_translation(path, pack_id)
    if not pack_path.exists():
        result.add_error(f"원본 pack 파일이 없습니다: {pack_path}")
        return result

    pack_payload = read_json(pack_path)
    pack_meta = pack_payload.get("meta")
    pack_questions = pack_payload.get("questions")
    if not isinstance(pack_meta, dict) or not isinstance(pack_questions, list):
        result.add_error("원본 pack 구조가 잘못되었습니다.")
        return result

    if version and str(pack_meta.get("version") or "") != version:
        result.add_warning("meta.version이 pack 버전과 다릅니다.")

    pack_question_ids: dict[str, dict[str, Any]] = {}
    for question in pack_questions:
        if isinstance(question, dict):
            question_id = str(question.get("id") or "").strip()
            if question_id:
                pack_question_ids[question_id] = question

    seen_ids: set[str] = set()
    any_filled_question = False
    for index, question_value in enumerate(questions):
        field_prefix = f"questions[{index}]"
        question = _require_dict(question_value, field_prefix, result)
        if question is None:
            continue

        question_id = _require_string(question, "id", f"{field_prefix}.id", result)
        if question_id is None:
            continue
        if question_id in seen_ids:
            result.add_error(f"{field_prefix}.id={question_id} 가 중복되었습니다.")
            continue
        seen_ids.add(question_id)

        pack_question = pack_question_ids.get(question_id)
        if pack_question is None:
            result.add_error(f"{field_prefix}.id={question_id} 는 원본 pack에 없습니다.")
            continue

        prompt_translated = _require_string(question, "prompt_translated", f"{field_prefix}.prompt_translated", result)
        choices_translated = _require_list(question.get("choices_translated"), f"{field_prefix}.choices_translated", result)
        if choices_translated is None:
            continue

        original_choices = pack_question.get("choices")
        if not isinstance(original_choices, list):
            result.add_error(f"{field_prefix}: 원본 pack choices 형식이 잘못되었습니다.")
            continue
        if len(choices_translated) != len(original_choices):
            result.add_error(f"{field_prefix}.choices_translated 길이가 원본 보기 수와 다릅니다.")

        normalized_choices: list[str] = []
        for choice_index, translated_choice in enumerate(choices_translated):
            choice_field = f"{field_prefix}.choices_translated[{choice_index}]"
            if not isinstance(translated_choice, str):
                result.add_error(f"{choice_field}는 문자열이어야 합니다.")
                continue
            normalized_choices.append(translated_choice.strip())

        if normalized_choices:
            non_empty_choices = [choice for choice in normalized_choices if choice]
            if non_empty_choices and len(non_empty_choices) != len(normalized_choices):
                result.add_error(f"{field_prefix}.choices_translated는 비우려면 전체를 비우고, 채우려면 전체를 채워야 합니다.")

        if (prompt_translated or "").strip() or any(choice.strip() for choice in normalized_choices):
            any_filled_question = True

    if not any_filled_question and title_translated == "" and text_translated == "":
        result.add_warning("이 번역 파일은 사실상 비어 있습니다.")

    missing_question_ids = sorted(set(pack_question_ids) - seen_ids)
    if missing_question_ids:
        result.add_warning(f"번역 파일에 없는 문항이 있습니다: {', '.join(missing_question_ids)}")

    return result


def iter_input_paths(raw_inputs: list[str]) -> list[Path]:
    paths: list[Path] = []
    for raw_input in raw_inputs:
        path = Path(raw_input)
        if not path.exists():
            raise FileNotFoundError(f"입력 경로를 찾을 수 없습니다: {path}")
        if path.is_file():
            paths.append(path)
            continue
        paths.extend(sorted(file_path for file_path in path.glob("*.json") if file_path.is_file()))
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reading ELLA 번역 오버레이 검사기")
    parser.add_argument("inputs", nargs="*", default=list(DEFAULT_INPUTS), help="검사할 파일 또는 폴더")
    parser.add_argument("--strict-warnings", action="store_true", help="경고가 있어도 종료 코드를 1로 처리합니다.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        paths = iter_input_paths(args.inputs)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}")
        return 1

    if not paths:
        print("[ERROR] 검사할 translation JSON 파일이 없습니다.")
        return 1

    results = [validate_translation(path) for path in paths]
    for result in results:
        print_result(result)

    error_count = sum(len(result.errors) for result in results)
    warning_count = sum(len(result.warnings) for result in results)
    ok_count = sum(1 for result in results if result.status == "OK")
    print(
        "Translation validation summary:"
        f" files={len(results)}, ok={ok_count}, warnings={warning_count}, errors={error_count}"
    )

    if error_count:
        return 1
    if args.strict_warnings and warning_count:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
