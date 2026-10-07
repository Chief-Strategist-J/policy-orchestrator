"""ALGORITHM & ARCHITECTURE BLUEPRINT: LAYER-WISE NEIGHBOR SAMPLING (FASTGCN & LADIES) (ALGO-GRAPH-GNN-268)

1. OVERVIEW & OBJECTIVE
Layer-Wise Neighbor Sampling addresses neighbor explosion in large-scale Graph Neural Network training
by sampling a fixed number of nodes per layer independently (FastGCN) or conditioned on upper layers
using Layer-Dependent Importance Sampling (LADIES), computing unbiased Monte Carlo estimators for inter-layer
graph convolution operations.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(L * S * d + |E_sampled|) where L is layer count, S is sample budget per layer.
- Time Complexity: O(L * S * deg_avg) per batch evaluation.
- Invariants:
  - Importance probabilities sum to 1.0 across active candidate node sets.
  - Normalized adjacency submatrices are properly scaled to eliminate estimation bias.

3. INPUT PARAMETERS:
- adjacency: Mapping[TNode, Collection[TNode]] graph topology.
- target_nodes: Collection[TNode] seed nodes for the final evaluation layer.
- layer_sample_sizes: Sequence[int] number of nodes to sample at each GNN layer.
- method: str 'fastgcn' (degree-based i.i.d.) or 'ladies' (layer-dependent laplacian).

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'layer_nodes': List[List[TNode]] sampled node sets per layer from input to output.
  - 'subgraph_edges': List[tuple[TNode, TNode, float]] scaled edge weights for GNN propagation.
  - 'sampling_probabilities': Dict[TNode, float] computed sampling probabilities.

5. AGENT CONTRACT:
- Fully generic over node identifier type `TNode`.
- Zero inline comment rule strictly adhered to.
"""

from __future__ import annotations

import math
import random
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Sequence, Set, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoLayerwiseNeighborSampling(Generic[TNode]):
    """Layer-Wise Neighbor Sampling (FastGCN & LADIES) for scalable graph representation learning.

    ```yaml
    contract:
      id: ALGO-GRAPH-GNN-268
      name: GraphAlgoLayerwiseNeighborSampling
      inputs:
        - name: adjacency
          type: Mapping[TNode, Collection[TNode]]
          description: Graph adjacency dictionary.
        - name: target_nodes
          type: Collection[TNode]
          description: Seed nodes requiring output representations.
        - name: layer_sample_sizes
          type: Sequence[int]
          description: Per-layer sample budgets S_l from layer L down to layer 0.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Sampled bipartite subgraphs, layer node sets, and normalization weights.
      parameters:
        method: str (default 'ladies', options 'fastgcn', 'ladies')
        seed: int (default 42)
      capability_tags:
        - GNN_SCALING
        - LAYERWISE_SAMPLING
        - LADIES_FASTGCN
      purity: DETERMINISTIC_WITH_SEED
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(L * S * deg_avg)
        space: O(L * S * d + |E_sampled|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        adjacency: Mapping[TNode, Collection[TNode]],
        target_nodes: Collection[TNode],
        layer_sample_sizes: Sequence[int],
        method: str = "ladies",
        seed: int = 42,
    ) -> Dict[str, Any]:
        """Performs layer-dependent or independent sampling for GNN mini-batching."""
        rng = random.Random(seed)
        all_nodes: List[TNode] = list(adjacency.keys())
        if not all_nodes or not target_nodes:
            return {
                "layer_nodes": [],
                "subgraph_edges": [],
                "sampling_probabilities": {},
            }

        degrees: Dict[TNode, int] = {u: max(1, len(adjacency.get(u, []))) for u in all_nodes}
        global_prob: Dict[TNode, float] = {}
        total_deg_sq: float = sum(float(degrees[u] ** 2) for u in all_nodes)
        for u in all_nodes:
            global_prob[u] = (float(degrees[u] ** 2)) / max(1.0, total_deg_sq)

        layers: List[List[TNode]] = [list(target_nodes)]
        subgraph_edges: List[tuple[TNode, TNode, float]] = []
        sampling_probs_record: Dict[TNode, float] = {}

        current_layer_nodes = list(target_nodes)

        for budget in layer_sample_sizes:
            if method == "fastgcn":
                population = all_nodes
                weights = [global_prob[u] for u in population]
                sampled = self._sample_without_replacement(population, weights, budget, rng)
            else:
                neighbor_candidates: Set[TNode] = set()
                candidate_weights: Dict[TNode, float] = {}
                for v in current_layer_nodes:
                    deg_v = degrees.get(v, 1)
                    inv_sqrt_dv = 1.0 / math.sqrt(float(deg_v))
                    for u in adjacency.get(v, []):
                        neighbor_candidates.add(u)
                        deg_u = degrees.get(u, 1)
                        weight_uv = inv_sqrt_dv * (1.0 / math.sqrt(float(deg_u)))
                        candidate_weights[u] = candidate_weights.get(u, 0.0) + (weight_uv ** 2)

                if not neighbor_candidates:
                    neighbor_candidates = set(current_layer_nodes)
                    candidate_weights = {u: 1.0 for u in current_layer_nodes}

                cand_list = list(neighbor_candidates)
                total_w = sum(candidate_weights.get(u, 1.0) for u in cand_list)
                cand_probs = [candidate_weights.get(u, 1.0) / max(1e-12, total_w) for u in cand_list]
                for u, p in zip(cand_list, cand_probs):
                    sampling_probs_record[u] = p
                sampled = self._sample_without_replacement(cand_list, cand_probs, budget, rng)

            sampled_set = set(sampled)
            for v in current_layer_nodes:
                deg_v = degrees.get(v, 1)
                for u in adjacency.get(v, []):
                    if u in sampled_set:
                        deg_u = degrees.get(u, 1)
                        raw_norm = 1.0 / (math.sqrt(float(deg_u)) * math.sqrt(float(deg_v)))
                        p_u = sampling_probs_record.get(u, 1.0 / max(1, len(sampled)))
                        scaled_w = raw_norm / max(1e-6, p_u * float(len(sampled)))
                        subgraph_edges.append((u, v, scaled_w))

            layers.insert(0, sampled)
            current_layer_nodes = sampled

        return {
            "layer_nodes": layers,
            "subgraph_edges": subgraph_edges,
            "sampling_probabilities": sampling_probs_record,
        }

    def _sample_without_replacement(
        self,
        population: List[TNode],
        weights: List[float],
        k: int,
        rng: random.Random,
    ) -> List[TNode]:
        """Samples k unique elements from population proportional to weights."""
        if len(population) <= k:
            return list(population)

        selected: Set[TNode] = set()
        result: List[TNode] = []
        pop_with_w = list(zip(population, weights))

        for _ in range(k):
            available = [(u, w) for u, w in pop_with_w if u not in selected]
            if not available:
                break
            tot_w = sum(w for _, w in available)
            if tot_w <= 0.0:
                pick = rng.choice([u for u, _ in available])
            else:
                threshold = rng.random() * tot_w
                running = 0.0
                pick = available[-1][0]
                for u, w in available:
                    running += w
                    if running >= threshold:
                        pick = u
                        break
            selected.add(pick)
            result.append(pick)
        return result
