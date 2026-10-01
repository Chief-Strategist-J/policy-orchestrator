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
