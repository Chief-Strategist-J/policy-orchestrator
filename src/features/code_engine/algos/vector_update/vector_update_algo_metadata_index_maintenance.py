"""
================================================================================
ALGORITHM BLUEPRINT: METADATA INDEX MAINTENANCE (ALGO-VEC-UPD-154)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Updates secondary categorical inverted indexes and numerical range boundaries
   atomically alongside primary vector storage mutations.
================================================================================
"""

from typing import Any, Dict, List, Optional, Set


class VectorUpdateAlgoMetadataIndexMaintenance:
    """
    --- contract:
      id: ALGO-VEC-UPD-154
      name: VectorUpdateAlgoMetadataIndexMaintenance
      category: update
      complexity: O(F)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        current_inverted_index: dict[str, dict[str, list[str]]]
        mutation_type: str
        record_id: str
        metadata: dict[str, Any]
      output_schema:
        updated_inverted_index: dict[str, dict[str, list[str]]]
        indexed_fields_count: int
    ---
    """

    @classmethod
    def apply_mutation(
        cls,
        current_inverted_index: Dict[str, Dict[str, List[str]]],
        mutation_type: str,
        record_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        idx: Dict[str, Dict[str, Set[str]]] = {}
        for f, val_map in current_inverted_index.items():
            idx[f] = {v: set(ids) for v, ids in val_map.items()}

        op = mutation_type.upper()
        if op == "DELETE" or op == "UPSERT":
            for f, val_map in idx.items():
                for v, id_set in val_map.items():
                    id_set.discard(record_id)

        if op == "UPSERT" and metadata:
            for field, val in metadata.items():
                if field not in idx:
                    idx[field] = {}
                v_str = str(val)
                if v_str not in idx[field]:
                    idx[field][v_str] = set()
                idx[field][v_str].add(record_id)

        serialized: Dict[str, Dict[str, List[str]]] = {}
        for f, val_map in idx.items():
            serialized[f] = {v: sorted(list(ids)) for v, ids in val_map.items() if ids}

        return {
            "updated_inverted_index": serialized,
            "indexed_fields_count": len(serialized),
        }
