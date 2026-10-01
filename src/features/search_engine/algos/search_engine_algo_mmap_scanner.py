"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MEMORY-MAPPED I/O SCANNER (ALGO 15)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Zero-copy virtual memory scanner that maps file descriptors directly into
   virtual address space (`mmap.mmap`) for high-throughput byte pattern scanning.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(FileSize) at raw hardware / page-cache speed.
   - Space Complexity: O(1) user-space buffer overhead.
   - Rules Enforced: R1 (Read Before Write), R5 (Resource Caps).

3. EXECUTION FLOW:
   Maps file into memory via OS page cache in read-only mode, searches byte
   sequences using kernel-optimized `mmap.find()`, and returns match offsets.
================================================================================
"""

import os
import mmap
from typing import List

class SearchEngineMmapScannerAlgo:
    @staticmethod
    def scan_file(file_path: str, needle: str) -> List[int]:
        if not needle or not os.path.isfile(file_path):
            return []

        target_bytes = needle.encode("utf-8")
        matches: List[int] = []

        try:
            with open(file_path, "rb") as f:
                size = os.fstat(f.fileno()).st_size
                if size == 0:
                    return []
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    start = 0
                    while True:
                        idx = mm.find(target_bytes, start)
                        if idx == -1:
                            break
                        matches.append(idx)
                        start = idx + 1
        except (OSError, PermissionError, ValueError):
            return []

        return matches
