"""Create or refresh a manual review CSV for pack files."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

try:
    from .validate_packs import collect_pack_files, validate_pack
except ImportError:
    from validate_packs import collect_pack_files, validate_pack


MANUAL_COLUMNS = [
    "reviewer",
    "review_round",
    "review_status",
    "sentence_level_ok",
    "choice_naturalness_ok",
    "rationale_korean_ok",
    "duplicate_risk",
    "final_decision",
    "notes",
]
SHEET_COLUMNS = [
    "pack_path",
    "pack_id",
    "level",
    "topic",
    "passage_title",
    "auto_status",
    "auto_error_count",
    "auto_warning_count",
    *MANUAL_COLUMNS,
]


def load_existing_manual_values(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            return {}

        existing: dict[str, dict[str, str]] = {}
        for row in reader:
            pack_id = (row.get("pack_id") or "").strip()
            if not pack_id:
                continue
            existing[pack_id] = {column: (row.get(column) or "").strip() for column in MANUAL_COLUMNS}
        return existing


def safe_read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def build_row(path: Path, manual_values: dict[str, str] | None = None) -> dict[str, str]:
    validation = validate_pack(path)
    payload = safe_read_json(path) or {}
    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    passage = payload.get("passage") if isinstance(payload.get("passage"), dict) else {}

    row = {
        "pack_path": str(path),
        "pack_id": str(meta.get("pack_id") or path.stem),
        "level": str(meta.get("level") or ""),
        "topic": str(meta.get("topic") or ""),
        "passage_title": str(passage.get("title") or ""),
        "auto_status": validation.status,
        "auto_error_count": str(len(validation.errors)),
        "auto_warning_count": str(len(validation.warnings)),
    }

    for column in MANUAL_COLUMNS:
        row[column] = (manual_values or {}).get(column, "")

    return row


def get_pack_id_from_payload(path: Path) -> str:
    payload = safe_read_json(path) or {}
    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    pack_id = meta.get("pack_id")
    if isinstance(pack_id, str) and pack_id.strip():
        return pack_id.strip()
    return path.stem


def write_sheet(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=SHEET_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reading ELLA 수동 검수 시트 생성기")
    parser.add_argument(
        "paths",
        nargs="*",
        default=["packs"],
        help="검수 시트를 만들 pack 파일 또는 폴더. 비우면 packs 폴더를 사용합니다.",
    )
    parser.add_argument(
        "--output",
        default="packs/manual_review_sheet.csv",
        help="출력 CSV 경로. 기본값: packs/manual_review_sheet.csv",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="폴더를 재귀적으로 검사합니다.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    files, collection_errors = collect_pack_files(args.paths, recursive=args.recursive)

    for message in collection_errors:
        print(f"[WARN] {message}")

    if not files:
        print("[ERROR] 검수 시트를 만들 JSON pack 파일이 없습니다.")
        return 1

    existing_manual_values = load_existing_manual_values(output_path)
    rows = []
    for path in files:
        pack_id = get_pack_id_from_payload(path)
        rows.append(build_row(path, manual_values=existing_manual_values.get(pack_id)))
    rows.sort(key=lambda row: row["pack_id"])
    write_sheet(output_path, rows)
    print(f"Manual review sheet created: {output_path} (rows={len(rows)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
