"""Generate saved translation JSON files by batching multiple packs into one Gemini call."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from backend.app.services.gemini_client import generate_json_response
    from backend.app.services.model_router import select_translation_model
except ImportError as exc:  # pragma: no cover - CLI import guard
    raise SystemExit(f"[ERROR] backend Gemini helper import failed: {exc}")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_number(pack_id: str) -> int:
    try:
        return int(pack_id.split("_")[-1])
    except ValueError:
        return 0


def iter_target_packs(input_dir: Path, *, level: str, include_samples: bool) -> list[Path]:
    results: list[Path] = []
    for path in sorted(input_dir.glob("*.json")):
        payload = load_json(path)
        meta = payload.get("meta")
        if not isinstance(meta, dict):
            continue
        pack_level = str(meta.get("level") or "").upper()
        if pack_level != level.upper():
            continue

        pack_id = str(meta.get("pack_id") or "")
        if not include_samples and parse_number(pack_id) >= 9000:
            continue
        results.append(path)
    return results


def filter_pack_paths_by_ids(pack_paths: list[Path], pack_ids: set[str] | None) -> list[Path]:
    if not pack_ids:
        return pack_paths

    filtered: list[Path] = []
    for path in pack_paths:
        payload = load_json(path)
        meta = payload.get("meta")
        if not isinstance(meta, dict):
            continue
        pack_id = str(meta.get("pack_id") or "")
        if pack_id in pack_ids:
            filtered.append(path)
    return filtered


def chunked[T](items: list[T], size: int) -> list[list[T]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def build_batch_payload(packs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for pack in packs:
        meta = pack["meta"]
        passage = pack["passage"]
        questions = pack["questions"]
        payloads.append(
            {
                "pack_id": str(meta["pack_id"]),
                "title": str(passage["title"]),
                "text": str(passage["text"]),
                "questions": [
                    {
                        "id": str(question["id"]),
                        "prompt": str(question["prompt"]),
                        "choices": [str(choice) for choice in question["choices"]],
                    }
                    for question in questions
                ],
            }
        )
    return payloads


def call_batch_translation_api(batch_payload: list[dict[str, Any]], *, target_lang: str) -> dict[str, Any]:
    return generate_json_response(
        model=select_translation_model(scope="passage"),
        system_instruction=(
            "You translate English reading packs for Korean elementary learners. "
            "Translate each pack faithfully into natural, simple Korean. "
            "Do not summarize. Do not omit any pack, question, or choice. "
            "Return JSON only."
        ),
        user_prompt=(
            f"Translate every text field in these reading packs into {target_lang}.\n"
            "Keep the original structure and IDs exactly.\n"
            "Each pack must include title_translated, text_translated, and all question translations.\n"
            'Return exactly this JSON shape: {"packs":[{"pack_id":"...","title_translated":"...","text_translated":"...","questions":[{"id":"q1","prompt_translated":"...","choices_translated":["...","...","...","..."]}]}]}\n'
            f"PACKS_JSON: {json.dumps(batch_payload, ensure_ascii=False)}"
        ),
        temperature=0.1,
    )


def build_translation_file(
    *,
    original_pack: dict[str, Any],
    translated_pack: dict[str, Any],
    lang: str,
    source: str,
) -> dict[str, Any]:
    meta = original_pack["meta"]
    questions = original_pack["questions"]
    translated_questions = translated_pack.get("questions")
    if not isinstance(translated_questions, list):
        raise ValueError(f"pack_id={meta['pack_id']} 번역 응답에 questions가 없습니다.")

    translated_question_map: dict[str, dict[str, Any]] = {}
    for entry in translated_questions:
        if not isinstance(entry, dict):
            continue
        translated_question_map[str(entry.get("id") or "")] = entry

    output_questions: list[dict[str, Any]] = []
    for question in questions:
        question_id = str(question["id"])
        translated_entry = translated_question_map.get(question_id)
        if translated_entry is None:
            raise ValueError(f"pack_id={meta['pack_id']} question_id={question_id} 번역이 없습니다.")

        prompt_translated = str(translated_entry.get("prompt_translated") or "").strip()
        if not prompt_translated:
            raise ValueError(f"pack_id={meta['pack_id']} question_id={question_id} prompt 번역이 비었습니다.")

        raw_choices = translated_entry.get("choices_translated")
        if not isinstance(raw_choices, list) or len(raw_choices) != len(question["choices"]):
            raise ValueError(
                f"pack_id={meta['pack_id']} question_id={question_id} 보기 번역 수가 원본과 다릅니다."
            )

        translated_choices = [str(choice or "").strip() for choice in raw_choices]
        if any(not choice for choice in translated_choices):
            raise ValueError(f"pack_id={meta['pack_id']} question_id={question_id} 빈 보기 번역이 있습니다.")

        output_questions.append(
            {
                "id": question_id,
                "prompt_translated": prompt_translated,
                "choices_translated": translated_choices,
            }
        )

    title_translated = str(translated_pack.get("title_translated") or "").strip()
    text_translated = str(translated_pack.get("text_translated") or "").strip()
    if not title_translated or not text_translated:
        raise ValueError(f"pack_id={meta['pack_id']} 지문 번역이 비었습니다.")

    return {
        "meta": {
            "pack_id": str(meta["pack_id"]),
            "lang": lang,
            "version": str(meta.get("version") or "0.1"),
            "source": source,
        },
        "passage": {
            "title_translated": title_translated,
            "text_translated": text_translated,
        },
        "questions": output_questions,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reading ELLA 배치 Gemini 번역 생성기")
    parser.add_argument("--input-dir", default="packs", help="pack 폴더. 기본값: packs")
    parser.add_argument("--output-dir", default="translations/ko", help="출력 폴더. 기본값: translations/ko")
    parser.add_argument("--level", default="GT", help="대상 레벨. 기본값: GT")
    parser.add_argument("--lang", default="ko", help="대상 언어. 기본값: ko")
    parser.add_argument("--batch-size", type=int, default=10, help="한 번 호출에 묶을 pack 수. 기본값: 10")
    parser.add_argument("--max-batches", type=int, default=0, help="호출할 최대 묶음 수. 0이면 전체")
    parser.add_argument("--source", default="gemini_batch_seed", help="meta.source 값")
    parser.add_argument("--include-samples", action="store_true", help="9001 같은 샘플도 포함")
    parser.add_argument("--force", action="store_true", help="기존 파일도 덮어쓰기")
    parser.add_argument("--sleep-seconds", type=float, default=1.0, help="호출 사이 대기 시간")
    parser.add_argument(
        "--pack-ids",
        default="",
        help="특정 pack_id만 다시 돌릴 때 사용. 예: g1_gt_0031,g1_gt_0032",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    target_level = str(args.level).upper()
    requested_pack_ids = {item.strip() for item in str(args.pack_ids).split(",") if item.strip()}

    if not input_dir.exists():
        print(f"[ERROR] 입력 폴더를 찾을 수 없습니다: {input_dir}")
        return 1
    if args.batch_size <= 0:
        print("[ERROR] batch-size는 1 이상이어야 합니다.")
        return 1

    pack_paths = iter_target_packs(input_dir, level=target_level, include_samples=args.include_samples)
    pack_paths = filter_pack_paths_by_ids(pack_paths, requested_pack_ids or None)
    if not pack_paths:
        print(f"[ERROR] level={target_level} 대상 pack이 없습니다.")
        return 1

    batches = chunked(pack_paths, args.batch_size)
    if args.max_batches > 0:
        batches = batches[: args.max_batches]

    total_written = 0
    total_errors = 0

    for batch_index, batch_paths in enumerate(batches, start=1):
        original_packs = [load_json(path) for path in batch_paths]
        request_payload = build_batch_payload(original_packs)
        batch_label = ", ".join(str(pack["meta"]["pack_id"]) for pack in original_packs)
        print(f"[CALL {batch_index}/{len(batches)}] {batch_label}")

        try:
            response_payload = call_batch_translation_api(request_payload, target_lang=args.lang)
        except Exception as exc:
            print(f"[ERROR] batch {batch_index}: API 호출 실패 - {exc}")
            total_errors += len(batch_paths)
            continue

        translated_packs = response_payload.get("packs")
        if not isinstance(translated_packs, list):
            print(f"[ERROR] batch {batch_index}: 응답에 packs 목록이 없습니다.")
            total_errors += len(batch_paths)
            continue

        translated_map = {
            str(item.get("pack_id") or ""): item
            for item in translated_packs
            if isinstance(item, dict)
        }

        for path, original_pack in zip(batch_paths, original_packs, strict=True):
            pack_id = str(original_pack["meta"]["pack_id"])
            output_path = output_dir / f"{pack_id}.json"
            if output_path.exists() and not args.force:
                print(f"[SKIP] {output_path}")
                continue

            translated_pack = translated_map.get(pack_id)
            if translated_pack is None:
                print(f"[ERROR] pack_id={pack_id}: 응답에서 빠졌습니다.")
                total_errors += 1
                continue

            try:
                translation = build_translation_file(
                    original_pack=original_pack,
                    translated_pack=translated_pack,
                    lang=args.lang,
                    source=args.source,
                )
                write_json(output_path, translation)
                print(f"[OK] {output_path}")
                total_written += 1
            except Exception as exc:
                print(f"[ERROR] pack_id={pack_id}: {exc}")
                total_errors += 1

        if batch_index < len(batches) and args.sleep_seconds > 0:
            time.sleep(args.sleep_seconds)

    print(
        f"Batch translation summary: level={target_level}, batches={len(batches)}, "
        f"written={total_written}, errors={total_errors}"
    )
    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
