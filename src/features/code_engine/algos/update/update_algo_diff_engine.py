"""
Module: update_algo_diff_engine
Architecture: Update Algorithm — Unified GNU/Git Context Diff Generator

Blueprint:
- Generates unified diffs (`--- a/path` `+++ b/path` `@@ -1,5 +1,5 @@`) between source code states.
- Preserves context lines and line numbering for deterministic human & agent inspection.
- Formats git patch headers compliant with RFC/Git patch application tooling.
- Zero-Inline-Comment Doctrine strictly enforced.
"""

from __future__ import annotations
import difflib
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class UnifiedDiffResult:
    file_path: str
    has_changes: bool
    added_lines: int
    deleted_lines: int
    patch: str


class UpdateDiffEngineAlgo:
    @staticmethod
    def generate_unified_diff(
        original_content: str,
        modified_content: str,
        file_path: str = "file",
        context_lines: int = 3,
    ) -> UnifiedDiffResult:
        orig_lines = original_content.splitlines(keepends=True)
        mod_lines = modified_content.splitlines(keepends=True)

        diff_lines = list(
            difflib.unified_diff(
                orig_lines,
                mod_lines,
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
                n=context_lines,
            )
        )

        has_changes = len(diff_lines) > 0
        added = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
        deleted = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))
        patch_str = "".join(diff_lines)

        return UnifiedDiffResult(
            file_path=file_path,
            has_changes=has_changes,
            added_lines=added,
            deleted_lines=deleted,
            patch=patch_str,
        )
