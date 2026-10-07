"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SNOWBALL & RDS SAMPLING (ALGO-GRAPH-SAMP-149)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Snowball, Forest Fire, and Respondent-Driven Sampling (RDS) suite with
   Volz-Heckathorn / Hansen-Hurwitz degree-bias corrections.
   Expands recursively from seed vertices through neighbor recruitment chains,
   computing 1 / deg(u) weights to produce unbiased population attribute estimates
   from chain-referral graph samples.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(sample_size) neighbor recruitment expansions.
   - Space Complexity: O(sample_size) sampled vertices.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - seeds: List[TNode] - Initial recruiter seed vertices.
   - target_sample_size: int - Total unique nodes to recruit.
   - max_recruits_per_node: int - Maximum referral invitations per participant (default: 3).
   - rng_seed: int - Random seed (default: 42).

4. OUTPUT PARAMETERS:
   - sampled_nodes: List[TNode] - Recruited sample participant vertices.
   - rds_weights: Dict[TNode, float] - Volz-Heckathorn inverse-degree debiasing weights.
   - sample_size: int - Total number of sampled vertices.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Seeds must be in the graph.
   - Guardrails: Volz-Heckathorn weights w(u) = (1/deg(u)) / sum_v(1/deg(v)) eliminate recruiter hub bias.
================================================================================
"""

import random
from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoSnowballRdsSampling(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-SAMP-149
      name: GraphAlgoSnowballRdsSampling
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, sampling, snowball_sampling, rds, respondent_driven_sampling, volz_heckathorn, forest_fire]
      inputs:
        type: object
        required: [adjacency, seeds, target_sample_size]
        properties:
          adjacency: {type: object}
          seeds: {type: array, items: {type: string}}
          target_sample_size: {type: integer}
          max_recruits_per_node: {type: integer, default: 3}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [sampled_nodes, rds_weights, sample_size]
        properties:
          sampled_nodes: {type: array, items: {type: string}}
          rds_weights: {type: object}
          sample_size: {type: integer}
      parameters:
        max_recruits_per_node: {type: integer, default: 3}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(S)
        space: O(S)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        seeds: List[TNode],
        target_sample_size: int,
        max_recruits_per_node: int = 3,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Snowball and RDS Sampling engine.

        Args:
            adjacency: Graph adjacency dictionary.
            seeds: Initial recruiter nodes.
            target_sample_size: Maximum sample quota.
            max_recruits_per_node: Max referral tokens per participant.
            rng_seed: Deterministic random seed.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._seeds: List[TNode] = seeds
        self._target_size: int = target_sample_size
        self._max_recruits: int = max_recruits_per_node
        self._rng_seed: int = rng_seed

    def sample_rds(self) -> Tuple[List[TNode], Dict[TNode, float], int]:
        """
        Execute Respondent-Driven Sampling and compute Volz-Heckathorn debiasing weights.

        Returns:
            Tuple of (sampled_nodes_list, rds_weights_dict, sample_size).
        """
        rng = random.Random(self._rng_seed)
        sampled_set: Set[TNode] = set(self._seeds)
        q: Deque[TNode] = deque(self._seeds)

        while q and len(sampled_set) < self._target_size:
            u = q.popleft()
            nbrs = [v for v in self._adj.get(u, []) if v not in sampled_set]
            if not nbrs:
                continue

            num_pick = min(self._max_recruits, len(nbrs))
            recruits = rng.sample(nbrs, num_pick)

            for v in recruits:
                if len(sampled_set) < self._target_size:
                    sampled_set.add(v)
                    q.append(v)

        sampled_nodes = sorted(list(sampled_set), key=lambda x: str(x))
        degrees = {u: max(1, len(self._adj.get(u, []))) for u in sampled_nodes}

        inv_deg_sum = sum(1.0 / float(degrees[u]) for u in sampled_nodes)
        rds_weights = {u: (1.0 / float(degrees[u])) / inv_deg_sum for u in sampled_nodes}

        return sampled_nodes, rds_weights, len(sampled_nodes)
