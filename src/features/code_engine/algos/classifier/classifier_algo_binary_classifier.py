"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BINARY / TEXT CLASSIFIER (ALGO-CLS-01)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Null-byte (0x00) and UTF-8 validity scanner that probes the first 8192
   bytes of a file to classify files into binary or plain text and guard against
   accidental binary file mutation or corruption.

2. ARCHITECTURAL ROLE:
   Classification & Guardrail role (Layer 1). Evaluates incoming files prior
   to AST indexing, regex searching, or structural refactoring.

3. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(min(FileSize, ProbeBytes)) byte scan.
   - Space Complexity: O(1) buffer allocation.
   - Rules Enforced: R7 (Encoding & Strictness).
   - Guardrails: G2 (Strict Deny-List on Binaries).
   - Zero-Inline-Comment Doctrine: Code body is 100% comment-free.

4. EXECUTION FLOW:
   a. Verify file existence and readability.
   b. Read up to probe_bytes (default 8KB) from the file head.
   c. If null bytes (0x00) exist, classify as binary (False).
   d. Attempt UTF-8 decoding. If decoding fails, classify as binary (False).
   e. Calculate ratio of non-ASCII control characters; if ratio > 30%, classify as binary.
   f. Otherwise, classify as valid text file (True).
================================================================================
"""

import os


class ClassifierAlgoBinaryClassifier:
    """
    --- contract:
      id: ALGO-CLS-01
      name: ClassifierAlgoBinaryClassifier
      version: 1.0.0
      category: classifier
      complexity:
        time: O(min(FileSize, ProbeBytes))
        space: O(1)
      pure_function: false
      zero_inline_comments: true
      capability_tags:
        - classifier.binary
        - filter.text
        - probe.null_byte
      input_schema:
        file_path: string
        probe_bytes: int
      output_schema:
        is_text: bool
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

            control_chars = sum(1 for c in decoded if ord(c) < 32 and c not in ("\n", "\r", "\t", "\b"))
            if len(decoded) > 0 and (control_chars / len(decoded)) > 0.30:
                return False

            return True

        except (OSError, PermissionError):
            return False


SearchEngineBinaryClassifierAlgo = ClassifierAlgoBinaryClassifier
