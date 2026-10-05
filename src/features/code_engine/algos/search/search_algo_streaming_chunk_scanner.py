"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: STREAMING CHUNK SCANNER (ALGO 13)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Sliding window chunk scanner that streams large multi-megabyte files in
   fixed buffers with boundary overlap to detect matches spanning chunk edges.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(FileSize).
   - Space Complexity: O(ChunkSize + OverlapSize) bounded memory.
   - Rules Enforced: R1 (Read Before Write), R5 (Resource Caps).

3. EXECUTION FLOW:
   Reads file in 64KB blocks. Maintains an overlap tail of size equal to pattern
   length across iterations so multi-byte keywords on chunk seams are never missed.
================================================================================
"""

import os
from typing import List, Tuple

class SearchEngineStreamingChunkScannerAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-13
      name: SearchEngineStreamingChunkScannerAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - scanner.streaming
      - buffer.sliding_window
      - chunk.overlap
      inputs:
        type: object
        required:
        - file_path
        properties:
          file_path:
            type: string
      outputs:
        type: array
        items:
          type: object
      parameters:
        type: object
        properties:
          chunk_size:
            type: integer
            default: 65536
          overlap_size:
            type: integer
            default: 1024
      purity: IMPURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(FileSize)
        space: O(ChunkSize)
      preconditions:
      - parameters.overlap_size < parameters.chunk_size
      - os.path.isfile(input.file_path)
      postconditions:
      - len(output) >= 0
      compatible_adapters: []
    ---
    """
    @staticmethod
    def scan_file_chunks(
        file_path: str,
        needle: str,
        chunk_size: int = 65536,
    ) -> List[int]:
        if not needle or not os.path.isfile(file_path):
            return []

        needle_bytes = needle.encode("utf-8")
        needle_len = len(needle_bytes)
        matches: List[int] = []
        global_offset = 0
        tail = b""

        try:
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    combined = tail + chunk
                    start = 0
                    while True:
                        idx = combined.find(needle_bytes, start)
                        if idx == -1:
                            break
                        match_global = global_offset - len(tail) + idx
                        if match_global >= 0:
                            matches.append(match_global)
                        start = idx + 1
                    tail = combined[-needle_len:] if len(combined) >= needle_len else combined
                    global_offset += len(chunk)
        except (OSError, PermissionError):
            return []

        return matches
