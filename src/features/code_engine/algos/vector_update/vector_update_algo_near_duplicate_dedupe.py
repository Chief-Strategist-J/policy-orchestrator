"""
================================================================================
ALGORITHM BLUEPRINT: NEAR-DUPLICATE DEDUPLICATION (ALGO-VEC-UPD-145)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Clusters vectors with high semantic cosine similarity, groups near-duplicates,
   and selects canonical records while collapsing redundant items.
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorUpdateAlgoNearDuplicateDedupe:
    """
    --- contract:
      id: ALGO-VEC-UPD-145
      name: VectorUpdateAlgoNearDuplicateDedupe
      category: update
      complexity: O(N^2 * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        candidates: list[dict[str, Any]]
        similarity_threshold: float
      output_schema:
        canonical_records: list[dict[str, Any]]
        clustered_duplicates: dict[str, list[str]]
        deduplicated_count: int
    ---
    """

    @staticmethod
    def _cos(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) or 1e-12
        nb = math.sqrt(sum(x * x for x in b)) or 1e-12
        return dot / (na * nb)

    @classmethod
    def cluster_and_dedupe(
        cls,
        candidates: List[Dict[str, Any]],
        similarity_threshold: float = 0.98,
    ) -> Dict[str, Any]:
        canonical = []
        clusters: Dict[str, List[str]] = {}
        assigned = set()

        sorted_cand = sorted(candidates, key=lambda x: x.get("timestamp", 0), reverse=True)

        for i, item in enumerate(sorted_cand):
            iid = item.get("id", str(i))
            if iid in assigned:
                continue
            canonical.append(item)
            assigned.add(iid)
            clusters[iid] = []

            iv = item.get("vector", [])
            for j in range(i + 1, len(sorted_cand)):
                other = sorted_cand[j]
                oid = other.get("id", str(j))
                if oid in assigned:
                    continue
                ov = other.get("vector", [])
                if len(iv) == len(ov) and len(iv) > 0:
                    sim = cls._cos(iv, ov)
                    if sim >= similarity_threshold:
                        clusters[iid].append(oid)
                        assigned.add(oid)

        return {
            "canonical_records": canonical,
            "clustered_duplicates": clusters,
            "deduplicated_count": len(candidates) - len(canonical),
        }
