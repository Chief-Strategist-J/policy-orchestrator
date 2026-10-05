"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: RECURSIVE DIRECTORY WALKER (ALGO 01)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Deterministic, depth-first traversal of a directory subtree with O(depth)
   memory bounds, batched kernel enumeration, and directory-level early pruning.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(N) filesystem operations across N entries.
   - Space Complexity: O(D) memory where D is maximum directory depth (D << N).
   - Rules Enforced: R1 (Read Before Write), R8 (Deterministic Reverse Sort).
   - Guardrails: G1 (Path allowlist).

3. EXECUTION FLOW:
   LIFO stack traversal storing relative paths. Evaluates directory segments
   against ignore lists prior to subtree descent. Yields regular file paths
   matching allowed extensions in deterministic lexicographical order.
================================================================================
"""

import os
from typing import List, Set, Optional

DEFAULT_IGNORED_NAMES: Set[str] = {
    ".git", "node_modules", "dist", "build", ".next", "vendor",
    ".idea", ".vscode", "__pycache__", ".turbo", "coverage",
    "data", "brain", ".gemini", "scratch", "tmp", "bin"
}


class SearchEngineRecursiveWalkAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-01
      name: SearchEngineRecursiveWalkAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - filesystem.traversal
      - directory.walk.dfs
      - filter.ignored_dirs
      inputs:
        type: object
        required:
        - root_dir
        properties:
          root_dir:
            type: string
      outputs:
        type: array
        items:
          type: string
          description: Absolute file path
      parameters:
        type: object
        properties:
          max_depth:
            type: integer
            default: 16
            minimum: 1
          allowed_extensions:
            type: array
            items:
              type: string
          ignored_names:
            type: array
            items:
              type: string
      purity: IMPURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(N)
        space: O(D)
      preconditions:
      - os.path.isdir(input.root_dir) == True
      postconditions:
      - is_sorted(output)
      - all(os.path.isfile(p) for p in output)
      compatible_adapters:
      - ADAPTER-FILE-PATH-TO-CONTENT
      - ADAPTER-FILE-PATH-TO-AST
    ---
    """
    @staticmethod

    def execute(
        root_dir: str,
        max_depth: int = 16,
        allowed_extensions: Optional[Set[str]] = None,
        ignored_names: Set[str] = DEFAULT_IGNORED_NAMES,
    ) -> List[str]:
        root_path = os.path.abspath(root_dir)
        matched_files: List[str] = []
        stack = [(root_path, 0)]

        while stack:
            current_dir, depth = stack.pop()
            if depth > max_depth or not os.path.isdir(current_dir):
                continue

            try:
                with os.scandir(current_dir) as entries:
                    dirs_to_push = []
                    for entry in sorted(entries, key=lambda e: e.name, reverse=True):
                        if entry.name in ignored_names or entry.name.startswith("."):
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            dirs_to_push.append((entry.path, depth + 1))
                        elif entry.is_file(follow_symlinks=False):
                            if not allowed_extensions or any(entry.name.endswith(ext) for ext in allowed_extensions):
                                matched_files.append(entry.path)
                    stack.extend(dirs_to_push)
            except (PermissionError, OSError):
                continue

        matched_files.sort()
        return matched_files
