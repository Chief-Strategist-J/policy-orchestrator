"""
================================================================================
ALGORITHM BLUEPRINT: DATABASE VS VECTOR INDEX RECONCILIATION AUDITOR (ALGO-VEC-OBS-198)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Performs periodic set-theoretic reconciliation audits comparing source database
   records against live vector index entries, detecting missing embeddings and stale orphans.

2. MATHEMATICAL FORMULATION:
   MissingInVectorStore = SourceDocIDs - VectorStoreSourceIDs
   OrphansInVectorStore = VectorStoreSourceIDs - SourceDocIDs
   ReconciliationMatchRatio = |Source ∩ Vector| / |Source ∪ Vector|
================================================================================
"""

from typing import Any, Dict, List, Optional, Set


class VectorObservabilityAlgoReconciliationChecks:
    """
    --- contract:
      id: ALGO-VEC-OBS-198
      name: VectorObservabilityAlgoReconciliationChecks
      category: observability
      complexity: O(N + M)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        source_database_ids: list[str]
        vector_index_ids: list[str]
        stale_content_hashes: Optional[dict[str, str]]
      output_schema:
        source_count: int
        vector_count: int
        match_ratio: float
        missing_in_vector_store: list[str]
        orphans_in_vector_store: list[str]
        is_reconciliation_passed: bool
    ---
    """

    @classmethod
    def audit(
        cls,
        source_database_ids: List[str],
        vector_index_ids: List[str],
        stale_content_hashes: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        source_set = set(source_database_ids)
        vector_set = set(vector_index_ids)

        missing = list(source_set - vector_set)
        orphans = list(vector_set - source_set)

        union_len = len(source_set.union(vector_set))
        inter_len = len(source_set.intersection(vector_set))
        match_ratio = inter_len / float(union_len) if union_len > 0 else 1.0

        is_passed = len(missing) == 0 and len(orphans) == 0

        return {
            "source_count": len(source_set),
            "vector_count": len(vector_set),
            "match_ratio": round(match_ratio, 4),
            "missing_in_vector_store": missing[:50],
            "orphans_in_vector_store": orphans[:50],
            "is_reconciliation_passed": is_passed,
        }
