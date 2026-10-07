"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FRAUDAR CAMOUFLAGE-RESISTANT DENSE BLOCKS (ALGO-GRAPH-DENSE-130)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Fraudar camouflage-resistant dense bipartite fraud block detection algorithm.
   Detects suspicious coordinated groups (fake reviews, bot followers, click rings)
   in bipartite graphs by discounting edges to popular items by 1 / log(deg(item) + c).
   Guarantees camouflage invariance against fraudulent edge injections.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(m log n) priority tree peeling.
   - Space Complexity: O(V + E) bipartite structure.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - bipartite_edges: List[Tuple[TNode, TNode]] - List of (user_u, item_v) bipartite links.
   - log_discount_c: float - Smoothing constant c in 1 / log(deg + c) (default: 5.0).

4. OUTPUT PARAMETERS:
   - max_fraud_score: float - Normalized weighted density score of the suspicious block.
   - fraud_users: List[TNode] - Suspicious user accounts in the detected dense block.
   - targeted_items: List[TNode] - Targeted entities or items in the detected block.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Bipartite edge pairs.
   - Guardrails: Popular item logarithmic downweighting neutralizes organic camouflage noise.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoFraudarDenseBlocks(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DENSE-130
      name: GraphAlgoFraudarDenseBlocks
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, dense_structures, fraudar, fraud_detection, camouflage_resistant, bipartite_dense_blocks]
      inputs:
        type: object
        required: [bipartite_edges]
        properties:
          bipartite_edges:
            type: array
            items: {type: array, items: [{type: string}, {type: string}]}
          log_discount_c: {type: number, default: 5.0}
      outputs:
        type: object
        required: [max_fraud_score, fraud_users, targeted_items]
        properties:
          max_fraud_score: {type: number}
          fraud_users: {type: array, items: {type: string}}
          targeted_items: {type: array, items: {type: string}}
      parameters:
        log_discount_c: {type: number, default: 5.0}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(m log n)
        space: O(V + E)
    ---
    """

    def __init__(
        self,
        bipartite_edges: List[Tuple[TNode, TNode]],
        log_discount_c: float = 5.0,
    ) -> None:
        """
        Initialize the Fraudar dense block detector.

        Args:
            bipartite_edges: List of (user, item) directed bipartite edges.
            log_discount_c: Logarithmic damping constant.
        """
        self._edges: List[Tuple[TNode, TNode]] = bipartite_edges
        self._c: float = log_discount_c

    def detect_fraud_block(self) -> Tuple[float, List[TNode], List[TNode]]:
        """
        Execute Fraudar peeling to identify the densest fraud block.

        Returns:
            Tuple of (max_fraud_score, fraud_user_list, targeted_item_list).
        """
        if not self._edges:
            return 0.0, [], []

        users: Set[TNode] = {u for u, _ in self._edges}
        items: Set[TNode] = {v for _, v in self._edges}

        user_adj: Dict[TNode, Set[TNode]] = {u: set() for u in users}
        item_adj: Dict[TNode, Set[TNode]] = {v: set() for v in items}

        for u, v in self._edges:
            user_adj[u].add(v)
            item_adj[v].add(u)

        item_weights: Dict[TNode, float] = {v: 1.0 / math.log(len(item_adj[v]) + self._c) for v in items}

        curr_user_weights: Dict[TNode, float] = {u: sum(item_weights[v] for v in user_adj[u]) for u in users}
        curr_item_weights: Dict[TNode, float] = {v: item_weights[v] * len(item_adj[v]) for v in items}

        total_weight: float = sum(curr_user_weights.values())
        rem_users: Set[TNode] = set(users)
        rem_items: Set[TNode] = set(items)

        best_score: float = total_weight / float(len(rem_users) + len(rem_items))
        best_users: Set[TNode] = set(rem_users)
        best_items: Set[TNode] = set(rem_items)

        while rem_users and rem_items:
            min_u = min(rem_users, key=lambda u: curr_user_weights[u])
            min_v = min(rem_items, key=lambda v: curr_item_weights[v])

            if curr_user_weights[min_u] <= curr_item_weights[min_v]:
                for v in user_adj[min_u]:
                    if v in rem_items:
                        item_adj[v].remove(min_u)
                        curr_item_weights[v] -= item_weights[v]
                        total_weight -= item_weights[v]
                rem_users.remove(min_u)
            else:
                for u in item_adj[min_v]:
                    if u in rem_users:
                        user_adj[u].remove(min_v)
                        curr_user_weights[u] -= item_weights[min_v]
                        total_weight -= item_weights[min_v]
                rem_items.remove(min_v)

            if rem_users and rem_items:
                denom = float(len(rem_users) + len(rem_items))
                score = total_weight / denom
                if score > best_score:
                    best_score = score
                    best_users = set(rem_users)
                    best_items = set(rem_items)

        return best_score, sorted(list(best_users), key=lambda x: str(x)), sorted(list(best_items), key=lambda x: str(x))
