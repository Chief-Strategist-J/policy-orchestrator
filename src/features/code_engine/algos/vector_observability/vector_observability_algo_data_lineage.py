"""
================================================================================
ALGORITHM BLUEPRINT: VECTOR DATA LINEAGE & PROVENANCE TRACKER (ALGO-VEC-OBS-197)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs and audits end-to-end provenance graphs linking vector embeddings
   to their raw source documents, chunking strategies, embedding models, and quantization codebooks.

2. MATHEMATICAL FORMULATION:
   LineageHash = SHA256(source_id + source_hash + chunker_ver + model_ver + quant_ver)
   IsComplete = all(mandatory_lineage_keys in record)
================================================================================
"""

import hashlib
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoDataLineage:
    """
    --- contract:
      id: ALGO-VEC-OBS-197
      name: VectorObservabilityAlgoDataLineage
      category: observability
      complexity: O(N)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vector_records: list[dict[str, Any]]
        required_lineage_fields: Optional[list[str]]
      output_schema:
        total_records: int
        valid_lineage_count: int
        missing_lineage_records: list[str]
        provenance_chains: list[dict[str, Any]]
        is_all_lineage_complete: bool
    ---
    """

    @classmethod
    def audit_lineage(
        cls,
        vector_records: List[Dict[str, Any]],
        required_lineage_fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        req_fields = required_lineage_fields or [
            "source_doc_id",
            "source_content_hash",
            "chunker_version",
            "embedding_model_version",
            "ingestion_timestamp",
        ]

        if not vector_records:
            return {
                "total_records": 0,
                "valid_lineage_count": 0,
                "missing_lineage_records": [],
                "provenance_chains": [],
                "is_all_lineage_complete": True,
            }

        valid_cnt = 0
        missing_ids: List[str] = []
        chains: List[Dict[str, Any]] = []

        for rec in vector_records:
            rec_id = str(rec.get("vector_id", rec.get("id", "vec")))
            meta = rec.get("metadata", rec)

            missing = [f for f in req_fields if f not in meta or meta[f] is None]

            if missing:
                missing_ids.append(rec_id)
            else:
                valid_cnt += 1
                fingerprint_str = f"{meta.get('source_doc_id')}:{meta.get('source_content_hash')}:{meta.get('embedding_model_version')}"
                l_hash = hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()[:16]
                chains.append({
                    "vector_id": rec_id,
                    "source_doc_id": meta.get("source_doc_id"),
                    "embedding_model": meta.get("embedding_model_version"),
                    "lineage_hash": l_hash,
                })

        return {
            "total_records": len(vector_records),
            "valid_lineage_count": valid_cnt,
            "missing_lineage_records": missing_ids,
            "provenance_chains": chains[:50],
            "is_all_lineage_complete": len(missing_ids) == 0,
        }
