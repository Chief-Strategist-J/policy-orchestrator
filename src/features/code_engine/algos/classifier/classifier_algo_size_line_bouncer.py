"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FILE SIZE & LINE BOUNCER (ALGO-CLS-04)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Stat-based file size cap and fast newline-counting bouncer that classifies
   and filters excessively large files to prevent heap exhaustion, out-of-memory
   panics, and thread starvation during AST parsing.

2. ARCHITECTURAL ROLE:
   Classification & Guardrail role (Layer 1). Rejects giant files before
   memory-intensive transformations.

3. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(1) stat check + O(K) streaming byte count.
   - Space Complexity: O(1).
   - Rules Enforced: R5 (Resource & Result Caps).
   - Guardrails: G3 (Safety Limits: File size <= 10MB, Lines <= 50,000).
   - Zero-Inline-Comment Doctrine: Code body is 100% comment-free.

4. EXECUTION FLOW:
   a. Check os.path.getsize(file_path) against max_bytes.
   b. Stream file chunks in 64KB blocks to count newline bytes.
   c. If line count exceeds max_lines, reject file with descriptive reason.
   d. Return acceptance status tuple (is_acceptable, rejection_reason).
================================================================================
"""

import os
from typing import Tuple


class ClassifierAlgoSizeLineBouncer:
    """
    --- contract:
      id: ALGO-CLS-04
      name: ClassifierAlgoSizeLineBouncer
      version: 1.0.0
      category: classifier
      complexity:
        time: O(K)
        space: O(1)
      pure_function: false
      zero_inline_comments: true
      capability_tags:
        - filter.size
        - guardrail.resource
        - bouncer.line_length
      input_schema:
        file_path: string
        max_bytes: int
        max_lines: int
      output_schema:
        is_acceptable: bool
        rejection_reason: string
    ---
    """

    @staticmethod
    def check_limits(
        file_path: str,
        max_bytes: int = 10 * 1024 * 1024,
        max_lines: int = 50000,
    ) -> Tuple[bool, str]:
        if not os.path.isfile(file_path):
            return False, "File does not exist"

        size = os.path.getsize(file_path)
        if size > max_bytes:
            return False, f"File size ({size} bytes) exceeds limit ({max_bytes} bytes)"

        line_count = 0
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    line_count += chunk.count(b"\n")
                    if line_count > max_lines:
                        return False, f"Line count ({line_count}) exceeds limit ({max_lines})"
        except (OSError, PermissionError) as exc:
            return False, str(exc)

        return True, "OK"


SearchEngineSizeLineBouncerAlgo = ClassifierAlgoSizeLineBouncer
