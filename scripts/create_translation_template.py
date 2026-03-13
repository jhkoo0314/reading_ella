"""Create a translation overlay template from an existing pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_SOURCE = "manual"


def load_pack(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"pack 파일을 찾을 수 없습니다: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_translation_template(
    pack: dict[str, object],
    *,
    lang: str,
    source: str,
    version: str | None = None,
) -> dict[str, object]:
    meta = pack.get("meta")
    questions = pack.get("questions")

    if not isinstance(meta, dict):
        raise ValueError("pack meta 정보가 없습니다.")
    if not isinstance(questions, list):
        raise ValueError("pack questions 정보가 없습니다.")

    pack_id = meta.get("pack_id")
    if not isinstance(pack_id, str) or not pack_id:
        raise ValueError("pack.meta.pack_id가 비어 있습니다.")

    resolved_version = version or str(meta.get("version") or "0.1")

    translation_questions: list[dict[str, object]] = []
    for question in questions:
        if not isinstance(question, dict):
            raise ValueError("questions 안의 항목 형식이 잘못되었습니다.")

        question_id = question.get("id")
        choices = question.get("choices")
        if not isinstance(question_id, str) or not question_id:
            raise ValueError("question id가 비어 있습니다.")
        if not isinstance(choices, list):
            raise ValueError(f"{question_id}의 choices 형식이 잘못되었습니다.")

        translation_questions.append(
            {
                "id": question_id,
                "prompt_translated": "",
                "choices_translated": ["" for _ in choices],
            }
        )

    return {
        "meta": {
            "pack_id": pack_id,
            "lang": lang,
            "version": resolved_version,
            "source": source,
        },
        "passage": {
            "title_translated": "",
            "text_translated": "",
        },
        "questions": translation_questions,
    }


def write_json(path: Path, payload: dict[str, object], *, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"이미 파일이 있습니다: {path}. 덮어쓰려면 --force를 사용하세요.")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reading ELLA 번역 템플릿 생성기")
    parser.add_argument("--pack", required=True, help="원본 pack 파일 경로. 예: packs/g1_gt_0001.json")
    parser.add_argument("--lang", default="ko", help="번역 언어 코드. 기본값: ko")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="번역 출처 표기. 기본값: manual")
    parser.add_argument("--version", help="번역 템플릿 버전. 비우면 pack 버전을 따라갑니다.")
    parser.add_argument("--output-dir", help="출력 폴더. 비우면 translations/{lang}를 사용합니다.")
    parser.add_argument("--force", action="store_true", help="같은 파일이 있어도 덮어씁니다.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pack_path = Path(args.pack)
    pack = load_pack(pack_path)
    translation = build_translation_template(
        pack,
        lang=args.lang,
        source=args.source,
        version=args.version,
    )
    output_dir = Path(args.output_dir) if args.output_dir else Path("translations") / args.lang
    output_path = output_dir / f"{translation['meta']['pack_id']}.json"
    write_json(output_path, translation, force=args.force)
    print(f"Translation template created: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
