"""Compatibility wrapper for the level-based content generator package."""

from __future__ import annotations

try:
    from .content.gt_generator import build_gt_pack_from_row
    from .content.mgt_generator import build_mgt_pack_from_row
    from .content.router import build_real_pack_from_row
    from .content.s_generator import build_s_pack_from_row
except ImportError:
    from content.gt_generator import build_gt_pack_from_row
    from content.mgt_generator import build_mgt_pack_from_row
    from content.router import build_real_pack_from_row
    from content.s_generator import build_s_pack_from_row


__all__ = [
    "build_gt_pack_from_row",
    "build_s_pack_from_row",
    "build_mgt_pack_from_row",
    "build_real_pack_from_row",
]
