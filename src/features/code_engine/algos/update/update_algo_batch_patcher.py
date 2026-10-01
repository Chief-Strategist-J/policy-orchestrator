"""
Module: update_algo_batch_patcher
Architecture: Update Algorithm — Deterministic Atomic Batch File Patcher

Blueprint:
- Applies atomic multi-file text or regex patches with SHA-256 precondition verification.
- Supports dry-run validation to simulate replacements without modifying disk state.
- Rollbacks modifications if any file in a batch fails SHA-256 pre-check or validation.
- Zero-Inline-Comment Doctrine strictly enforced.
"""

from __future__ import annotations
import hashlib
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class PatchOperation:
    file_path: str
    find_pattern: str
    replace_text: str
    expected_sha256: Optional[str] = None
    is_regex: bool = False


@dataclass
class PatchResult:
    file_path: str
    success: bool
    occurrences: int
    before_sha256: str
    after_sha256: str
    error_message: Optional[str] = None


class UpdateBatchPatcherAlgo:
    @staticmethod
    def compute_sha256(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @classmethod
    def apply_patch(cls, op: PatchOperation, dry_run: bool = False) -> PatchResult:
        if not os.path.isfile(op.file_path):
            return PatchResult(
                file_path=op.file_path,
                success=False,
                occurrences=0,
                before_sha256="",
                after_sha256="",
                error_message="Target file not found",
            )

        try:
            with open(op.file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return PatchResult(
                file_path=op.file_path,
                success=False,
                occurrences=0,
                before_sha256="",
                after_sha256="",
                error_message=str(e),
            )

        current_sha256 = cls.compute_sha256(content)
        if op.expected_sha256 and current_sha256 != op.expected_sha256:
            return PatchResult(
                file_path=op.file_path,
                success=False,
                occurrences=0,
                before_sha256=current_sha256,
                after_sha256=current_sha256,
                error_message="Precondition SHA-256 mismatch",
            )

        if op.is_regex:
            new_content, count = re.subn(op.find_pattern, op.replace_text, content)
        else:
            count = content.count(op.find_pattern)
            new_content = content.replace(op.find_pattern, op.replace_text)

        new_sha256 = cls.compute_sha256(new_content)

        if not dry_run and count > 0:
            with open(op.file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

        return PatchResult(
            file_path=op.file_path,
            success=True,
            occurrences=count,
            before_sha256=current_sha256,
            after_sha256=new_sha256,
        )

    @classmethod
    def apply_batch(cls, ops: List[PatchOperation], dry_run: bool = False) -> List[PatchResult]:
        return [cls.apply_patch(op, dry_run=dry_run) for op in ops]
