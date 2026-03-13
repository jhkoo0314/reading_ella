"""Route a plan row to the correct level generator."""

from __future__ import annotations

from typing import Any

try:
    from ..create_pack import DEFAULT_VERSION, normalize_level
except ImportError:
    from create_pack import DEFAULT_VERSION, normalize_level

from .gt_generator import build_gt_pack_from_row
from .mgt_generator import build_mgt_pack_from_row
from .s_generator import build_s_pack_from_row


def build_real_pack_from_row(
    row: dict[str, str],
    *,
    version: str = DEFAULT_VERSION,
    created_at: str | None = None,
) -> dict[str, Any]:
    level = normalize_level(row["level"])
    if level == "GT":
        return build_gt_pack_from_row(row, version=version, created_at=created_at)
    if level == "S":
        return build_s_pack_from_row(row, version=version, created_at=created_at)
    if level == "MGT":
        return build_mgt_pack_from_row(row, version=version, created_at=created_at)
    raise ValueError(f"지원하지 않는 level입니다: {level}")
