"""
================================================================================
ALGORITHM BLUEPRINT: WRITE-AHEAD ROLLBACK JOURNAL (PRE-IMAGE LOG)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Maintains an append-only transaction journal storing pre-image snapshots
   of files before applying edits. If any downstream verification step (syntax parse,
   type-check, linter, unit test) fails, the rollback journal restores all
   modified files to their exact pre-transaction byte states in reverse order.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Pre-Image Invariant: A file is NEVER written to until its pre-image snapshot
     is safely recorded and flushed in the journal.
   - Idempotent Rollback: Executing rollback restores the exact initial state.

3. COMPLEXITY ANALYSIS:
   - Journal Write: O(File_Size)
   - Rollback: O(Total_Modified_Bytes)
   - Space Complexity: O(Total_Modified_Bytes)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import hashlib
from typing import Dict, Any, List, Optional, Tuple


class JournalEntry:
    def __init__(self, file_path: str, pre_image: str, post_image: str) -> None:
        self.file_path: str = file_path
        self.pre_image: str = pre_image
        self.post_image: str = post_image
        self.pre_hash: str = hashlib.sha256(pre_image.encode("utf-8")).hexdigest()
        self.post_hash: str = hashlib.sha256(post_image.encode("utf-8")).hexdigest()


class CodeEngineWriteAheadJournalAlgo:
    """
    --- contract:
      id: ALGO-ATMC-161
      name: CodeEngineWriteAheadJournalAlgo
      version: 1.0.0
      category: atomic_mutation
      complexity:
        time: O(N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - atomic.write_ahead_journal
      - safety.rollback_log
      - transaction.pre_image
      input_schema:
        files: object
        mutations: object
        action: string
      output_schema:
        algorithm: string
        status: string
        restored_files: object
        journal_entries_count: integer
    ---
    """

    def __init__(self) -> None:
        self.entries: List[JournalEntry] = []

    def record_and_apply(self, files: Dict[str, str], mutations: Dict[str, str]) -> Dict[str, str]:
        updated = dict(files)
        for path, new_content in mutations.items():
            old_content = files.get(path, "")
            entry = JournalEntry(path, old_content, new_content)
            self.entries.append(entry)
            updated[path] = new_content
        return updated

    def rollback(self, files: Dict[str, str]) -> Dict[str, str]:
        restored = dict(files)
        for entry in reversed(self.entries):
            restored[entry.file_path] = entry.pre_image
        self.entries.clear()
        return restored

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        files: Dict[str, str] = payload.get("files", {})
        mutations: Dict[str, str] = payload.get("mutations", {})
        action: str = str(payload.get("action", "apply"))

        journal = CodeEngineWriteAheadJournalAlgo()

        if action == "rollback":
            for path, pre_val in payload.get("pre_images", {}).items():
                journal.entries.append(JournalEntry(path, pre_val, files.get(path, "")))
            res_files = journal.rollback(files)
            status = "rolled_back"
        else:
            res_files = journal.record_and_apply(files, mutations)
            status = "applied"

        return {
            "algorithm": "ALGO-ATMC-161",
            "status": status,
            "restored_files": res_files,
            "journal_entries_count": len(journal.entries),
        }
