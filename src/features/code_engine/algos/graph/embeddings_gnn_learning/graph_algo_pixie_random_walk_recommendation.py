"""ALGORITHM & ARCHITECTURE BLUEPRINT: PIXIE REAL-TIME RANDOM WALK RECOMMENDATION (ALGO-GRAPH-RANK-287)

1. OVERVIEW & OBJECTIVE
Pixie (Eksombatchai et al., Pinterest) is a high-throughput, graph-based real-time recommendation engine.
Given multiple query/seed vertices with associated weights, Pixie executes biased random walks with early
stopping criteria (terminating individual walk steps when visit counts exceed confidence thresholds) and
aggregates visit counts across bipartite query boards/pins to generate low-latency top-K item recommendations.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V_visited| + N_query) storing sparse visit counter dictionaries.
- Time Complexity: O(sum_{q in Query} N_steps(q)) bounded random walk simulation.
- Invariants:
  - Query nodes receive walk budgets proportional to input weights: N_steps(q) = N_total * w_q / sum(w).
  - High-degree neighbor scaling penalizes ubiquitous hub nodes: P(v|u) proportional to 1 / sqrt(deg(v)).

3. INPUT PARAMETERS:
- bipartite_adjacency: Mapping[TNode, Collection[TNode]] user-to-item or board-to-pin graph topology.
- query_seeds: Mapping[TNode, float] query nodes and positive importance weights.
- num_total_steps: int total random walk step budget across all query seeds.
- alpha: float restart probability back to the active query seed (default 0.5).
- max_visits_early_stop: int threshold of visits for a single node to trigger early walk pruning.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'recommendations': List[tuple[TNode, float]] top-K ranked items sorted by normalized visit score.
  - 'visit_counts': Dict[TNode, int] raw visit frequencies per node.
  - 'total_steps_executed': int total walk steps evaluated.

5. AGENT CONTRACT:
- Strict zero-inline-comment doctrine.
- Generic node typing via `TNode`.
"""

from __future__ import annotations

import collections
import math
import random
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoPixieRandomWalkRecommendation(Generic[TNode]):
    """Pixie real-time random walk recommendation engine with biased sampling and early stopping.

    ```yaml
    contract:
      id: ALGO-GRAPH-RANK-287
      name: GraphAlgoPixieRandomWalkRecommendation
      inputs:
        - name: bipartite_adjacency
          type: Mapping[TNode, Collection[TNode]]
          description: Undirected or bipartite graph adjacency.
        - name: query_seeds
          type: Mapping[TNode, float]
          description: Seed nodes and non-negative query weights.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Ranked recommended items, raw visit counts, and step metrics.
      parameters:
        num_total_steps: int (default 10000)
        alpha: float (default 0.5)
        max_visits_early_stop: int (default 2000)
        top_k: int (default 20)
        seed: int (default 42)
      capability_tags:
        - RECOMMENDATION
        - PIXIE
        - RANDOM_WALKS
        - EARLY_STOPPING
      purity: DETERMINISTIC_WITH_SEED
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(N_steps)
        space: O(|V_visited|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        bipartite_adjacency: Mapping[TNode, Collection[TNode]],
        query_seeds: Mapping[TNode, float],
        num_total_steps: int = 10000,
        alpha: float = 0.5,
        max_visits_early_stop: int = 2000,
        top_k: int = 20,
        seed: int = 42,
    ) -> Dict[str, Any]:
        """Executes multi-seed Pixie random walks with degree-biased transitions and early stopping."""
        rng = random.Random(seed)
        valid_seeds = {q: max(0.0, float(w)) for q, w in query_seeds.items() if q in bipartite_adjacency}
        total_weight = sum(valid_seeds.values())
        if not valid_seeds or total_weight <= 0.0:
            return {"recommendations": [], "visit_counts": {}, "total_steps_executed": 0}

        degrees: Dict[TNode, int] = {
            u: len(nbrs) for u, nbrs in bipartite_adjacency.items()
        }

        total_visit_counts: collections.Counter[TNode] = collections.Counter()
        steps_executed = 0

        for q, w in valid_seeds.items():
            allocated_steps = int(num_total_steps * (w / total_weight))
            curr = q
            steps_for_q = 0

            while steps_for_q < allocated_steps:
                steps_for_q += 1
                steps_executed += 1

                if rng.random() < alpha:
                    curr = q
                    continue

                nbrs = list(bipartite_adjacency.get(curr, []))
                if not nbrs:
                    curr = q
                    continue

                weights = [1.0 / math.sqrt(max(1.0, float(degrees.get(v, 1)))) for v in nbrs]
                tot_w = sum(weights)
                thresh = rng.random() * tot_w
                running = 0.0
                next_node = nbrs[-1]
                for v, weight in zip(nbrs, weights):
                    running += weight
                    if running >= thresh:
                        next_node = v
                        break

                curr = next_node
                if curr not in valid_seeds:
                    total_visit_counts[curr] += 1
                    if total_visit_counts[curr] >= max_visits_early_stop:
                        break

        total_visits = sum(total_visit_counts.values())
        scored_items: List[Tuple[TNode, float]] = []

        for u, cnt in total_visit_counts.items():
            scaled_score = (float(cnt) / max(1.0, float(total_visits))) / math.sqrt(max(1.0, float(degrees.get(u, 1))))
            scored_items.append((u, scaled_score))

        scored_items.sort(key=lambda x: x[1], reverse=True)
        top_recommendations = scored_items[:top_k]

        return {
            "recommendations": top_recommendations,
            "visit_counts": dict(total_visit_counts),
            "total_steps_executed": steps_executed,
        }
