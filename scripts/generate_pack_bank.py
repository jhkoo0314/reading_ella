"""Generate Reading ELLA packs from the pack-bank CSV and validate them automatically."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

try:
    from .content.router import build_real_pack_from_row
    from .create_pack import build_pack_template, build_pack_id, normalize_number, write_json
    from .level_profiles import LEVEL_PROFILES
    from .pack_bank import DEFAULT_PLAN_PATH, PACKS_PER_LEVEL_TARGET, load_plan_rows
    from .validate_packs import ValidationResult, print_result, validate_pack
except ImportError:
    from content.router import build_real_pack_from_row
    from create_pack import build_pack_template, build_pack_id, normalize_number, write_json
    from level_profiles import LEVEL_PROFILES
    from pack_bank import DEFAULT_PLAN_PATH, PACKS_PER_LEVEL_TARGET, load_plan_rows
    from validate_packs import ValidationResult, print_result, validate_pack


def parse_levels(raw_levels: list[str] | None) -> list[str]:
    if not raw_levels:
        return list(LEVEL_PROFILES.keys())
    levels = [level.strip().upper() for level in raw_levels]
    invalid = [level for level in levels if level not in LEVEL_PROFILES]
    if invalid:
        raise ValueError(f"알 수 없는 level이 있습니다: {', '.join(invalid)}")
    return levels


def validate_plan_rows(rows: list[dict[str, str]], levels: list[str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    selected_rows = [row for row in rows if row["level"] in levels]
    topic_slugs = Counter(row["topic_slug"] for row in selected_rows if row["topic_slug"])
    pack_ids = Counter(row["pack_id"] for row in selected_rows if row["pack_id"])

    for row in selected_rows:
        expected_pack_id = build_pack_id(row["grade"], row["level"], normalize_number(row["number"]))

        if row["grade"] != "G1":
            errors.append(f"{row['pack_id'] or row['number']}: grade는 G1만 허용됩니다.")
        if row["level"] not in LEVEL_PROFILES:
            errors.append(f"{row['pack_id'] or row['number']}: level 값이 잘못되었습니다.")
        if not row["topic"]:
            errors.append(f"{row['pack_id'] or row['number']}: topic이 비어 있습니다.")
        if not row["topic_slug"]:
            errors.append(f"{row['pack_id'] or row['number']}: topic_slug가 비어 있습니다.")
        if row["pack_id"] != expected_pack_id:
            errors.append(
                f"{row['pack_id'] or row['number']}: pack_id가 규칙과 다릅니다. 기대값={expected_pack_id}"
            )

    duplicate_slugs = sorted(slug for slug, count in topic_slugs.items() if count > 1)
    duplicate_pack_ids = sorted(pack_id for pack_id, count in pack_ids.items() if count > 1)

    for slug in duplicate_slugs:
        errors.append(f"topic_slug가 중복되었습니다: {slug}")
    for pack_id in duplicate_pack_ids:
        errors.append(f"pack_id가 중복되었습니다: {pack_id}")

    counts = Counter(row["level"] for row in rows)
    for level in levels:
        if counts[level] < PACKS_PER_LEVEL_TARGET:
            warnings.append(
                f"{level} 계획 row 수가 {PACKS_PER_LEVEL_TARGET}보다 적습니다. 현재 {counts[level]}개입니다."
            )

    return errors, warnings


def select_rows(
    rows: list[dict[str, str]],
    *,
    levels: list[str],
    limit_per_level: int | None,
) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    per_level_counts: Counter[str] = Counter()

    for row in rows:
        level = row["level"]
        if level not in levels:
            continue

        if limit_per_level is not None and per_level_counts[level] >= limit_per_level:
            continue

        selected.append(row)
        per_level_counts[level] += 1

    return selected


def render_generation_result(result: ValidationResult) -> None:
    print_result(result)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reading ELLA pack bank 일괄 생성기")
    parser.add_argument(
        "--plan",
        default=str(DEFAULT_PLAN_PATH),
        help=f"pack bank CSV 경로. 기본값: {DEFAULT_PLAN_PATH}",
    )
    parser.add_argument(
        "--levels",
        nargs="*",
        help="생성할 level 목록. 비우면 GT S MGT 전체를 생성합니다.",
    )
    parser.add_argument(
        "--limit-per-level",
        type=int,
        help="레벨별 생성 개수 제한. 예: 2 라고 주면 각 레벨에서 2개씩만 생성합니다.",
    )
    parser.add_argument(
        "--output-dir",
        default="packs",
        help="생성된 pack을 저장할 폴더. 기본값: packs",
    )
    parser.add_argument(
        "--mode",
        choices=["real", "template"],
        default="real",
        help="real이면 실문항을 만들고, template이면 TODO 템플릿을 만듭니다. 기본값: real",
    )
    parser.add_argument("--force", action="store_true", help="같은 pack 파일이 있어도 덮어씁니다.")
    parser.add_argument(
        "--strict-warnings",
        action="store_true",
        help="validator 경고가 있으면 종료 코드를 1로 처리합니다.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(f"[ERROR] 계획 CSV를 찾을 수 없습니다: {plan_path}")
        return 1

    levels = parse_levels(args.levels)
    rows = load_plan_rows(plan_path)
    plan_errors, plan_warnings = validate_plan_rows(rows, levels)

    for warning in plan_warnings:
        print(f"[WARN] {warning}")
    for error in plan_errors:
        print(f"[ERROR] {error}")

    if plan_errors:
        return 1

    selected_rows = select_rows(rows, levels=levels, limit_per_level=args.limit_per_level)
    if not selected_rows:
        print("[ERROR] 생성할 row가 없습니다.")
        return 1

    output_dir = Path(args.output_dir)
    validation_results: list[ValidationResult] = []

    for row in selected_rows:
        if args.mode == "template":
            pack = build_pack_template(
                grade=row["grade"],
                level=row["level"],
                number=row["number"],
                topic=row["topic"],
            )
        else:
            pack = build_real_pack_from_row(row)
        output_path = output_dir / f"{pack['meta']['pack_id']}.json"
        write_json(output_path, pack, force=args.force)
        validation_results.append(validate_pack(output_path))

    for result in validation_results:
        render_generation_result(result)

    warning_count = sum(len(result.warnings) for result in validation_results)
    error_count = sum(len(result.errors) for result in validation_results)
    print(
        "Generation summary:"
        f" generated={len(validation_results)}, warnings={warning_count}, errors={error_count}"
    )

    if error_count > 0:
        return 1
    if args.strict_warnings and warning_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
