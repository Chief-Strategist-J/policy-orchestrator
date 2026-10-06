"""
================================================================================
ALGORITHM BLUEPRINT: GALLOPING (EXPONENTIAL SEARCH) INTERSECTION
================================================================================

1. OVERVIEW:
   Galloping (Exponential Search / Doubling Search) Intersection is an asymmetric
   set intersection algorithm optimized for cases where one list is significantly
   shorter than the other (|A| << |B|). Instead of scanning sequentially through the
   longer list, it performs exponential jumps (+1, +2, +4, +8, ...) followed by binary
   search in the localized range, reducing comparison count dramatically.

2. MATHEMATICAL & ALGORITHMIC FORMULATION:
   - For each element x in short list A:
       1. In list B, starting from index j, test offsets: 2^0, 2^1, 2^2, ...
       2. Find k such that B[j + 2^(k-1)] < x <= B[min(len(B)-1, j + 2^k)].
       3. Perform binary search for x in range [j + 2^(k-1), min(len(B)-1, j + 2^k)].
       4. If found, emit x. Update j to the insertion/found position.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(|A| * log(|B| / |A|)) comparisons.
   - When |A| = 10 and |B| = 1,000,000, evaluates ~150 comparisons vs 1,000,000 in linear merge.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method/function bodies.
================================================================================
"""

import bisect
from typing import Dict, List, Any, Optional


class SearchEngineGallopingIntersectionAlgo:
    """
    --- contract:
      id: ALGO-SRCH-66
      name: SearchEngineGallopingIntersectionAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(M * log(N/M))
        space: O(Results)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - posting.galloping
      - search.intersection
      - index.skip
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def intersect_galloping(self, short_list: List[int], long_list: List[int]) -> List[int]:
        if not short_list or not long_list:
            return []

        if len(short_list) > len(long_list):
            short_list, long_list = long_list, short_list

        result: List[int] = []
        curr_b_idx = 0
        len_b = len(long_list)

        for target in short_list:
            if curr_b_idx >= len_b:
                break
            if long_list[curr_b_idx] == target:
                result.append(target)
                curr_b_idx += 1
                continue

            jump = 1
            low = curr_b_idx
            high = curr_b_idx + jump

            while high < len_b and long_list[high] < target:
                low = high
                jump *= 2
                high = curr_b_idx + jump

            high = min(high, len_b - 1)
            idx = bisect.bisect_left(long_list, target, low, high + 1)
            if idx < len_b and long_list[idx] == target:
                result.append(target)
                curr_b_idx = idx + 1
            else:
                curr_b_idx = idx

        return result

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        list_a = sorted([int(x) for x in payload.get("list_a", [])])
        list_b = sorted([int(x) for x in payload.get("list_b", [])])

        intersection = self.intersect_galloping(list_a, list_b)

        return {
            "algorithm": "ALGO-SRCH-66",
            "size_a": len(list_a),
            "size_b": len(list_b),
            "is_unbalanced": abs(len(list_a) - len(list_b)) > 5,
            "intersection": intersection,
            "match_count": len(intersection)
        }
