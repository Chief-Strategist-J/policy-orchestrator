"""
================================================================================
ALGORITHM BLUEPRINT: UPSERT BY STABLE ID (ALGO-VEC-UPD-111)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Deterministic upsert key derivation and deduplication engine. Produces a stable,
   reproducible content identifier across replays and re-runs to ensure zero duplicate
   entries in downstream vector indexes.

2. ARCHITECTURAL ROLE:
   Indexer role (Layer 1). Guarantees write idempotency by hashing immutable source
   attributes and skipping re-embedding if content hash matches existing state.

3. EXECUTION FLOW:
   a. Compute stable ID: sha256(source_id + ':' + chunk_id + ':' + model_version).
   b. Compute payload content hash over text, metadata, and optional vector components.
   c. Check existing record in index state.
   d. If absent: mark INSERT.
   e. If present and content hash matches: mark NOOP_SKIPPED.
   f. If present and content hash differs: mark UPDATE (tombstone old version).
================================================================================
"""

import hashlib
import json
from typing import Any, Dict, List, Optional


class VectorUpdateAlgoUpsertStableId:
    """
    --- contract:
      id: ALGO-VEC-UPD-111
      name: VectorUpdateAlgoUpsertStableId
      category: update
      complexity: O(|content|)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        source_id: str
        chunk_id: str
        model_version: str
        content: str
        metadata: dict[str, Any]
        existing_index: dict[str, Any]
      output_schema:
        stable_id: str
        action: str
        content_hash: str
        is_noop: bool
        previous_record: Optional[dict[str, Any]]
    ---
    """

    @staticmethod
    def derive_id(source_id: str, chunk_id: str, model_version: str) -> str:
        key = f"{source_id}:{chunk_id}:{model_version}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    @staticmethod
    def compute_content_hash(content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        meta_str = json.dumps(metadata or {}, sort_keys=True, default=str)
        payload = f"{content.strip()}||{meta_str}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def execute(
        cls,
        source_id: str,
        chunk_id: str,
        model_version: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        existing_index: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        stable_id = cls.derive_id(source_id, chunk_id, model_version)
        c_hash = cls.compute_content_hash(content, metadata)
        store = existing_index or {}

        if stable_id not in store:
            return {
                "stable_id": stable_id,
                "action": "INSERT",
                "content_hash": c_hash,
                "is_noop": False,
                "previous_record": None,
            }

        prev = store[stable_id]
        prev_hash = prev.get("content_hash", "")
        if prev_hash == c_hash:
            return {
                "stable_id": stable_id,
                "action": "NOOP_SKIPPED",
                "content_hash": c_hash,
                "is_noop": True,
                "previous_record": prev,
            }

        return {
            "stable_id": stable_id,
            "action": "UPDATE",
            "content_hash": c_hash,
            "is_noop": False,
            "previous_record": prev,
        }
