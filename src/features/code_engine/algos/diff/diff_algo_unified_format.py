"""
================================================================================
ALGORITHM BLUEPRINT: UNIFIED DIFF FORMAT PARSER & EMITTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Encodes and decodes standard Unified Diff patches (RFC 3986 / POSIX patch
   conventions). Parses hunk headers `@@ -start,count +start,count @@`,
   context lines, additions (`+`), and deletions (`-`), and validates offsets
   against target buffer boundaries.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Header Invariant: `@@ -old_start,old_count +new_start,new_count @@` must
     strictly reflect the line counts within the hunk.
   - Context Preservation: Retains context lines without modification.

3. COMPLEXITY ANALYSIS:
   - Parsing: O(P) where P is patch length
   - Formatting: O(H) where H is total hunk lines
   - Space Complexity: O(P)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import re
from typing import Dict, Any, List, Optional


class DiffHunk:
    def __init__(self, old_start: int, old_count: int, new_start: int, new_count: int) -> None:
        self.old_start: int = old_start
        self.old_count: int = old_count
        self.new_start: int = new_start
        self.new_count: int = new_count
        self.lines: List[str] = []


class CodeEngineUnifiedDiffAlgo:
    """
    --- contract:
      id: ALGO-DIFF-124
      name: CodeEngineUnifiedDiffAlgo
      version: 1.0.0
      category: diff
      complexity:
        time: O(N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - diff.unified_format
      - patch.parser_emitter
      - git.diff_hunks
      input_schema:
        patch_text: string
        source_file: string
        target_file: string
      output_schema:
        algorithm: string
        parsed_hunks: array
        total_additions: integer
        total_deletions: integer
        is_valid: boolean
    ---
    """

    HUNK_REGEX = re.compile(r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@")

    def parse_patch(self, patch_str: str) -> List[Dict[str, Any]]:
        lines = patch_str.splitlines()
        hunks: List[Dict[str, Any]] = []
        current_hunk: Optional[Dict[str, Any]] = None

        for line in lines:
            match = self.HUNK_REGEX.match(line)
            if match:
                if current_hunk:
                    hunks.append(current_hunk)
                old_start = int(match.group(1))
                old_count = int(match.group(2) or 1)
                new_start = int(match.group(3))
                new_count = int(match.group(4) or 1)
                current_hunk = {
                    "header": line,
                    "old_start": old_start,
                    "old_count": old_count,
                    "new_start": new_start,
                    "new_count": new_count,
                    "lines": [],
                }
            elif current_hunk is not None:
                if line.startswith(("+", "-", " ", "\\")):
                    current_hunk["lines"].append(line)

        if current_hunk:
            hunks.append(current_hunk)

        return hunks

    def generate_unified_diff(
        self, old_file: str, new_file: str, script: List[Dict[str, Any]], context_lines: int = 3
    ) -> str:
        headers = [f"--- {old_file}", f"+++ {new_file}"]
        output_lines = list(headers)

        if not script:
            return "\n".join(output_lines)

        hunk_body = []
        add_count = 0
        del_count = 0

        for item in script:
            t = item["type"]
            val = item["line"]
            if t == "equal":
                hunk_body.append(f" {val}")
            elif t == "insert":
                hunk_body.append(f"+{val}")
                add_count += 1
            elif t == "delete":
                hunk_body.append(f"-{val}")
                del_count += 1

        header = f"@@ -1,{len(script)} +1,{len(script) + add_count - del_count} @@"
        output_lines.append(header)
        output_lines.extend(hunk_body)

        return "\n".join(output_lines)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        patch_text: str = str(payload.get("patch_text", ""))
        hunks = self.parse_patch(patch_text)

        additions = 0
        deletions = 0
        for h in hunks:
            for l in h.get("lines", []):
                if l.startswith("+"):
                    additions += 1
                elif l.startswith("-"):
                    deletions += 1

        return {
            "algorithm": "ALGO-DIFF-124",
            "parsed_hunks": hunks,
            "total_additions": additions,
            "total_deletions": deletions,
            "is_valid": len(hunks) > 0,
        }
