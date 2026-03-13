"""Runtime configuration for the Reading ELLA backend."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _parse_csv_list(raw_value: str | None, *, default: list[str]) -> list[str]:
    if raw_value is None or not raw_value.strip():
        return default
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def _build_default_cors_origins() -> list[str]:
    origins: list[str] = []
    for host in ("localhost", "127.0.0.1"):
        for port in (3000, 3001, 3002):
            origins.append(f"http://{host}:{port}")
    return origins


def _resolve_path(raw_value: str | None, *, default: Path, project_root: Path) -> Path:
    if raw_value is None or not raw_value.strip():
        return default

    path = Path(raw_value.strip())
    if path.is_absolute():
        return path
    return project_root / path


def _clean_optional(raw_value: str | None) -> str | None:
    if raw_value is None:
        return None
    cleaned = raw_value.strip()
    return cleaned or None


def _first_env(*names: str) -> str | None:
    for name in names:
        value = _clean_optional(os.getenv(name))
        if value is not None:
            return value
    return None


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        env_key = key.strip()
        env_value = value.strip()
        if not env_key:
            continue

        if len(env_value) >= 2 and env_value[0] == env_value[-1] and env_value[0] in {"'", '"'}:
            env_value = env_value[1:-1]

        os.environ.setdefault(env_key, env_value)


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    api_v1_prefix: str
    environment: str
    debug: bool
    cors_origins: list[str]
    project_root: Path
    packs_dir: Path
    translations_dir: Path
    data_dir: Path
    database_path: Path
    translation_provider: str | None
    explanation_provider: str | None
    tts_provider: str | None
    assist_model_default: str
    assist_model_deep: str
    tts_voice_default: str

    @property
    def translation_api_available(self) -> bool:
        return self.translation_provider is not None

    @property
    def explanation_api_available(self) -> bool:
        return self.explanation_provider is not None

    @property
    def tts_api_available(self) -> bool:
        return self.tts_provider is not None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    project_root = Path(__file__).resolve().parents[3]
    _load_env_file(project_root / "backend" / ".env")
    _load_env_file(project_root / ".env")
    packs_dir = _resolve_path(
        os.getenv("READING_ELLA_PACKS_DIR"),
        default=project_root / "packs",
        project_root=project_root,
    )
    translations_dir = _resolve_path(
        os.getenv("READING_ELLA_TRANSLATIONS_DIR"),
        default=project_root / "translations",
        project_root=project_root,
    )
    database_path = _resolve_path(
        os.getenv("READING_ELLA_DATABASE_PATH"),
        default=project_root / "backend" / "data" / "app.db",
        project_root=project_root,
    )
    data_dir = database_path.parent

    return Settings(
        app_name=os.getenv("READING_ELLA_APP_NAME", "Reading ELLA Backend"),
        app_version=os.getenv("READING_ELLA_APP_VERSION", "0.1.0"),
        api_v1_prefix=os.getenv("READING_ELLA_API_V1_PREFIX", "/api/v1"),
        environment=os.getenv("READING_ELLA_ENV", "development"),
        debug=os.getenv("READING_ELLA_DEBUG", "false").strip().lower() == "true",
        cors_origins=_parse_csv_list(
            os.getenv("READING_ELLA_CORS_ORIGINS"),
            default=_build_default_cors_origins(),
        ),
        project_root=project_root,
        packs_dir=packs_dir,
        translations_dir=translations_dir,
        data_dir=data_dir,
        database_path=database_path,
        translation_provider=_clean_optional(os.getenv("READING_ELLA_TRANSLATION_PROVIDER")),
        explanation_provider=_clean_optional(os.getenv("READING_ELLA_EXPLANATION_PROVIDER")),
        tts_provider=_clean_optional(os.getenv("READING_ELLA_TTS_PROVIDER")),
        assist_model_default=_first_env(
            "READING_ELLA_ASSIST_MODEL_DEFAULT",
            "READING_ELLA_TRANSLATION_MODEL_LITE",
            "READING_ELLA_EXPLANATION_MODEL_SHORT",
        )
        or "gemini-3.1-flash-lite-preview",
        assist_model_deep=_first_env(
            "READING_ELLA_ASSIST_MODEL_DEEP",
            "READING_ELLA_EXPLANATION_MODEL_DEEP",
        )
        or "gemini-2.5-flash",
        tts_voice_default=os.getenv("READING_ELLA_TTS_VOICE_DEFAULT", "alloy"),
    )
