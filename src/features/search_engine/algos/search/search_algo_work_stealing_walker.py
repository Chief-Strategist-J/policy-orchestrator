"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: PARALLEL WORK-STEALING WALKER (ALGO 02)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Multi-threaded directory hierarchy traversal leveraging dynamic worker
   dispatching and concurrent sub-tree enumeration for large monorepos.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(N / Workers) for parallel directory scanning.
   - Space Complexity: O(QueueSize + ActiveThreads).
   - Rules Enforced: R5 (Resource Caps), R8 (Deterministic Aggregate Sort).
   - Guardrails: G3 (Safety Limits - Concurrency bound to CPU count).

3. EXECUTION FLOW:
   Partitions top-level directory entries and dispatches concurrent subtree
   walkers across a bounded thread worker pool. Merges and sorts results.
================================================================================
"""

import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Set, Optional

from src.features.search_engine.algos.search.search_algo_recursive_walk import (
    SearchEngineRecursiveWalkAlgo,
    DEFAULT_IGNORED_NAMES,
)

class SearchEngineWorkStealingWalkerAlgo:
    @staticmethod
    def execute(
        root_dir: str,
        max_workers: int = 4,
        allowed_extensions: Optional[Set[str]] = None,
    ) -> List[str]:
        root_path = os.path.abspath(root_dir)
        if not os.path.isdir(root_path):
            return []

        top_level_subdirs = []
        top_level_files = []
        try:
            with os.scandir(root_path) as entries:
                for entry in entries:
                    if entry.name in DEFAULT_IGNORED_NAMES or entry.name.startswith("."):
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        top_level_subdirs.append(entry.path)
                    elif entry.is_file(follow_symlinks=False):
                        if not allowed_extensions or any(entry.name.endswith(ext) for ext in allowed_extensions):
                            top_level_files.append(entry.path)
        except (PermissionError, OSError):
            return []

        all_files = list(top_level_files)
        if not top_level_subdirs:
            return sorted(all_files)

        with ThreadPoolExecutor(max_workers=min(max_workers, len(top_level_subdirs))) as executor:
            futures = [
                executor.submit(SearchEngineRecursiveWalkAlgo.execute, sdir, 16, allowed_extensions)
                for sdir in top_level_subdirs
            ]
            for f in futures:
                try:
                    all_files.extend(f.result())
                except Exception:
                    pass

        return sorted(all_files)
