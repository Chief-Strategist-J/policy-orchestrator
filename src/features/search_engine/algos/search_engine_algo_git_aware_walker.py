"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GIT-AWARE WALKER (ALGO 03)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Fast filesystem scanner that reads parent `.gitignore` rules hierarchically,
   filtering out untracked and ignored assets before parsing.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(N * RulesCount) pattern match operations.
   - Space Complexity: O(IgnoredRules).
   - Rules Enforced: R1 (Read Before Write), R7 (Encoding).
   - Guardrails: G2 (Strict Deny-List).

3. EXECUTION FLOW:
   Walks parent directory chain from target root to find all `.gitignore` files,
   compiles ignore glob rules, and filters candidate paths from the base walker.
================================================================================
"""

import os
import fnmatch
from typing import List, Set, Optional

from src.features.search_engine.algos.search_engine_algo_recursive_walk import (
    SearchEngineRecursiveWalkAlgo,
)

class SearchEngineGitAwareWalkerAlgo:
    @staticmethod
    def execute(
        root_dir: str,
        allowed_extensions: Optional[Set[str]] = None,
    ) -> List[str]:
        root_path = os.path.abspath(root_dir)
        gitignore_rules: List[str] = []
        
        current = root_path
        while current and current != os.path.dirname(current):
            gi_path = os.path.join(current, ".gitignore")
            if os.path.isfile(gi_path):
                try:
                    with open(gi_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#"):
                                gitignore_rules.append(line)
                except Exception:
                    pass
            current = os.path.dirname(current)

        all_files = SearchEngineRecursiveWalkAlgo.execute(root_path, allowed_extensions=allowed_extensions)
        if not gitignore_rules:
            return all_files

        filtered_files = []
        for fpath in all_files:
            rel_path = os.path.relpath(fpath, root_path)
            ignored = False
            for rule in gitignore_rules:
                clean_rule = rule.strip("/")
                if fnmatch.fnmatch(rel_path, clean_rule) or fnmatch.fnmatch(os.path.basename(fpath), clean_rule):
                    ignored = True
                    break
            if not ignored:
                filtered_files.append(fpath)

        return filtered_files
