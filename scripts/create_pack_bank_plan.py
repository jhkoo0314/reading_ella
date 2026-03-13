"""Create a 300-row pack-bank planning CSV for GT, S, and MGT."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from .pack_bank import DEFAULT_PLAN_PATH, PACKS_PER_LEVEL_TARGET, build_plan_rows, write_plan_csv
except ImportError:
    from pack_bank import DEFAULT_PLAN_PATH, PACKS_PER_LEVEL_TARGET, build_plan_rows, write_plan_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reading ELLA pack bank 계획표 생성기")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_PLAN_PATH),
        help=f"출력 CSV 경로. 기본값: {DEFAULT_PLAN_PATH}",
    )
    parser.add_argument(
        "--packs-per-level",
        type=int,
        default=PACKS_PER_LEVEL_TARGET,
        help=f"레벨별 계획 row 수. 기본값: {PACKS_PER_LEVEL_TARGET}",
    )
    parser.add_argument("--force", action="store_true", help="같은 파일이 있어도 덮어씁니다.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = build_plan_rows(packs_per_level=args.packs_per_level)
    output_path = Path(args.output)
    write_plan_csv(output_path, rows, force=args.force)

    per_level = args.packs_per_level
    print(
        f"Pack bank plan created: {output_path} "
        f"(GT {per_level}, S {per_level}, MGT {per_level}, total {len(rows)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
