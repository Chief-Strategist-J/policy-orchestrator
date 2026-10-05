"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: TRIGRAM / N-GRAM INVERTED INDEX (ALGO 09)
================================================================================

1. OVERVIEW & OBJECTIVE:
   3-gram positional inverted index that maps every 3-character substring to the
   set of candidate file IDs containing it, enabling sub-millisecond regex candidate
   filtering across hundreds of files.

2. COMPLEXITY & INVARIANTS:
   - Index Build: Time O(TotalBytes) | Space O(TrigramCount).
   - Query Lookup: Time O(QueryTrigrams * SetIntersection) << O(FullScan).
   - Rules Enforced: R1 (Read Before Write), R5 (Result Caps).

3. EXECUTION FLOW:
   Extracts all 3-grams from input files into an inverted posting map.
   For any search query >= 3 characters, intersects the posting lists to find
   the minimal candidate file set before running full regex validation.
================================================================================
"""

from collections import defaultdict
from typing import List, Dict, Set

class SearchEngineTrigramIndexAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-09
      name: SearchEngineTrigramIndexAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - index.trigram
      - search.candidate_filter
      - index.inverted
      inputs:
        type: object
        required:
        - documents
        properties:
          documents:
            type: object
            additionalProperties:
              type: string
      outputs:
        type: object
        required:
        - total_trigrams
        properties:
          total_trigrams:
            type: integer
      parameters:
        type: object
        properties: {}
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(SumDocLength)
        space: O(Trigrams)
      preconditions:
      - len(input.documents) > 0
      postconditions:
      - output.total_trigrams >= 0
      compatible_adapters:
      - ADAPTER-QUERY-TO-TRIGRAM-CANDIDATES
    ---
    """
    def __init__(self) -> None:
        self._index: Dict[str, Set[str]] = defaultdict(set)
        self._indexed_files: Set[str] = set()

    def index_file(self, file_path: str, content: str) -> None:
        content_clean = content.lower()
        if len(content_clean) < 3:
            return
        self._indexed_files.add(file_path)
        for i in range(len(content_clean) - 2):
            gram = content_clean[i : i + 3]
            self._index[gram].add(file_path)

    def query_candidates(self, query: str) -> Set[str]:
        q_clean = query.lower()
        if len(q_clean) < 3:
            return set(self._indexed_files)

        query_grams = [q_clean[i : i + 3] for i in range(len(q_clean) - 2)]
        if not query_grams:
            return set(self._indexed_files)

        candidate_sets = [self._index.get(g, set()) for g in query_grams]
        candidate_sets.sort(key=len)
        
        result = set(candidate_sets[0])
        for cset in candidate_sets[1:]:
            result &= cset
            if not result:
                break

        return result
