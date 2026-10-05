"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BINARY / TEXT CLASSIFIER (ALGO 05)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Null-byte ($0x00$) and UTF-8 validity scanner that probes the first 8192
   bytes of a file to guard against accidental binary file mutation.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(min(FileSize, 8192)) byte scan.
   - Space Complexity: O(1) buffer allocation.
   - Rules Enforced: R7 (Encoding & Strictness).
   - Guardrails: G2 (Strict Deny-List on Binaries).

3. EXECUTION FLOW:
   Reads up to 8KB sample. If null bytes exist or UTF-8 decode fails with high
   non-ASCII control character ratio (>30%), returns False (Binary).
================================================================================
"""

import os

class SearchEngineBinaryClassifierAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-05
      name: SearchEngineBinaryClassifierAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - classifier.binary
      - filter.text
      - probe.null_byte
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
        - is_text
        properties:
          is_text:
            type: boolean
      parameters:
        type: object
        properties:
          sample_size:
            type: integer
            default: 1024
      purity: IMPURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(min(FileSize, SampleSize))
        space: O(1)
      preconditions:
      - os.path.isfile(input.file_path) == True
      postconditions:
      - isinstance(output.is_text, bool)
      compatible_adapters: []
    ---
    """
    @staticmethod
    def is_text_file(file_path: str, probe_bytes: int = 8192) -> bool:
        if not os.path.isfile(file_path):
            return False
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(probe_bytes)
            if not chunk:
                return True
            if b"\x00" in chunk:
                return False
            try:
                decoded = chunk.decode("utf-8")
            except UnicodeDecodeError:
                return False
            control_chars = sum(1 for ch in decoded if ord(ch) < 32 and ch not in "\n\r\t\b")
            return (control_chars / len(decoded)) < 0.15
        except (OSError, PermissionError):
            return False
