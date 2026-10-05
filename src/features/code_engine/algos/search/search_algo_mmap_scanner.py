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
    """
    ---
    contract:
      algo_id: ALGO-SRCH-15
      name: SearchEngineMmapScannerAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - scanner.mmap
      - zero_copy.scan
      - kernel.page_cache
      inputs:
        type: object
        required:
        - file_path
        - pattern_bytes
        properties:
          file_path:
            type: string
          pattern_bytes:
            type: string
      outputs:
        type: array
        items:
          type: integer
      parameters:
        type: object
        properties: {}
      purity: IMPURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(FileSize)
        space: O(1)
      preconditions:
      - os.path.getsize(input.file_path) > 0
      postconditions:
      - is_strictly_ascending(output)
      compatible_adapters:
      - ADAPTER-OFFSET-TO-SPAN-OBS-16
    ---
    """
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
