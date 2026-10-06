"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: POSITIONAL TRIGRAM OFFSET INDEX (ALGO 45)
================================================================================

1. OVERVIEW & OBJECTIVE:
   A high-precision trigram index (Zoekt style) that records exact byte offsets
   (DocId, Offset) for each trigram occurrence. For a query "hello", verifies
   that "hel" at offset p is immediately followed by "ell" at p+1 and "llo" at
   p+2, dropping false-positive candidate documents by >95% before disk reads.

2. COMPLEXITY & INVARIANTS:
   - Index Build: O(TotalDocumentCharacters).
   - Positional Verification: O(min(Postings)) linear contiguous alignment check.
   - Purity & Determinism: 100% pure and deterministic.
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - Indexes: trigram -> [(doc_id_1, offset_a), (doc_id_1, offset_b), ...].
   - For query Q:
     * Extracts trigrams T_0, T_1, ..., T_k at query offsets 0, 1, ..., k.
     * Looks up positional posting lists.
     * Checks if there exists an offset P in doc D such that T_i occurs at P + i for all i.
================================================================================
"""

from typing import List, Dict, Any, Set, Tuple, Optional


class SearchEnginePositionalTrigramIndexAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-45
      name: SearchEnginePositionalTrigramIndexAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - search.positional_index
      - zoekt.trigram_offset
      - precision.alignment
      inputs:
        type: object
        required:
        - documents
        properties:
          documents:
            type: array
            items:
              type: object
              required:
              - id
              - text
              properties:
                id:
                  type: string
                text:
                  type: string
      outputs:
        type: array
        items:
          type: object
          required:
          - doc_id
          - match_offsets
          properties:
            doc_id:
              type: string
            match_offsets:
              type: array
              items:
                type: integer
      parameters:
        type: object
        required:
        - query
        properties:
          query:
            type: string
            minLength: 3
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(Chars + min(PositionalPostings))
        space: O(TrigramOccurrences)
    ---
    """

    @classmethod
    def build_index(cls, documents: List[Dict[str, str]]) -> Dict[str, Dict[str, List[int]]]:
        index: Dict[str, Dict[str, List[int]]] = {}
        for doc in documents:
            doc_id = doc["id"]
            text = doc["text"]
            for i in range(len(text) - 2):
                tri = text[i:i + 3]
                if tri not in index:
                    index[tri] = {}
                if doc_id not in index[tri]:
                    index[tri][doc_id] = []
                index[tri][doc_id].append(i)

        return index

    @classmethod
    def query(
        cls,
        index: Dict[str, Dict[str, List[int]]],
        query: str,
    ) -> List[Dict[str, Any]]:
        if len(query) < 3:
            return []

        q_trigrams = [(query[i:i + 3], i) for i in range(len(query) - 2)]
        first_tri, _ = q_trigrams[0]
        if first_tri not in index:
            return []

        results: List[Dict[str, Any]] = []

        candidate_docs = set(index[first_tri].keys())
        for tri, _ in q_trigrams[1:]:
            if tri not in index:
                return []
            candidate_docs.intersection_update(index[tri].keys())

        for doc_id in sorted(candidate_docs):
            valid_start_offsets: List[int] = []
            base_offsets = index[first_tri][doc_id]

            for start_p in base_offsets:
                is_valid = True
                for tri, offset_delta in q_trigrams[1:]:
                    expected_p = start_p + offset_delta
                    if expected_p not in index[tri][doc_id]:
                        is_valid = False
                        break
                if is_valid:
                    valid_start_offsets.append(start_p)

            if valid_start_offsets:
                results.append({
                    "doc_id": doc_id,
                    "match_offsets": sorted(valid_start_offsets),
                })

        return results

    @classmethod
    def execute(
        cls,
        documents: List[Dict[str, str]],
        query: str,
    ) -> List[Dict[str, Any]]:
        index = cls.build_index(documents)
        return cls.query(index, query)
