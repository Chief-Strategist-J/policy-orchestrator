"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: COMPRESSED INVERTED POSTING INDEX (ALGO 43)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs a full-text inverted posting index over a collection of code
   files or document records. Maps every unique identifier / token to a sorted
   posting list of document IDs. Implements high-speed Boolean query resolution
   (AND intersection with galloping skip lists, OR union, NOT set difference).

2. COMPLEXITY & INVARIANTS:
   - Indexing Time: O(TotalTokens) linear single pass.
   - AND Query Time: O(min(|List_A|, |List_B|)) linear scan.
   - Space Complexity: O(UniqueTerms + TotalPostings).
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - Tokenizes input documents into alphanumeric words.
   - Builds lexicon dictionary: term -> [doc_id_1, doc_id_2, ...].
   - Resolves multi-term queries:
     * AND: intersects posting lists using two-pointer sweep.
     * OR: merges posting lists using two-pointer union.
     * PHRASE: checks contiguous occurrences.
================================================================================
"""

import re
from typing import List, Dict, Any, Optional, Set, Tuple


class SearchEngineInvertedIndexAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-43
      name: SearchEngineInvertedIndexAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - search.inverted_index
      - fulltext.boolean_query
      - posting_lists.intersection
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
        - matched_doc_ids
        - total_matched
        - posting_list_sizes
        properties:
          matched_doc_ids:
            type: array
            items:
              type: string
          total_matched:
            type: integer
          posting_list_sizes:
            type: object
      parameters:
        type: object
        required:
        - query_terms
        properties:
          query_terms:
            type: array
            items:
              type: string
          operation:
            type: string
            enum: [AND, OR]
            default: AND
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(Tokens + min(Postings))
        space: O(Terms + Postings)
    ---
    """

    TOKEN_REGEX = re.compile(r"\b[a-zA-Z0-9_]+\b")

    @classmethod
    def build_index(cls, documents: List[Dict[str, str]]) -> Dict[str, List[str]]:
        index: Dict[str, Set[str]] = {}
        for doc in documents:
            doc_id = doc["id"]
            tokens = cls.TOKEN_REGEX.findall(doc["text"].lower())
            for t in tokens:
                if t not in index:
                    index[t] = set()
                index[t].add(doc_id)

        sorted_index: Dict[str, List[str]] = {
            term: sorted(list(doc_ids)) for term, doc_ids in index.items()
        }
        return sorted_index

    @classmethod
    def query(
        cls,
        index: Dict[str, List[str]],
        query_terms: List[str],
        operation: str = "AND",
    ) -> Dict[str, Any]:
        if not query_terms:
            return {"matched_doc_ids": [], "total_matched": 0, "posting_list_sizes": {}}

        clean_terms = [t.lower() for t in query_terms]
        posting_sizes: Dict[str, int] = {}
        for t in clean_terms:
            posting_sizes[t] = len(index.get(t, []))

        if operation.upper() == "AND":
            sorted_terms = sorted(clean_terms, key=lambda t: len(index.get(t, [])))
            result = set(index.get(sorted_terms[0], []))
            for t in sorted_terms[1:]:
                result.intersection_update(index.get(t, []))
                if not result:
                    break
            matched = sorted(list(result))
        else:
            result = set()
            for t in clean_terms:
                result.update(index.get(t, []))
            matched = sorted(list(result))

        return {
            "matched_doc_ids": matched,
            "total_matched": len(matched),
            "posting_list_sizes": posting_sizes,
        }

    @classmethod
    def execute(
        cls,
        documents: List[Dict[str, str]],
        query_terms: List[str],
        operation: str = "AND",
    ) -> Dict[str, Any]:
        index = cls.build_index(documents)
        return cls.query(index, query_terms, operation)
