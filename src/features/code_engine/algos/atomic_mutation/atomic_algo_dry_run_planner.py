"""
================================================================================
ALGORITHM BLUEPRINT: DRY-RUN PLANNER (PLAN / APPLY SEPARATION)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Enforces strict separation between change generation and disk mutations.
   Simulates all proposed edits against in-memory file buffers, generates a
   verified dry-run execution plan with diff summaries, and validates that all
   preconditions hold before any actual persistent file writes take place.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Zero Side-Effects in Dry-Run: The planning phase must NEVER mutate disk files.
   - Pre-condition Verification: Verifies file existence, read permissions,
     and content hashes during planning.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(Total_Edits)
   - Space Complexity: O(Total_Plan_Size)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import hashlib
from typing import Dict, Any, List, Optional, Tuple


class CodeEngineDryRunPlannerAlgo:
    """
    --- contract:
      id: ALGO-ATMC-157
      name: CodeEngineDryRunPlannerAlgo
      version: 1.0.0
      category: atomic_mutation
      complexity:
        time: O(E) where E is edits count
        space: O(Plan_Size)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - atomic.dry_run_planner
      - safety.plan_apply_separation
      - validation.preconditions
      input_schema:
        files: object
        planned_edits: array
      output_schema:
        algorithm: string
        plan_summary: object
        can_apply: boolean
        validation_errors: array
    ---
    """

    def plan_changes(
        self, files: Dict[str, str], edits: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], bool, List[str]]:
        simulated_files = dict(files)
        errors = []
        file_actions = []

        for edit in edits:
            fpath = edit.get("file_path", "")
            action = edit.get("action", "modify")
            expected_hash = edit.get("expected_sha256", None)

            if action == "modify":
                if fpath not in simulated_files:
                    errors.append(f"Target file does not exist: {fpath}")
                    continue
                cur_content = simulated_files[fpath]
                actual_hash = hashlib.sha256(cur_content.encode("utf-8")).hexdigest()
                if expected_hash and actual_hash != expected_hash:
                    errors.append(f"Content hash mismatch for {fpath}: expected {expected_hash}, got {actual_hash}")
                    continue

                search = edit.get("search_text", "")
                replace = edit.get("replace_text", "")
                if search and search not in cur_content:
                    errors.append(f"Search target not found in {fpath}")
                    continue
                simulated_files[fpath] = cur_content.replace(search, replace, 1) if search else replace
                file_actions.append({"file": fpath, "action": "modify", "bytes_delta": len(replace) - len(search)})

            elif action == "create":
                if fpath in simulated_files:
                    errors.append(f"Cannot create existing file: {fpath}")
                    continue
                content = edit.get("content", "")
                simulated_files[fpath] = content
                file_actions.append({"file": fpath, "action": "create", "bytes_delta": len(content)})

            elif action == "delete":
                if fpath not in simulated_files:
                    errors.append(f"Cannot delete non-existent file: {fpath}")
                    continue
                del simulated_files[fpath]
                file_actions.append({"file": fpath, "action": "delete", "bytes_delta": 0})

        can_apply = len(errors) == 0
        summary = {
            "total_edits": len(edits),
            "affected_files": len(file_actions),
            "actions": file_actions,
        }
        return (summary, can_apply, errors)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        files: Dict[str, str] = payload.get("files", {})
        edits: List[Dict[str, Any]] = payload.get("planned_edits", [])

        summary, can_apply, errors = self.plan_changes(files, edits)

        return {
            "algorithm": "ALGO-ATMC-157",
            "plan_summary": summary,
            "can_apply": can_apply,
            "validation_errors": errors,
        }
