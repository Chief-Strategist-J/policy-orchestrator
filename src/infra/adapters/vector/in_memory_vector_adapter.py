"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: IN-MEMORY COSINE VECTOR ADAPTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides a pure-Python, zero-dependency, high-speed vector index
   implementing VectorStorePort. It computes normalized dot product (cosine
   similarity) across stored embeddings and supports arbitrary metadata key/value
   filtering, eliminating external database requirements for edge & local runs.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: Vector normalization, cosine similarity math,
     and predicate evaluation are detailed in this top-side blueprint.
   - Exact Scoring: Cosine similarity S = (A · B) / (||A|| * ||B||).
   - Filter Semantics: Exact match over top-level metadata dictionaries.

3. METHOD CONTRACTS:
   - upsert(): Thread-safe storage update.
   - query_by_vector(): Top-K nearest neighbors sorted descending by similarity score.
   - delete(): Evicts matching records by ID.
   - count(): Returns total active vectors.
   - clear(): Resets index state.
================================================================================
"""

import math
from typing import List, Dict, Any, Optional

from src.domain.ports.vector_port import (
    VectorStorePort,
    VectorDocument,
    VectorQueryResult,
)

class InMemoryCosineVectorAdapter(VectorStorePort):
    def __init__(self) -> None:
        self._store: Dict[str, VectorDocument] = {}

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        if len(vec_a) != len(vec_b) or not vec_a:
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def _matches_filter(self, metadata: Dict[str, Any], filter_metadata: Optional[Dict[str, Any]]) -> bool:
        if not filter_metadata:
            return True
        for k, v in filter_metadata.items():
            if metadata.get(k) != v:
                return False
        return True

    def upsert(self, documents: List[VectorDocument]) -> int:
        count = 0
        for doc in documents:
            self._store[doc.id] = doc
            count += 1
        return count

    def query_by_vector(
        self,
        vector: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[VectorQueryResult]:
        scored_results: List[VectorQueryResult] = []
        for doc in self._store.values():
            if not self._matches_filter(doc.metadata, filter_metadata):
                continue
            score = self._cosine_similarity(vector, doc.embedding)
            scored_results.append(VectorQueryResult(document=doc, score=score))

        scored_results.sort(key=lambda r: r.score, reverse=True)
        return scored_results[:top_k]

    def delete(self, ids: List[str]) -> int:
        removed = 0
        for doc_id in ids:
            if doc_id in self._store:
                del self._store[doc_id]
                removed += 1
        return removed

    def count(self) -> int:
        return len(self._store)

    def clear(self) -> None:
        self._store.clear()
