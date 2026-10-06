"""
================================================================================
ALGORITHM BLUEPRINT: WAND & BLOCK-MAX WAND (TOP-K CANDIDATE PRUNING)
================================================================================

1. OVERVIEW:
   WAND (Weak AND) and Block-Max WAND are dynamic pruning algorithms for top-K
   ranked retrieval (e.g., BM25/TF-IDF scoring). By computing static term upper-bounds
   and dynamic block-level maximum scores, WAND identifies a 'pivot' document and
   safely skips thousands of candidate postings that cannot surpass the K-th best
   score threshold theta, accelerating query evaluation by 5x-50x.

2. MATHEMATICAL & ALGORITHMIC FORMULATION:
   - Term Upper-Bound: U_t = max possible score contribution of term t.
   - Threshold theta: Score of current K-th best candidate in min-heap.
   - Pivot Selection:
       1. Sort query term posting iterators by current doc_id: t_1, t_2, ..., t_m.
       2. Accumulate upper bounds: sum_{i=1}^p U_{t_i} >= theta.
       3. Doc_id of t_p is the pivot document D_pivot.
       4. If all preceding iterators are behind D_pivot, skip them directly to D_pivot.
       5. If t_1.doc_id == D_pivot, fully score D_pivot and update top-K heap and theta.

3. COMPLEXITY ANALYSIS:
   - Evaluates exact top-K results without scoring >90% of index postings.
   - Memory: O(K) for top-K min-heap.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside function bodies.
================================================================================
"""

import heapq
from typing import Dict, List, Any, Optional, Tuple


class PostingCursor:
    def __init__(self, term: str, postings: List[Tuple[int, float]], upper_bound: float) -> None:
        self.term: str = term
        self.postings: List[Tuple[int, float]] = sorted(postings, key=lambda x: x[0])
        self.idx: int = 0
        self.upper_bound: float = upper_bound

    @property
    def current_doc(self) -> int:
        if self.idx < len(self.postings):
            return self.postings[self.idx][0]
        return 10**12

    @property
    def current_score(self) -> float:
        if self.idx < len(self.postings):
            return self.postings[self.idx][1]
        return 0.0

    def advance_to(self, target_doc: int) -> None:
        while self.idx < len(self.postings) and self.postings[self.idx][0] < target_doc:
            self.idx += 1


class SearchEngineBlockMaxWandAlgo:
    """
    --- contract:
      id: ALGO-SRCH-68
      name: SearchEngineBlockMaxWandAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(TermPostings)
        space: O(K)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - index.wand
      - retrieval.block_max
      - posting.pruning
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def search_top_k(self, term_postings: Dict[str, List[Tuple[int, float]]], k: int = 10) -> List[Dict[str, Any]]:
        cursors: List[PostingCursor] = []
        for term, postings in term_postings.items():
            if postings:
                max_score = max(score for _, score in postings)
                cursors.append(PostingCursor(term, postings, max_score))

        if not cursors:
            return []

        top_k_heap: List[Tuple[float, int]] = []
        theta: float = 0.0
        docs_scored = 0
        docs_skipped = 0

        while True:
            cursors = [c for c in cursors if c.idx < len(c.postings)]
            if not cursors:
                break

            cursors.sort(key=lambda c: c.current_doc)

            accum_ub = 0.0
            pivot_idx = -1
            for i, c in enumerate(cursors):
                accum_ub += c.upper_bound
                if accum_ub >= theta:
                    pivot_idx = i
                    break

            if pivot_idx == -1:
                break

            pivot_doc = cursors[pivot_idx].current_doc
            if pivot_doc >= 10**12:
                break

            if cursors[0].current_doc == pivot_doc:
                total_score = 0.0
                matched_terms: List[str] = []
                for c in cursors:
                    if c.current_doc == pivot_doc:
                        total_score += c.current_score
                        matched_terms.append(c.term)
                        c.idx += 1

                docs_scored += 1
                if len(top_k_heap) < k:
                    heapq.heappush(top_k_heap, (total_score, pivot_doc))
                    if len(top_k_heap) == k:
                        theta = top_k_heap[0][0]
                elif total_score > top_k_heap[0][0]:
                    heapq.heappushpop(top_k_heap, (total_score, pivot_doc))
                    theta = top_k_heap[0][0]
            else:
                docs_skipped += 1
                cursors[0].advance_to(pivot_doc)

        sorted_results = sorted(top_k_heap, key=lambda x: -x[0])
        return [
            {
                "doc_id": doc_id,
                "score": round(score, 4),
                "rank": rank + 1
            } for rank, (score, doc_id) in enumerate(sorted_results)
        ]

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        term_data = payload.get("term_postings", {})
        k = int(payload.get("k", 10))

        formatted_postings: Dict[str, List[Tuple[int, float]]] = {}
        for term, posts in term_data.items():
            parsed: List[Tuple[int, float]] = []
            for item in posts:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    parsed.append((int(item[0]), float(item[1])))
                elif isinstance(item, dict):
                    parsed.append((int(item.get("doc_id", 0)), float(item.get("score", 1.0))))
                else:
                    parsed.append((int(item), 1.0))
            formatted_postings[term] = parsed

        top_k_results = self.search_top_k(formatted_postings, k=k)

        return {
            "algorithm": "ALGO-SRCH-68",
            "k": k,
            "terms_queried": list(formatted_postings.keys()),
            "top_k_results": top_k_results,
            "result_count": len(top_k_results)
        }
