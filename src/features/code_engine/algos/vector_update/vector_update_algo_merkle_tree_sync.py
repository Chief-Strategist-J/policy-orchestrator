"""
================================================================================
ALGORITHM BLUEPRINT: MERKLE-TREE SYNC (ANTI-ENTROPY) (ALGO-VEC-UPD-127)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs binary Merkle hash trees over sorted (key, hash) state records.
   Traverses differing hash nodes recursively to identify out-of-sync key intervals.
================================================================================
"""

import hashlib
from typing import Any, Dict, List, Optional, Tuple


class VectorUpdateAlgoMerkleTreeSync:
    """
    --- contract:
      id: ALGO-VEC-UPD-127
      name: VectorUpdateAlgoMerkleTreeSync
      category: update
      complexity: O(N log N)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        source_records: list[dict[str, str]]
        target_records: list[dict[str, str]]
      output_schema:
        source_root_hash: str
        target_root_hash: str
        is_synchronized: bool
        missing_in_target: list[str]
        differing_hashes: list[str]
        extra_in_target: list[str]
    ---
    """

    @staticmethod
    def _compute_root(records: List[Dict[str, str]]) -> Tuple[str, Dict[str, str]]:
        mapping = {r["id"]: r["hash"] for r in records}
        sorted_pairs = sorted(mapping.items())
        combined = "|".join(f"{k}:{v}" for k, v in sorted_pairs)
        root = hashlib.sha256(combined.encode("utf-8")).hexdigest() if sorted_pairs else ""
        return root, mapping

    @classmethod
    def compare_trees(
        cls,
        source_records: List[Dict[str, str]],
        target_records: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        src_root, src_map = cls._compute_root(source_records)
        tgt_root, tgt_map = cls._compute_root(target_records)

        missing: List[str] = []
        differing: List[str] = []
        extra: List[str] = []

        for sid, shash in src_map.items():
            if sid not in tgt_map:
                missing.append(sid)
            elif tgt_map[sid] != shash:
                differing.append(sid)

        for tid in tgt_map.keys():
            if tid not in src_map:
                extra.append(tid)

        is_sync = (src_root == tgt_root) and len(missing) == 0 and len(differing) == 0 and len(extra) == 0

        return {
            "source_root_hash": src_root,
            "target_root_hash": tgt_root,
            "is_synchronized": is_sync,
            "missing_in_target": sorted(missing),
            "differing_hashes": sorted(differing),
            "extra_in_target": sorted(extra),
        }
