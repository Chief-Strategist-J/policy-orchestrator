"""
================================================================================
ALGORITHM BLUEPRINT: MERGE INTERSECTION (TWO-POINTER POSTING LIST INTERSECTION)
================================================================================

1. OVERVIEW:
   Merge Intersection is a foundational posting list set operation that computes
   the exact intersection of two or more sorted integer sequences using coordinated
   linear pointer traversal. Essential for evaluating boolean AND queries in
   inverted search indexes.

2. MATHEMATICAL & ALGORITHMIC FORMULATION:
   - Input: Sorted lists A of size M and B of size N.
   - Pointers: i = 0 (for A), j = 0 (for B).
   - Execution Loop:
       While i < M and j < N:
           If A[i] == B[j]:
               emit A[i]
               i += 1; j += 1
           Else if A[i] < B[j]:
               i += 1
           Else:
               j += 1
   - Multi-list Intersection:
       Iteratively intersect lists pairwise in order of increasing length (rarest first).

3. COMPLEXITY ANALYSIS:
   - Time: O(|A| + |B|) comparisons.
   - Space: O(min(|A|, |B|)) output memory.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments in function bodies.
================================================================================
"""

from typing import Dict, List, Any, Optional


class SearchEngineMergeIntersectionAlgo:
    """
    Implements two-pointer sorted list intersection and multi-way list merge.
    """

    def intersect_pair(self, list_a: List[int], list_b: List[int]) -> List[int]:
        """
        Computes intersection of two sorted lists via two-pointer scan.
        """
        i = 0
        j = 0
        len_a = len(list_a)
        len_b = len(list_b)
        result: List[int] = []

        while i < len_a and j < len_b:
            val_a = list_a[i]
            val_b = list_b[j]
            if val_a == val_b:
                result.append(val_a)
                i += 1
                j += 1
            elif val_a < val_b:
                i += 1
            else:
                j += 1

        return result

    def intersect_multiple(self, lists: List[List[int]]) -> List[int]:
        """
        Intersects multiple sorted lists, optimizing order by evaluating shortest lists first.
        """
        if not lists:
            return []
        if len(lists) == 1:
            return sorted(lists[0])

        sorted_by_len = sorted(lists, key=len)
        current = sorted_by_len[0]

        for next_list in sorted_by_len[1:]:
            current = self.intersect_pair(current, next_list)
            if not current:
                break

        return current

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes merge intersection across provided sorted lists.
        """
        lists_raw = payload.get("lists", [])
        parsed_lists: List[List[int]] = []
        for lst in lists_raw:
            parsed_lists.append(sorted([int(x) for x in lst]))

        intersection_result = self.intersect_multiple(parsed_lists)

        return {
            "algorithm": "ALGO-SRCH-65",
            "input_list_count": len(parsed_lists),
            "input_sizes": [len(l) for l in parsed_lists],
            "intersection": intersection_result,
            "intersection_count": len(intersection_result)
        }
