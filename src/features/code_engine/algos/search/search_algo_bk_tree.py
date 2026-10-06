"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BURKHARD-KELLER METRIC TREE (BK-TREE) (ALGO 30)
================================================================================

1. OVERVIEW & OBJECTIVE:
   A discrete metric tree data structure designed for fast nearest-neighbor
   and range queries in metric spaces satisfying the triangle inequality:
   d(x, z) <= d(x, y) + d(y, z). Operates over Levenshtein distance to prune
   massive dictionary searches, visiting only subtrees within [d - k, d + k].

2. COMPLEXITY & INVARIANTS:
   - Tree Construction: O(N * log N * L^2) average time | Space O(N).
   - Range Query (radius K): O(N^(1 - 1/K)) average time, sub-linear pruning.
   - Purity & Determinism: 100% pure and deterministic.
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - Root is initialized with the first inserted word.
   - Inserting word W: computes distance D to current node. If child at edge D
     exists, recurse down child; otherwise, add new node at edge D.
   - Querying word Q with radius K:
     * Compute distance D = dist(Q, current_node.word).
     * If D <= K, add current_node.word to matches.
     * Prune search to only explore children with edge distance in [D - K, D + K].
================================================================================
"""

from typing import List, Dict, Any, Tuple, Optional


def _levenshtein(s1: str, s2: str) -> int:
    if s1 == s2:
        return 0
    if len(s1) == 0:
        return len(s2)
    if len(s2) == 0:
        return len(s1)

    v0 = list(range(len(s2) + 1))
    v1 = [0] * (len(s2) + 1)

    for i in range(len(s1)):
        v1[0] = i + 1
        for j in range(len(s2)):
            cost = 0 if s1[i] == s2[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        v0[:] = v1[:]

    return v0[len(s2)]


class BKTreeNode:
    def __init__(self, word: str) -> None:
        self.word = word
        self.children: Dict[int, BKTreeNode] = {}


class SearchEngineBkTreeAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-30
      name: SearchEngineBkTreeAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - search.metric_tree
      - search.bk_tree
      - fuzzy.spelling_correction
      inputs:
        type: object
        required:
        - dictionary
        properties:
          dictionary:
            type: array
            items:
              type: string
      outputs:
        type: array
        items:
          type: object
          required:
          - word
          - distance
          properties:
            word:
              type: string
            distance:
              type: integer
      parameters:
        type: object
        required:
        - query
        properties:
          query:
            type: string
            minLength: 1
          max_distance:
            type: integer
            default: 2
            minimum: 0
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(N^alpha)
        space: O(N)
    ---
    """

    def __init__(self, words: Optional[List[str]] = None) -> None:
        self.root: Optional[BKTreeNode] = None
        if words:
            for w in words:
                self.insert(w)

    def insert(self, word: str) -> None:
        if self.root is None:
            self.root = BKTreeNode(word)
            return

        curr = self.root
        while True:
            dist = _levenshtein(word, curr.word)
            if dist == 0:
                return
            if dist in curr.children:
                curr = curr.children[dist]
            else:
                curr.children[dist] = BKTreeNode(word)
                break

    def query(self, target: str, max_distance: int = 2) -> List[Dict[str, Any]]:
        if self.root is None:
            return []

        results: List[Dict[str, Any]] = []
        stack = [self.root]

        while stack:
            node = stack.pop()
            d = _levenshtein(target, node.word)
            if d <= max_distance:
                results.append({
                    "word": node.word,
                    "distance": d,
                })

            low = max(0, d - max_distance)
            high = d + max_distance

            for edge_dist, child_node in node.children.items():
                if low <= edge_dist <= high:
                    stack.append(child_node)

        results.sort(key=lambda x: (x["distance"], x["word"]))
        return results

    @classmethod
    def execute(
        cls,
        dictionary: List[str],
        query: str,
        max_distance: int = 2,
    ) -> List[Dict[str, Any]]:
        tree = cls(words=dictionary)
        return tree.query(target=query, max_distance=max_distance)
