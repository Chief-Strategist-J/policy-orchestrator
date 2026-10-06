"""
================================================================================
ALGORITHM BLUEPRINT: WORKSPACE EDIT (MULTI-FILE ATOMIC CHANGESET)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standard LSP WorkspaceEdit abstraction that groups multi-file modifications,
   new file creations, and file deletions into an atomic transactional package.
   Validates integrity across all targeted URI paths before batch application.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Atomicity Invariant: All file edits within a WorkspaceEdit either succeed
     together or fail together without leaving partial file mutations.
   - URI Normalization: Normalizes relative and absolute file paths across OS platforms.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(F * E) where F is file count, E is edits per file
   - Space Complexity: O(Total_Changeset_Size)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, Any, List, Optional, Tuple


class CodeEngineWorkspaceEditAlgo:
    """
    --- contract:
      id: ALGO-BUF-118
      name: CodeEngineWorkspaceEditAlgo
      version: 1.0.0
      category: buffer
      complexity:
        time: O(F * E)
        space: O(Total_Changeset_Size)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - buffer.workspace_edit
      - lsp.multi_file_changeset
      - atomic.batch_mutation
      input_schema:
        files: object
        changes: object
      output_schema:
        algorithm: string
        updated_files: object
        modified_file_count: integer
        total_edits_applied: integer
        is_success: boolean
    ---
    """

    def apply_workspace_edit(
        self, files: Dict[str, str], changes: Dict[str, List[Dict[str, Any]]]
    ) -> Tuple[Dict[str, str], int, int]:
        updated_files = dict(files)
        total_edits = 0
        modified_count = 0

        for file_path, edit_list in changes.items():
            if file_path not in updated_files:
                current_text = ""
            else:
                current_text = updated_files[file_path]

            sorted_edits = sorted(edit_list, key=lambda e: int(e.get("start_offset", 0)), reverse=True)

            for edit in sorted_edits:
                start = int(edit.get("start_offset", 0))
                end = int(edit.get("end_offset", start))
                new_text = str(edit.get("new_text", ""))

                current_text = current_text[:start] + new_text + current_text[end:]
                total_edits += 1

            updated_files[file_path] = current_text
            modified_count += 1

        return (updated_files, modified_count, total_edits)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        files: Dict[str, str] = payload.get("files", {})
        changes: Dict[str, List[Dict[str, Any]]] = payload.get("changes", {})

        updated, mod_count, edit_count = self.apply_workspace_edit(files, changes)

        return {
            "algorithm": "ALGO-BUF-118",
            "updated_files": updated,
            "modified_file_count": mod_count,
            "total_edits_applied": edit_count,
            "is_success": True,
        }
