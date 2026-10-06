"""
================================================================================
ALGORITHM BLUEPRINT: THREE-WAY MERGE (DIFF3 WITH CONFLICT DETECTION)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Merges two divergent revisions (Branch A / Ours, and Branch B / Theirs)
   relative to a common ancestor (Base / Ancestor). Computes diff(Base -> A)
   and diff(Base -> B). If both branches modify non-overlapping regions, the
   changes are cleanly combined. If both modify the same region with differing
   content, conflict markers (`<<<<<<< OURS`, `||||||| BASE`, `=======`, `>>>>>>> THEIRS`)
   are emitted.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Clean Merge Invariant: If only Branch A modified a block, take A. If only
     Branch B modified a block, take B. If both made identical edits, take A.
   - Conflict Isolation: Conflicts are bounded strictly to overlapping edit spans.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(LCS(Base, A) + LCS(Base, B))
   - Space Complexity: O(N)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import difflib
from typing import Dict, Any, List, Optional, Tuple


class CodeEngineThreeWayMergeAlgo:
    """
    --- contract:
      id: ALGO-DIFF-153
      name: CodeEngineThreeWayMergeAlgo
      version: 1.0.0
      category: diff
      complexity:
        time: O(N log N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - diff.three_way_merge
      - git.diff3
      - merge.conflict_resolution
      input_schema:
        base_text: string
        ours_text: string
        theirs_text: string
      output_schema:
        algorithm: string
        merged_text: string
        conflict_count: integer
        is_clean_merge: boolean
    ---
    """

    def merge_three_way(
        self, base_lines: List[str], ours_lines: List[str], theirs_lines: List[str]
    ) -> Tuple[List[str], int]:
        sm_ours = difflib.SequenceMatcher(None, base_lines, ours_lines)
        sm_theirs = difflib.SequenceMatcher(None, base_lines, theirs_lines)

        opcodes_ours = sm_ours.get_opcodes()
        opcodes_theirs = sm_theirs.get_opcodes()

        merged: List[str] = []
        conflicts: int = 0

        i_ours = 0
        i_theirs = 0
        base_pos = 0

        while base_pos < len(base_lines):
            mod_ours = None
            for tag, i1, i2, j1, j2 in opcodes_ours:
                if i1 <= base_pos < i2:
                    mod_ours = (tag, i1, i2, j1, j2)
                    break

            mod_theirs = None
            for tag, i1, i2, j1, j2 in opcodes_theirs:
                if i1 <= base_pos < i2:
                    mod_theirs = (tag, i1, i2, j1, j2)
                    break

            if mod_ours and mod_theirs:
                tag_o, o_i1, o_i2, o_j1, o_j2 = mod_ours
                tag_t, t_i1, t_i2, t_j1, t_j2 = mod_theirs

                if tag_o == "equal" and tag_t == "equal":
                    merged.append(base_lines[base_pos])
                    base_pos += 1
                elif tag_o != "equal" and tag_t == "equal":
                    chunk = ours_lines[o_j1:o_j2]
                    merged.extend(chunk)
                    base_pos = o_i2
                elif tag_o == "equal" and tag_t != "equal":
                    chunk = theirs_lines[t_j1:t_j2]
                    merged.extend(chunk)
                    base_pos = t_i2
                else:
                    chunk_o = ours_lines[o_j1:o_j2]
                    chunk_t = theirs_lines[t_j1:t_j2]
                    if chunk_o == chunk_t:
                        merged.extend(chunk_o)
                        base_pos = max(o_i2, t_i2)
                    else:
                        conflicts += 1
                        conflict_block = [
                            "<<<<<<< OURS",
                            *chunk_o,
                            "||||||| BASE",
                            *base_lines[min(o_i1, t_i1):max(o_i2, t_i2)],
                            "=======",
                            *chunk_t,
                            ">>>>>>> THEIRS",
                        ]
                        merged.extend(conflict_block)
                        base_pos = max(o_i2, t_i2)
            else:
                merged.append(base_lines[base_pos])
                base_pos += 1

        return (merged, conflicts)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        base_str: str = str(payload.get("base_text", ""))
        ours_str: str = str(payload.get("ours_text", ""))
        theirs_str: str = str(payload.get("theirs_text", ""))

        base_lines = base_str.splitlines()
        ours_lines = ours_str.splitlines()
        theirs_lines = theirs_str.splitlines()

        merged_lines, conflicts = self.merge_three_way(base_lines, ours_lines, theirs_lines)
        merged_output = "\n".join(merged_lines)

        return {
            "algorithm": "ALGO-DIFF-153",
            "merged_text": merged_output,
            "conflict_count": conflicts,
            "is_clean_merge": conflicts == 0,
        }
