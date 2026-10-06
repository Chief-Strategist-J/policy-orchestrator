"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: INVERTED TRIGRAM 3-GRAM INDEX (ALGO 44)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Corpus-level inverted 3-gram character index. Deconstructs documents into
   character trigrams (e.g. "hello" -> "hel", "ell", "llo") and indexes them
   into posting lists. Allows running substring and regex candidate queries
   across massive codebases in sub-millisecond time.

2. COMPLEXITY & INVARIANTS:
   - Index Build: O(TotalDocumentCharacters) single sliding pass.
   - Query Time: O(min(|TrigramPostings|)) intersection of query trigrams.
   - Purity & Determinism: 100% pure and deterministic.
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - For each document, extracts all unique character trigrams.
   - Appends document ID to each trigram's posting list.
   - For a query string S: extracts all trigrams from S and computes posting list intersection.
   - Emits candidate document IDs for second-stage exact verification.
================================================================================
"""

from typing import List, Dict, Any, Set, Tuple, Optional


class SearchEngineTrigramInvertedIndexAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-44
      name: SearchEngineTrigramInvertedIndexAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - search.trigram_index
      - substring.prefilter
      - code_search.scaling
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
        type: object
        required:
        - candidate_doc_ids
        - query_trigrams
        - total_candidates
        properties:
          candidate_doc_ids:
            type: array
            items:
              type: string
          query_trigrams:
            type: array
            items:
              type: string
          total_candidates:
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
        time: O(Chars + min(Postings))
        space: O(Trigrams + Postings)
    ---
    """

    @classmethod
    def extract_trigrams(cls, text: str) -> Set[str]:
        trigrams: Set[str] = set()
        if len(text) < 3:
            return trigrams
        for i in range(len(text) - 2):
            trigrams.add(text[i:i + 3])
        return trigrams

    @classmethod
    def build_index(cls, documents: List[Dict[str, str]]) -> Dict[str, List[str]]:
        index: Dict[str, Set[str]] = {}
        for doc in documents:
            doc_id = doc["id"]
            tri_set = cls.extract_trigrams(doc["text"])
            for tri in tri_set:
                if tri not in index:
                    index[tri] = set()
                index[tri].add(doc_id)

        return {tri: sorted(list(doc_ids)) for tri, doc_ids in index.items()}

    @classmethod
    def query(
        cls,
        index: Dict[str, List[str]],
        query: str,
    ) -> Dict[str, Any]:
        query_trigrams = cls.extract_trigrams(query)
        if not query_trigrams:
            return {
                "candidate_doc_ids": [],
                "query_trigrams": [],
                "total_candidates": 0,
            }

        sorted_trigrams = sorted(list(query_trigrams), key=lambda tri: len(index.get(tri, [])))
        candidates = set(index.get(sorted_trigrams[0], []))

        for tri in sorted_trigrams[1:]:
            candidates.intersection_update(index.get(tri, []))
            if not candidates:
                break

        res_docs = sorted(list(candidates))
        return {
            "candidate_doc_ids": res_docs,
            "query_trigrams": sorted(list(query_trigrams)),
            "total_candidates": len(res_docs),
        }

    @classmethod
    def execute(
        cls,
        documents: List[Dict[str, str]],
        query: str,
    ) -> Dict[str, Any]:
        index = cls.build_index(documents)
        return cls.query(index, query)
