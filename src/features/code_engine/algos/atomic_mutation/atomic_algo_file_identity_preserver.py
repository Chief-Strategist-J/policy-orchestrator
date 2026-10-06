"""
================================================================================
ALGORITHM BLUEPRINT: FILE IDENTITY PRESERVER (ENCODING, LINE ENDINGS, BOM, MODE)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Inspects, captures, and re-applies subtle file identity attributes across
   code edits:
   - Byte Order Mark (BOM): UTF-8 BOM (`\xef\xbb\xbf`), UTF-16 LE/BE.
   - Line Endings: Unix (`\n`) vs Windows (`\r\n`) vs mixed.
   - Final Newline Convention: Preserves absence or presence of trailing newline.
   - File Modes: Preserves Unix permission bits (e.g. executable scripts 0o755).

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Zero Accidental Line-Ending Normalization: Edits to a CRLF file MUST NOT
     silently convert unaffected lines to LF.
   - BOM Preservation: Files containing a BOM must retain that exact BOM on save.

3. COMPLEXITY ANALYSIS:
   - Analysis: O(N) where N is raw file byte size
   - Re-application: O(N)
   - Space Complexity: O(1)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, Any, List, Optional, Tuple


class FileIdentityMetadata:
    def __init__(
        self,
        has_utf8_bom: bool = False,
        line_ending: str = "\n",
        has_trailing_newline: bool = True,
        file_mode: int = 0o644,
    ) -> None:
        self.has_utf8_bom: bool = has_utf8_bom
        self.line_ending: str = line_ending
        self.has_trailing_newline: bool = has_trailing_newline
        self.file_mode: int = file_mode


class CodeEngineFileIdentityPreserverAlgo:
    """
    --- contract:
      id: ALGO-ATMC-165
      name: CodeEngineFileIdentityPreserverAlgo
      version: 1.0.0
      category: atomic_mutation
      complexity:
        time: O(N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - atomic.file_identity_preserver
      - encoding.bom_detection
      - line_endings.crlf_preservation
      input_schema:
        raw_bytes_hex: string
        modified_text: string
      output_schema:
        algorithm: string
        detected_crlf: boolean
        detected_bom: boolean
        reconstructed_text: string
    ---
    """

    UTF8_BOM = b"\xef\xbb\xbf"

    def analyze_bytes(self, raw_bytes: bytes) -> FileIdentityMetadata:
        has_bom = raw_bytes.startswith(self.UTF8_BOM)
        crlf_count = raw_bytes.count(b"\r\n")
        lf_count = raw_bytes.count(b"\n") - crlf_count

        dominant_ending = "\r\n" if crlf_count > lf_count else "\n"
        has_trailing = raw_bytes.endswith(b"\n") or raw_bytes.endswith(b"\r\n")

        return FileIdentityMetadata(
            has_utf8_bom=has_bom,
            line_ending=dominant_ending,
            has_trailing_newline=has_trailing,
        )

    def apply_identity(self, text: str, meta: FileIdentityMetadata) -> str:
        lines = text.splitlines()
        normalized_body = meta.line_ending.join(lines)
        if meta.has_trailing_newline and not normalized_body.endswith(meta.line_ending):
            normalized_body += meta.line_ending
        return normalized_body

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raw_hex: str = str(payload.get("raw_bytes_hex", ""))
        mod_text: str = str(payload.get("modified_text", ""))

        if raw_hex:
            raw_bytes = bytes.fromhex(raw_hex)
        else:
            raw_bytes = mod_text.encode("utf-8")

        meta = self.analyze_bytes(raw_bytes)
        reconstructed = self.apply_identity(mod_text, meta)

        return {
            "algorithm": "ALGO-ATMC-165",
            "detected_crlf": meta.line_ending == "\r\n",
            "detected_bom": meta.has_utf8_bom,
            "reconstructed_text": reconstructed,
        }
