"""Generate local Korean seed translations for Reading ELLA packs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .translation_rules import build_seed_translation
    from .validate_packs import validate_pack
except ImportError:
    from translation_rules import build_seed_translation
    from validate_packs import validate_pack


def load_pack(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, object], *, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"이미 파일이 있습니다: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def iter_pack_paths(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    return sorted(path for path in input_path.glob("*.json") if path.is_file())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reading ELLA 로컬 번역 초안 일괄 생성기")
    parser.add_argument("input", nargs="?", default="packs", help="pack 파일 또는 폴더. 기본값: packs")
    parser.add_argument("--lang", default="ko", help="출력 언어 코드. 현재는 ko만 권장합니다.")
    parser.add_argument("--output-dir", help="출력 폴더. 비우면 translations/{lang}")
    parser.add_argument("--source", default="rule_based_seed", help="meta.source 값. 기본값: rule_based_seed")
    parser.add_argument("--force", action="store_true", help="이미 있는 파일도 덮어씁니다.")
    parser.add_argument(
        "--refresh-generated",
        action="store_true",
        help="이미 있는 파일 중 meta.source가 현재 source와 같은 자동 생성본만 다시 만듭니다.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] 입력 경로를 찾을 수 없습니다: {input_path}")
        return 1

    output_dir = Path(args.output_dir) if args.output_dir else Path("translations") / args.lang
    pack_paths = iter_pack_paths(input_path)
    if not pack_paths:
        print("[ERROR] 번역할 pack 파일이 없습니다.")
        return 1

    generated = 0
    skipped = 0
    errors = 0

    for pack_path in pack_paths:
        validation = validate_pack(pack_path)
        if validation.errors:
            print(f"[SKIP] {pack_path.name}: pack 오류가 있어 번역을 만들지 않습니다.")
            skipped += 1
            continue

        pack = load_pack(pack_path)
        pack_id = str(pack["meta"]["pack_id"])
        output_path = output_dir / f"{pack_id}.json"
        if output_path.exists():
            if args.force:
                pass
            elif args.refresh_generated:
                existing_translation = load_pack(output_path)
                existing_meta = existing_translation.get("meta")
                existing_source = str(existing_meta.get("source") or "") if isinstance(existing_meta, dict) else ""
                if existing_source != args.source:
                    print(f"[SKIP] {output_path}")
                    skipped += 1
                    continue
            else:
                print(f"[SKIP] {output_path}")
                skipped += 1
                continue

        try:
            translation = build_seed_translation(pack, lang=args.lang, source=args.source)
            write_json(output_path, translation, force=args.force or args.refresh_generated)
            print(f"[OK] {output_path}")
            generated += 1
        except Exception as exc:  # pragma: no cover - CLI safety
            print(f"[ERROR] {pack_path.name}: {exc}")
            errors += 1

    print(f"Translation summary: generated={generated}, skipped={skipped}, errors={errors}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
