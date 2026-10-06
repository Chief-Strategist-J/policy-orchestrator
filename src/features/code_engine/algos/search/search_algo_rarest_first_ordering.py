"""
================================================================================
ALGORITHM BLUEPRINT: RAREST-FIRST QUERY PLANNING & OPTIMIZATION
================================================================================

1. OVERVIEW:
   Rarest-First Query Planning sorts conjunction query terms in ascending order
   of document frequency (DF) / posting list length. Evaluating the rarest, most
   selective term first shrinks the intermediate candidate set most aggressively,
   minimizing memory traffic and comparisons for subsequent posting list intersections.

2. MATHEMATICAL & ALGORITHMIC FORMULATION:
   - Input Terms: T = {t_1, t_2, ..., t_m} with document frequencies DF(t_i).
   - Ordering: Sort terms such that DF(t_(1)) <= DF(t_(2)) <= ... <= DF(t_(m)).
   - Execution Pipeline:
       1. Set Candidate_Set = PostingList(t_(1)).
       2. For i = 2 to m:
           If |Candidate_Set| == 0: break early (empty result).
           Candidate_Set = GallopingIntersect(Candidate_Set, PostingList(t_(i))).
       3. Return Candidate_Set.

3. COMPLEXITY ANALYSIS:
   - Reordering Time: O(M log M) where M is query term count.
   - Total Intersection Work: Reduced by up to 90%-99% compared to arbitrary term order.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside function bodies.
================================================================================
"""

from typing import Dict, List, Any, Optional, Tuple


class SearchEngineRarestFirstOrderingAlgo:
    """
    Implements query term selectivity sorting and rarest-first progressive intersection.
    """

    def plan_query(self, term_frequencies: Dict[str, int]) -> List[Tuple[str, int]]:
        """
        Orders terms by ascending document frequency (rarest first).
        """
        return sorted(term_frequencies.items(), key=lambda item: item[1])

    def execute_ordered_search(self, term_postings: Dict[str, List[int]]) -> Dict[str, Any]:
        """
        Plans and executes rarest-first intersection across posting lists.
        """
        if not term_postings:
            return {"plan": [], "result": [], "evaluated_count": 0}

        plan = sorted([(term, len(postings)) for term, postings in term_postings.items()], key=lambda x: x[1])

        if not plan:
            return {"plan": [], "result": [], "evaluated_count": 0}

        first_term = plan[0][0]
        current_set = set(term_postings[first_term])

        step_counts: List[Dict[str, Any]] = [{"term": first_term, "remaining_docs": len(current_set)}]

        for term, df in plan[1:]:
            if not current_set:
                break
            current_set &= set(term_postings[term])
            step_counts.append({"term": term, "remaining_docs": len(current_set)})

        return {
            "execution_plan": [{"term": t, "initial_df": df} for t, df in plan],
            "step_reduction": step_counts,
            "final_candidates": sorted(list(current_set)),
            "candidate_count": len(current_set)
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes rarest-first query planning and intersection simulation.
        """
        term_postings_raw = payload.get("term_postings", {})
        parsed_postings: Dict[str, List[int]] = {}
        for term, posts in term_postings_raw.items():
            parsed_postings[str(term)] = [int(x) for x in posts]

        result = self.execute_ordered_search(parsed_postings)

        return {
            "algorithm": "ALGO-SRCH-71",
            "search_summary": result
        }
