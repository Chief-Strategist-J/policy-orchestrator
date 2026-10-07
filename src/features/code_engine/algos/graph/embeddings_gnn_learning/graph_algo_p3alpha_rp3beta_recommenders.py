"""ALGORITHM & ARCHITECTURE BLUEPRINT: P3ALPHA & RP3BETA RANDOM WALK RECOMMENDERS (ALGO-GRAPH-RANK-288)

1. OVERVIEW & OBJECTIVE
P3alpha and RP3beta are state-of-the-art item-based collaborative filtering algorithms based on 3-step random walks
on bipartite user-item graphs (Item -> User -> Item). P3alpha parameterizes transition probabilities via
exponent alpha (P_{ij}^alpha), while RP3beta explicitly downweights popular item recommendations by dividing
transition probabilities by the item degree raised to power beta (P3alpha_{ij} / deg(item_j)^beta), maximizing
accuracy and catalog recommendation novelty.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|Users| * |Items| + |E|) bipartite adjacency representation.
- Time Complexity: O(|Items| * deg_avg(Item)^2 * deg_avg(User)) 3-step transition evaluation.
- Invariants:
  - Transition matrix P_{item -> user} is row-normalized by user-item degrees.
  - RP3beta applies degree penalization strictly to target destination item nodes.

3. INPUT PARAMETERS:
- user_item_interactions: Mapping[TNode, Collection[TNode]] user-to-item bipartite interactions.
- target_user: TNode target user for recommendation.
- alpha: float degree transition exponent (e.g. 1.0 or 1.2).
- beta: float item degree popularity penalization exponent (0.0 for P3alpha, > 0 for RP3beta).
- top_k: int number of recommended items to return.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'recommendations': List[tuple[TNode, float]] top-K recommended items and computed scores.
  - 'interacted_items': Set[TNode] historical items excluded from recommendation.
  - 'algorithm_variant': str 'RP3beta' if beta > 0 else 'P3alpha'.

5. AGENT CONTRACT:
- Strict zero-inline-comment rule.
- Pure numeric computation.
"""

from __future__ import annotations

import collections
import math
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoP3alphaRp3betaRecommenders(Generic[TNode]):
    """P3alpha and RP3beta 3-step random walk collaborative filtering recommender.

    ```yaml
    contract:
      id: ALGO-GRAPH-RANK-288
      name: GraphAlgoP3alphaRp3betaRecommenders
      inputs:
        - name: user_item_interactions
          type: Mapping[TNode, Collection[TNode]]
          description: Mapping of user IDs to interacted item sets.
        - name: target_user
          type: TNode
          description: Target user for recommendation query.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Ranked recommended items and variant metadata.
      parameters:
        alpha: float (default 1.0)
        beta: float (default 0.6)
        top_k: int (default 10)
      capability_tags:
        - RECOMMENDATION
        - P3ALPHA
        - RP3BETA
        - 3_STEP_RANDOM_WALK
        - COLLABORATIVE_FILTERING
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(|Items| * deg_avg^2)
        space: O(|V| + |E|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        user_item_interactions: Mapping[TNode, Collection[TNode]],
        target_user: TNode,
        alpha: float = 1.0,
        beta: float = 0.6,
        top_k: int = 10,
    ) -> Dict[str, Any]:
        """Calculates 3-step item recommendation scores for target user."""
        user_items: Dict[TNode, Set[TNode]] = {
            u: set(items) for u, items in user_item_interactions.items()
        }

        item_users: Dict[TNode, Set[TNode]] = collections.defaultdict(set)
        for u, items in user_items.items():
            for it in items:
                item_users[it].add(u)

        target_items = user_items.get(target_user, set())
        if not target_items:
            return {
                "recommendations": [],
                "interacted_items": set(),
                "algorithm_variant": "RP3beta" if beta > 0.0 else "P3alpha",
            }

        item_degrees: Dict[TNode, int] = {it: len(users) for it, users in item_users.items()}
        user_degrees: Dict[TNode, int] = {u: len(items) for u, items in user_items.items()}

        candidate_scores: Dict[TNode, float] = collections.defaultdict(float)

        for seed_item in target_items:
            deg_seed = item_degrees.get(seed_item, 1)
            p_item_to_users = 1.0 / math.pow(max(1.0, float(deg_seed)), alpha) if deg_seed > 0 else 0.0

            for user in item_users[seed_item]:
                deg_user = user_degrees.get(user, 1)
                p_user_to_items = 1.0 / math.pow(max(1.0, float(deg_user)), alpha) if deg_user > 0 else 0.0

                trans_weight = p_item_to_users * p_user_to_items

                for target_item in user_items[user]:
                    if target_item not in target_items:
                        candidate_scores[target_item] += trans_weight

        if beta > 0.0:
            for item in list(candidate_scores.keys()):
                deg_target = item_degrees.get(item, 1)
                candidate_scores[item] = candidate_scores[item] / math.pow(max(1.0, float(deg_target)), beta)

        sorted_recs = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
        top_recs = sorted_recs[:top_k]

        return {
            "recommendations": top_recs,
            "interacted_items": target_items,
            "algorithm_variant": "RP3beta" if beta > 0.0 else "P3alpha",
        }
