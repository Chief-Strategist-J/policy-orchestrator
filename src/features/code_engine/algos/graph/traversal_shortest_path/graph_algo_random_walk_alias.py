"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: RANDOM WALK WITH ALIAS SAMPLING (ALGO-GRAPH-TRV-18)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Generates stochastic node sequences across weighted graphs using Vose's Alias
   method for O(1) step sampling. Supports random walks with restart (RWR),
   teleportation probabilities, and deterministic pseudo-random seeds for
   Node2Vec/DeepWalk embeddings, PageRank estimation, and graph sampling.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E) alias table setup, O(walk_length) per walk.
   - Space Complexity: O(V + E) for probability tables and alias arrays.
   - Purity: Pure functional transformation with deterministic seeds.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Rules: Fixed seed (GR5) ensures 100% reproducible walk sequences.
================================================================================
"""

from __future__ import annotations
import random
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoRandomWalkAlias(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TRV-18
      name: GraphAlgoRandomWalkAlias
      version: 1.0.0
      category: graph_traversal
      capability_tags: [graph, traversal, random_walk, alias_method, node2vec_sampling]
      inputs:
        type: object
        required: [weighted_adjacency, start_node]
        properties:
          weighted_adjacency:
            type: object
            additionalProperties:
              type: array
              items:
                type: object
                required: [target, weight]
                properties:
                  target: {type: string}
                  weight: {type: number}
          start_node: {type: string}
      outputs:
        type: object
        required: [walk_sequence, walk_length, visited_unique_nodes, transition_counts]
      parameters:
        walk_length: {type: integer, default: 20}
        restart_prob: {type: number, default: 0.15}
        seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E + L)
        space: O(V + E)
    ---
    """

    @staticmethod
    def generate_walk(
        weighted_adjacency: Dict[str, List[Dict[str, Any]]],
        start_node: str,
        walk_length: int = 20,
        restart_prob: float = 0.15,
        seed: int = 42,
    ) -> Dict[str, Any]:
        rng = random.Random(seed)
        all_nodes = sorted(list(weighted_adjacency.keys()))

        alias_tables: Dict[str, Tuple[List[float], List[int], List[str]]] = {}
        for u, edges in weighted_adjacency.items():
            if edges:
                targets = [e["target"] for e in edges]
                weights = [float(e.get("weight", 1.0)) for e in edges]
                prob, alias = GraphAlgoRandomWalkAlias._create_alias_table(weights)
                alias_tables[u] = (prob, alias, targets)

        curr = start_node
        walk: List[str] = [curr]
        transition_counts: Dict[Tuple[str, str], int] = {}

        for _ in range(walk_length - 1):
            if rng.random() < restart_prob or curr not in alias_tables:
                next_node = start_node
            else:
                prob, alias, targets = alias_tables[curr]
                k = len(targets)
                idx = rng.randint(0, k - 1)
                chosen_idx = idx if rng.random() < prob[idx] else alias[idx]
                next_node = targets[chosen_idx]

            pair = (curr, next_node)
            transition_counts[pair] = transition_counts.get(pair, 0) + 1
            walk.append(next_node)
            curr = next_node

        return {
            "walk_sequence": walk,
            "walk_length": len(walk),
            "visited_unique_nodes": len(set(walk)),
            "transition_counts": {f"{k[0]}->{k[1]}": v for k, v in sorted(transition_counts.items())},
            "seed": seed,
        }

    @staticmethod
    def _create_alias_table(weights: List[float]) -> Tuple[List[float], List[int]]:
        n = len(weights)
        total = sum(weights)
        if total <= 0:
            return [1.0] * n, list(range(n))

        norm_weights = [w * n / total for w in weights]
        small: List[int] = []
        large: List[int] = []

        for i, nw in enumerate(norm_weights):
            if nw < 1.0:
                small.append(i)
            else:
                large.append(i)

        prob = [1.0] * n
        alias = [0] * n

        while small and large:
            s = small.pop()
            l = large.pop()

            prob[s] = norm_weights[s]
            alias[s] = l

            norm_weights[l] = (norm_weights[l] + norm_weights[s]) - 1.0
            if norm_weights[l] < 1.0:
                small.append(l)
            else:
                large.append(l)

        return prob, alias
