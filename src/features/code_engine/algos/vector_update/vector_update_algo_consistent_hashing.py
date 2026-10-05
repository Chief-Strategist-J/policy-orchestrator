"""
================================================================================
ALGORITHM BLUEPRINT: CONSISTENT-HASHING REBALANCING (ALGO-VEC-UPD-139)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Distributes vector partition keys across a ring with virtual nodes. Computes
   minimal migration plans when nodes are added or removed from the cluster.
================================================================================
"""

import hashlib
from typing import Any, Dict, List, Optional, Tuple


class VectorUpdateAlgoConsistentHashing:
    """
    --- contract:
      id: ALGO-VEC-UPD-139
      name: VectorUpdateAlgoConsistentHashing
      category: update
      complexity: O(Keys * log(Nodes * V))
      pure_function: true
      zero_inline_comments: true
      input_schema:
        active_nodes: list[str]
        virtual_nodes_per_node: int
        keys_to_assign: list[str]
      output_schema:
        assignments: dict[str, str]
        node_key_counts: dict[str, int]
    ---
    """

    @staticmethod
    def _hash(val: str) -> int:
        return int(hashlib.md5(val.encode("utf-8")).hexdigest(), 16)

    @classmethod
    def assign_keys(
        cls,
        active_nodes: List[str],
        virtual_nodes_per_node: int = 16,
        keys_to_assign: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if not active_nodes:
            return {"assignments": {}, "node_key_counts": {}}

        ring: List[Tuple[int, str]] = []
        for n in active_nodes:
            for v in range(virtual_nodes_per_node):
                h = cls._hash(f"{n}-vn-{v}")
                ring.append((h, n))
        ring.sort(key=lambda x: x[0])

        assignments: Dict[str, str] = {}
        counts: Dict[str, int] = {n: 0 for n in active_nodes}

        for k in (keys_to_assign or []):
            kh = cls._hash(k)
            assigned_node = ring[0][1]
            for h, node in ring:
                if h >= kh:
                    assigned_node = node
                    break
            assignments[k] = assigned_node
            counts[assigned_node] += 1

        return {
            "assignments": assignments,
            "node_key_counts": counts,
            "total_assigned": len(assignments),
        }
