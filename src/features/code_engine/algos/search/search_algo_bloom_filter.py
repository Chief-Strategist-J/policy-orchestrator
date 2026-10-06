"""
================================================================================
ALGORITHM BLUEPRINT: BLOOM FILTER (PROBABILISTIC MEMBERSHIP FILTER)
================================================================================

1. OVERVIEW:
   A Bloom Filter is a space-efficient probabilistic data structure that tests
   set membership. It returns either "definitely not present" (with zero false
   negatives) or "maybe present" (with a tunable, mathematically bounded false
   positive probability). Widely utilized for skipping non-matching file shards,
   pre-filtering expensive disk lookups, and accelerating code symbol queries.

2. MATHEMATICAL FORMULATION:
   - Bit Array: Size M initialized to all 0s.
   - Hash Functions: K independent universal hash functions h_1, h_2, ..., h_k:
     h_i(x) = (hash(x) + i * hash_2(x)) mod M (Kirsch-Mitzenmacher optimization).
   - Insertion: For item x, set bits A[h_i(x)] = 1 for all 1 <= i <= K.
   - Membership Check: Item y is in set only if A[h_i(y)] == 1 for all 1 <= i <= K.
   - Optimal K: K = (M / N) * ln(2) where N is the expected number of elements.
   - False Positive Rate: p = (1 - e^(-K * N / M))^K.

3. COMPLEXITY ANALYSIS:
   - Insertion Time: O(K).
   - Query Time: O(K).
   - Space Complexity: O(M) bits (typically 10 bits per item for ~1% FPR).

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Pure, deterministic calculation with 0 inline comments inside function bodies.
================================================================================
"""

import math
import hashlib
from typing import Dict, List, Any, Optional


class SearchEngineBloomFilterAlgo:
    """
    --- contract:
      id: ALGO-SRCH-57
      name: SearchEngineBloomFilterAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(K)
        space: O(M)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - filter.bloom
      - probabilistic.membership
      - hash.filter
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def __init__(self, expected_elements: int = 1000, false_positive_rate: float = 0.01) -> None:
        self._expected_elements: int = max(1, expected_elements)
        self._target_fpr: float = max(0.0001, min(0.5, false_positive_rate))
        self._bit_size: int = self._calculate_bit_size(self._expected_elements, self._target_fpr)
        self._num_hashes: int = self._calculate_num_hashes(self._bit_size, self._expected_elements)
        self._bit_array: List[int] = [0] * self._bit_size
        self._count: int = 0

    def _calculate_bit_size(self, n: int, p: float) -> int:
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return max(8, int(math.ceil(m)))

    def _calculate_num_hashes(self, m: int, n: int) -> int:
        k = (m / n) * math.log(2)
        return max(1, int(round(k)))

    def _get_hashes(self, item: str) -> List[int]:
        item_bytes = item.encode("utf-8")
        h1 = int(hashlib.md5(item_bytes).hexdigest()[:8], 16)
        h2 = int(hashlib.sha1(item_bytes).hexdigest()[:8], 16)

        indices: List[int] = []
        for i in range(self._num_hashes):
            idx = (h1 + i * h2) % self._bit_size
            indices.append(idx)
        return indices

    def add(self, item: str) -> None:
        for idx in self._get_hashes(item):
            self._bit_array[idx] = 1
        self._count += 1

    def contains(self, item: str) -> bool:
        for idx in self._get_hashes(item):
            if self._bit_array[idx] == 0:
                return False
        return True

    def estimated_false_positive_rate(self) -> float:
        if self._bit_size == 0 or self._count == 0:
            return 0.0
        exp_val = - (self._num_hashes * self._count) / self._bit_size
        return float((1.0 - math.exp(exp_val)) ** self._num_hashes)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        expected = int(payload.get("expected_elements", 1000))
        target_fpr = float(payload.get("false_positive_rate", 0.01))
        items_to_add = payload.get("add_items", [])
        query_items = payload.get("query_items", [])

        if expected != self._expected_elements or abs(target_fpr - self._target_fpr) > 1e-5:
            self._expected_elements = max(1, expected)
            self._target_fpr = max(0.0001, min(0.5, target_fpr))
            self._bit_size = self._calculate_bit_size(self._expected_elements, self._target_fpr)
            self._num_hashes = self._calculate_num_hashes(self._bit_size, self._expected_elements)
            self._bit_array = [0] * self._bit_size
            self._count = 0

        for it in items_to_add:
            self.add(str(it))

        query_results: Dict[str, bool] = {}
        for q in query_items:
            s_q = str(q)
            query_results[s_q] = self.contains(s_q)

        return {
            "algorithm": "ALGO-SRCH-57",
            "bit_size": self._bit_size,
            "num_hashes": self._num_hashes,
            "inserted_count": self._count,
            "bits_set": sum(self._bit_array),
            "estimated_fpr": self.estimated_false_positive_rate(),
            "query_results": query_results
        }
