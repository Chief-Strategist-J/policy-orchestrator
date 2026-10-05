"""
================================================================================
ALGORITHM BLUEPRINT: IDEMPOTENT INGESTION WITH CONTENT-HASH DEDUPE (ALGO-VEC-UPD-124)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Bypasses redundant embedding and vector index mutation by comparing normalized
   source content hashes against stored lineage hashes.
================================================================================
"""

import hashlib
from typing import Any, Dict, List, Optional


class VectorUpdateAlgoIdempotentIngestion:
    """
    --- contract:
      id: ALGO-VEC-UPD-124
      name: VectorUpdateAlgoIdempotentIngestion
      category: update
      complexity: O(N)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        incoming_chunks: list[dict[str, Any]]
        stored_hash_map: dict[str, str]
      output_schema:
        to_insert: list[dict[str, Any]]
        to_update: list[dict[str, Any]]
        skipped_noop_count: int
        dropped_ids: list[str]
    ---
    """

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    @classmethod
    def filter_batch(
        cls,
        incoming_chunks: List[Dict[str, Any]],
        stored_hash_map: Dict[str, str],
        active_source_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        to_insert: List[Dict[str, Any]] = []
        to_update: List[Dict[str, Any]] = []
        skipped = 0
        incoming_ids = set()

        for chunk in incoming_chunks:
            cid = chunk.get("chunk_id", "")
            incoming_ids.add(cid)
            content = chunk.get("content", "")
            chash = cls._hash(content)
            chunk_with_hash = dict(chunk)
            chunk_with_hash["content_hash"] = chash

            if cid not in stored_hash_map:
                to_insert.append(chunk_with_hash)
            elif stored_hash_map[cid] != chash:
                to_update.append(chunk_with_hash)
            else:
                skipped += 1

        dropped = []
        if active_source_ids is not None:
            active_set = set(active_source_ids)
            for sid in stored_hash_map.keys():
                if sid not in active_set and sid not in incoming_ids:
                    dropped.append(sid)

        return {
            "to_insert": to_insert,
            "to_update": to_update,
            "skipped_noop_count": skipped,
            "dropped_ids": sorted(dropped),
        }
