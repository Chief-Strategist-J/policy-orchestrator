"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FILE SIZE & LINE BOUNCER (ALGO 07)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Stat-based file size cap and fast newline-counting bouncer that rejects
   excessively large files to prevent heap exhaustion and thread starvation.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(1) filesystem stat check + optional streaming count.
   - Space Complexity: O(1).
   - Rules Enforced: R5 (Resource & Result Caps).
   - Guardrails: G3 (Safety Limits: File size <= 10MB, Lines <= 50,000).

3. EXECUTION FLOW:
   Checks `os.path.getsize(file_path)` against max_byte_limit. If within bounds,
   streams chunks to verify total line count does not exceed max_lines.
================================================================================
"""

import os
from typing import Tuple

class SearchEngineSizeLineBouncerAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-07
      name: SearchEngineSizeLineBouncerAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - filter.size
      - guardrail.resource
      - bouncer.line_length
      inputs:
        type: object
        required:
        - file_path
        properties:
          file_path:
            type: string
      outputs:
        type: object
        required:
        - is_acceptable
        properties:
          is_acceptable:
            type: boolean
          rejection_reason:
            type: string
            nullable: true
      parameters:
        type: object
        properties:
          max_bytes:
            type: integer
            default: 5000000
          max_line_length:
            type: integer
            default: 10000
      purity: IMPURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(K)
        space: O(1)
      preconditions:
      - os.path.isfile(input.file_path) == True
      postconditions:
      - isinstance(output.is_acceptable, bool)
      compatible_adapters: []
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
