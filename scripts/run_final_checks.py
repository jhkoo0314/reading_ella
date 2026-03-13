"""Run final Reading ELLA checks for frontend build, packs, and backend flows."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKS_DIR = PROJECT_ROOT / "packs"
TRANSLATIONS_DIR = PROJECT_ROOT / "translations"
BACKEND_DATA_DIR = PROJECT_ROOT / "backend" / "data"
DEFAULT_DB_PATH = BACKEND_DATA_DIR / "final_check_test.db"
PNPM_COMMAND = "pnpm.cmd" if os.name == "nt" else "pnpm"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.validate_packs import validate_pack
from scripts.validate_translations import validate_translation


class CheckFailed(RuntimeError):
    """Raised when one final-check step fails."""


def log(message: str) -> None:
    print(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailed(message)


def run_command(command: list[str], *, label: str) -> None:
    log(f"[RUN] {label}: {' '.join(command)}")
    completed = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    if completed.returncode != 0:
        raise CheckFailed(f"{label} 실패 (exit={completed.returncode})")
    log(f"[OK] {label}")


def load_pack_payload(pack_path: Path) -> dict[str, object]:
    return json.loads(pack_path.read_text(encoding="utf-8"))


def count_pack_levels() -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in sorted(PACKS_DIR.glob("*.json")):
        payload = load_pack_payload(path)
        meta = payload.get("meta")
        if isinstance(meta, dict):
            level = str(meta.get("level") or "").upper()
            if level:
                counts[level] += 1
    return counts


def validate_all_packs() -> None:
    results = [validate_pack(path) for path in sorted(PACKS_DIR.glob("*.json"))]
    require(results, "검사할 pack JSON 파일이 없습니다.")

    error_count = sum(len(result.errors) for result in results)
    warning_count = sum(len(result.warnings) for result in results)
    require(error_count == 0, f"pack validator 오류가 {error_count}개 있습니다.")
    require(warning_count == 0, f"pack validator 경고가 {warning_count}개 있습니다.")
    log(f"[OK] pack validator 통과 ({len(results)} files)")


def validate_all_translations() -> None:
    translation_paths = sorted((TRANSLATIONS_DIR / "ko").glob("*.json"))
    require(translation_paths, "검사할 translation JSON 파일이 없습니다.")

    results = [validate_translation(path) for path in translation_paths]
    error_count = sum(len(result.errors) for result in results)
    warning_count = sum(len(result.warnings) for result in results)
    require(error_count == 0, f"translation validator 오류가 {error_count}개 있습니다.")
    log(f"[OK] translation validator 통과 ({len(results)} files, warnings={warning_count})")


def build_wrong_answers(pack_id: str, *, packs_dir: Path) -> list[dict[str, object]]:
    payload = load_pack_payload(packs_dir / f"{pack_id}.json")
    questions = payload.get("questions")
    require(isinstance(questions, list), f"{pack_id} questions 형식이 잘못되었습니다.")

    answers: list[dict[str, object]] = []
    for question in questions:
        require(isinstance(question, dict), f"{pack_id} question 항목 형식이 잘못되었습니다.")
        question_id = str(question.get("id") or "").strip()
        correct_index = int(question.get("answer_index"))
        require(question_id, f"{pack_id} question_id가 비어 있습니다.")
        answers.append(
            {
                "question_id": question_id,
                "chosen_index": (correct_index + 1) % 4,
            }
        )
    return answers


@contextmanager
def temporary_env(overrides: dict[str, str | None]) -> Iterator[None]:
    original_values: dict[str, str | None] = {key: os.environ.get(key) for key in overrides}

    for key, value in overrides.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

    try:
        yield
    finally:
        for key, original_value in original_values.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value


def reset_backend_settings() -> None:
    from backend.app.core.config import get_settings

    get_settings.cache_clear()

    try:
        import backend.app.main as main_module
    except ModuleNotFoundError:
        return

    main_module.settings = get_settings()


@contextmanager
def backend_env(overrides: dict[str, str | None]) -> Iterator[None]:
    with temporary_env(overrides):
        reset_backend_settings()
        try:
            yield
        finally:
            reset_backend_settings()


def create_no_rationale_pack_dir() -> Path:
    temp_root = Path(tempfile.mkdtemp(prefix="final-check-", dir=BACKEND_DATA_DIR))
    temp_packs_dir = temp_root / "packs"
    temp_packs_dir.mkdir(parents=True, exist_ok=True)

    source_path = PACKS_DIR / "g1_gt_9001.json"
    payload = load_pack_payload(source_path)
    questions = payload.get("questions")
    require(isinstance(questions, list) and questions, "g1_gt_9001 questions 형식이 잘못되었습니다.")
    first_question = questions[0]
    require(isinstance(first_question, dict), "g1_gt_9001 첫 문항 형식이 잘못되었습니다.")
    first_question["rationale"] = ""

    output_path = temp_packs_dir / source_path.name
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return temp_root


def run_backend_checks() -> None:
    base_env = {
        "READING_ELLA_DATABASE_PATH": str(DEFAULT_DB_PATH),
        "READING_ELLA_PACKS_DIR": None,
        "READING_ELLA_TRANSLATIONS_DIR": None,
        "READING_ELLA_TRANSLATION_PROVIDER": None,
        "READING_ELLA_EXPLANATION_PROVIDER": None,
        "READING_ELLA_TTS_PROVIDER": None,
    }

    if DEFAULT_DB_PATH.exists():
        DEFAULT_DB_PATH.unlink()

    no_rationale_root = create_no_rationale_pack_dir()

    try:
        with backend_env(base_env):
            from fastapi.testclient import TestClient
            from backend.app.main import app

            with TestClient(app) as client:
                health = client.get("/api/v1/health")
                require(health.status_code == 200, "health endpoint가 응답하지 않습니다.")
                log("[OK] health endpoint")

                for level in ("GT", "S", "MGT"):
                    response = client.get("/api/v1/packs", params={"level": level, "lang": "ko"})
                    require(response.status_code == 200, f"{level} pack 로드가 실패했습니다.")
                    pack_id = response.json()["pack_id"]
                    require(pack_id.startswith(f"g1_{level.lower()}_"), f"{level} 응답 pack_id 형식이 잘못되었습니다.")
                log("[OK] 레벨별 pack 로드")

                invalid_level = client.get("/api/v1/packs", params={"level": "BAD"})
                require(invalid_level.status_code == 400, "잘못된 level 오류 응답이 없습니다.")
                log("[OK] 잘못된 level 오류 처리")

                submission = client.post(
                    "/api/v1/submissions",
                    json={
                        "pack_id": "g1_gt_9001",
                        "started_at": "2026-03-13T10:00:00+09:00",
                        "answers": build_wrong_answers("g1_gt_9001", packs_dir=PACKS_DIR),
                    },
                )
                require(submission.status_code == 200, "제출 API가 실패했습니다.")
                submission_payload = submission.json()
                attempt_id = submission_payload["attempt_id"]
                wrong_ids = submission_payload["wrong_question_ids"]
                require(len(wrong_ids) == 6, "오답 6개 저장 검증에 실패했습니다.")
                log("[OK] 제출 및 채점")

                bad_submission = client.post(
                    "/api/v1/submissions",
                    json={
                        "pack_id": "g1_gt_9001",
                        "started_at": "2026-03-13T10:00:00+09:00",
                        "answers": build_wrong_answers("g1_gt_9001", packs_dir=PACKS_DIR)[:5],
                    },
                )
                require(bad_submission.status_code == 400, "답안 개수 오류 응답이 없습니다.")
                log("[OK] 제출 오류 처리")

                result = client.get(f"/api/v1/results/{attempt_id}")
                require(result.status_code == 200, "결과 조회가 실패했습니다.")
                result_payload = result.json()
                require(len(result_payload["wrong_questions"]) == 6, "결과 화면용 오답 목록 수가 맞지 않습니다.")
                log("[OK] 결과 조회")

                missing_result = client.get("/api/v1/results/not-a-real-attempt")
                require(missing_result.status_code == 404, "없는 attempt 결과 오류 응답이 없습니다.")
                log("[OK] 결과 오류 처리")

                review = client.get("/api/v1/review-items", params={"limit": 20})
                require(review.status_code == 200, "복습 목록 조회가 실패했습니다.")
                review_items = review.json()["items"]
                require(any(item["attempt_id"] == attempt_id for item in review_items), "복습 목록에 방금 저장한 오답이 없습니다.")
                log("[OK] DB 저장 및 복습 목록")

                local_translation = client.post(
                    "/api/v1/assist/translation",
                    json={
                        "pack_id": "g1_gt_9001",
                        "target_lang": "ko",
                        "scope": "passage",
                        "allow_external_api": False,
                    },
                )
                require(local_translation.status_code == 200, "로컬 번역 응답이 실패했습니다.")
                require(local_translation.json()["source"] == "local_overlay", "로컬 번역 source가 잘못되었습니다.")
                log("[OK] 로컬 번역")

                blocked_translation = client.post(
                    "/api/v1/assist/translation",
                    json={
                        "pack_id": "g1_s_9001",
                        "target_lang": "ja",
                        "scope": "passage",
                        "allow_external_api": False,
                    },
                )
                require(blocked_translation.status_code == 403, "번역 API OFF 차단이 동작하지 않습니다.")
                log("[OK] 번역 API OFF 차단")

                with backend_env({"READING_ELLA_TRANSLATION_PROVIDER": "mock"}):
                    api_translation = client.post(
                        "/api/v1/assist/translation",
                        json={
                            "pack_id": "g1_s_9001",
                            "target_lang": "ja",
                            "scope": "passage",
                            "allow_external_api": True,
                        },
                    )
                    require(api_translation.status_code == 200, "mock 번역 호출이 실패했습니다.")
                    translation_payload = api_translation.json()
                    require(translation_payload["source"] == "api_live", "mock 번역 source가 잘못되었습니다.")
                    require(
                        translation_payload["model_used"] == "gemini-3.1-flash-lite-preview",
                        "기본 번역 모델 라우팅이 기대와 다릅니다.",
                    )
                log("[OK] 번역 API ON")

                for detail_level in ("short", "deep"):
                    local_explanation = client.post(
                        "/api/v1/assist/explanation",
                        json={
                            "pack_id": "g1_gt_9001",
                            "question_id": "q1",
                            "chosen_index": 1,
                            "target_lang": "ko",
                            "detail_level": detail_level,
                            "allow_external_api": False,
                        },
                    )
                    require(local_explanation.status_code == 200, f"로컬 {detail_level} 해설이 실패했습니다.")
                    require(
                        local_explanation.json()["source"] == "local_rationale",
                        f"로컬 {detail_level} 해설 source가 잘못되었습니다.",
                    )
                log("[OK] short/deep 해설")

                with backend_env({"READING_ELLA_PACKS_DIR": str(no_rationale_root / "packs")}):
                    blocked_explanation = client.post(
                        "/api/v1/assist/explanation",
                        json={
                            "pack_id": "g1_gt_9001",
                            "question_id": "q1",
                            "chosen_index": 1,
                            "target_lang": "ko",
                            "detail_level": "short",
                            "allow_external_api": False,
                        },
                    )
                    require(blocked_explanation.status_code == 403, "해설 API OFF 차단이 동작하지 않습니다.")
                log("[OK] 해설 API OFF 차단")

                with backend_env(
                    {
                        "READING_ELLA_PACKS_DIR": str(no_rationale_root / "packs"),
                        "READING_ELLA_EXPLANATION_PROVIDER": "mock",
                    }
                ):
                    short_explanation = client.post(
                        "/api/v1/assist/explanation",
                        json={
                            "pack_id": "g1_gt_9001",
                            "question_id": "q1",
                            "chosen_index": 1,
                            "target_lang": "ko",
                            "detail_level": "short",
                            "allow_external_api": True,
                        },
                    )
                    require(short_explanation.status_code == 200, "mock short 해설 호출이 실패했습니다.")
                    require(
                        short_explanation.json()["model_used"] == "gemini-3.1-flash-lite-preview",
                        "short 해설 모델 라우팅이 기대와 다릅니다.",
                    )

                    deep_explanation = client.post(
                        "/api/v1/assist/explanation",
                        json={
                            "pack_id": "g1_gt_9001",
                            "question_id": "q1",
                            "chosen_index": 1,
                            "target_lang": "ko",
                            "detail_level": "deep",
                            "allow_external_api": True,
                        },
                    )
                    require(deep_explanation.status_code == 200, "mock deep 해설 호출이 실패했습니다.")
                    require(
                        deep_explanation.json()["model_used"] == "gemini-2.5-flash",
                        "deep 해설 모델 라우팅이 기대와 다릅니다.",
                    )
                log("[OK] 해설 API ON")

                browser_tts = client.post(
                    "/api/v1/assist/tts",
                    json={
                        "pack_id": "g1_gt_9001",
                        "scope": "passage",
                        "allow_external_api": False,
                    },
                )
                require(browser_tts.status_code == 200, "브라우저 TTS 응답이 실패했습니다.")
                require(browser_tts.json()["source"] == "browser_tts", "브라우저 TTS source가 잘못되었습니다.")
                log("[OK] 브라우저 TTS")

                blocked_tts = client.post(
                    "/api/v1/assist/tts",
                    json={
                        "pack_id": "g1_gt_9001",
                        "scope": "passage",
                        "allow_external_api": True,
                    },
                )
                require(blocked_tts.status_code == 501, "외부 TTS 미설정 오류가 없습니다.")
                log("[OK] 외부 TTS 미설정 처리")

                with backend_env({"READING_ELLA_TTS_PROVIDER": "mock"}):
                    api_tts = client.post(
                        "/api/v1/assist/tts",
                        json={
                            "pack_id": "g1_gt_9001",
                            "scope": "passage",
                            "allow_external_api": True,
                        },
                    )
                    require(api_tts.status_code == 200, "mock TTS 호출이 실패했습니다.")
                    tts_payload = api_tts.json()
                    require(tts_payload["source"] == "api_live", "mock TTS source가 잘못되었습니다.")
                    require(tts_payload["playback_mode"] == "external", "mock TTS 재생 방식이 잘못되었습니다.")
                log("[OK] 외부 TTS ON")
    finally:
        if DEFAULT_DB_PATH.exists():
            DEFAULT_DB_PATH.unlink()
        shutil.rmtree(no_rationale_root, ignore_errors=True)


def main() -> int:
    try:
        run_command([PNPM_COMMAND, "lint"], label="frontend lint")
        run_command([PNPM_COMMAND, "build"], label="frontend build")

        counts = count_pack_levels()
        for level in ("GT", "S", "MGT"):
            require(counts[level] >= 100, f"{level} pack 수가 부족합니다. 현재 {counts[level]}개입니다.")
        log(f"[OK] 레벨별 pack 수량 확인 {dict(counts)}")

        validate_all_packs()
        validate_all_translations()
        run_backend_checks()
    except CheckFailed as exc:
        log(f"[FAIL] {exc}")
        return 1

    log("[DONE] final checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
