"""ALGORITHM & ARCHITECTURE BLUEPRINT: PATH RANKING ALGORITHM (PRA) (ALGO-GRAPH-RANK-289)

1. OVERVIEW & OBJECTIVE
Path Ranking Algorithm (PRA; Lao & Cohen) models relational link prediction and knowledge graph completion
by extracting bounded-length relation path types (e.g. e1 -[r1]-> e2 -[r2]-> e3) and computing random walk
path-following probabilities P(t | s, pi) as discriminative features for logistic regression ranking.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|PathTypes| * |V| + |E|) path probability feature matrix storage.
- Time Complexity: O(|PathTypes| * |E|) multi-hop relational transition matrix multiplication.
- Invariants:
  - Path probabilities P(t | s, pi) are computed via sequential relational matrix chain multiplication.
  - Logistic regression weights theta_pi yield ranking scores: score(s, r, t) = sum_{pi} theta_pi * P(t | s, pi).

3. INPUT PARAMETERS:
- knowledge_graph_triplets: Sequence[tuple[TNode, str, TNode]] (head, relation, tail) relational graph facts.
- target_relation: str query relation being predicted.
- max_path_length: int maximum relation sequence length (e.g. 2 or 3).
- candidate_source: TNode source entity node s.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'candidate_scores': Dict[TNode, float] predicted probabilities for target entities.
  - 'extracted_paths': List[tuple[str, ...]] discovered relational path types.
  - 'path_features': Dict[TNode, Dict[tuple[str, ...], float]] per-target path following probabilities.

5. AGENT CONTRACT:
- Strict zero-inline-comment doctrine.
- Generic node typing via `TNode`.
"""

from __future__ import annotations

import collections
import math
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoPathRankingAlgorithmPra(Generic[TNode]):
    """Path Ranking Algorithm (PRA) for relation learning and link prediction in Knowledge Graphs.

    ```yaml
    contract:
      id: ALGO-GRAPH-RANK-289
      name: GraphAlgoPathRankingAlgorithmPra
      inputs:
        - name: knowledge_graph_triplets
          type: Sequence[tuple[TNode, str, TNode]]
          description: List of (source, relation_type, target) triplets.
        - name: target_relation
          type: str
          description: Query predicate to predict.
        - name: candidate_source
          type: TNode
          description: Source entity node.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Predicted target entity scores and extracted relational path features.
      parameters:
        max_path_length: int (default 2)
        top_k: int (default 10)
      capability_tags:
        - KNOWLEDGE_GRAPH
        - PATH_RANKING
        - PRA
        - LINK_PREDICTION
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(|Paths| * |E|)
        space: O(|Paths| * |V|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        knowledge_graph_triplets: Sequence[Tuple[TNode, str, TNode]],
        target_relation: str,
        candidate_source: TNode,
        max_path_length: int = 2,
        top_k: int = 10,
    ) -> Dict[str, Any]:
        """Extracts relational paths and computes PRA path-following probabilities."""
        rel_adj: Dict[str, Dict[TNode, List[TNode]]] = collections.defaultdict(lambda: collections.defaultdict(list))
        all_relations: Set[str] = set()

        for s, r, t in knowledge_graph_triplets:
            rel_adj[r][s].append(t)
            all_relations.add(r)

        if not all_relations or candidate_source not in [s for s, _, _ in knowledge_graph_triplets]:
            return {
                "candidate_scores": {},
                "extracted_paths": [],
                "path_features": {},
            }

        candidate_paths: List[Tuple[str, ...]] = []
        for length in range(1, max_path_length + 1):
            for p in self._generate_path_types(list(all_relations), length):
                if p != (target_relation,):
                    candidate_paths.append(p)

        target_path_probs: Dict[TNode, Dict[Tuple[str, ...], float]] = collections.defaultdict(dict)
        candidate_targets: Set[TNode] = set()

        for path_seq in candidate_paths:
            dist: Dict[TNode, float] = {candidate_source: 1.0}
            for rel in path_seq:
                next_dist: Dict[TNode, float] = collections.defaultdict(float)
                for u, prob_u in dist.items():
                    nbrs = rel_adj[rel].get(u, [])
                    if nbrs:
                        p_step = prob_u / float(len(nbrs))
                        for v in nbrs:
                            next_dist[v] += p_step
                dist = next_dist

            for target_node, p_val in dist.items():
                if target_node != candidate_source and p_val > 1e-4:
                    target_path_probs[target_node][path_seq] = p_val
                    candidate_targets.add(target_node)

        scores: Dict[TNode, float] = {}
        for target_node in candidate_targets:
            p_dict = target_path_probs[target_node]
            score_val = sum(p_dict.values())
            prob = 1.0 / (1.0 + math.exp(-score_val))
            scores[target_node] = prob

        sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k])

        return {
            "candidate_scores": sorted_scores,
            "extracted_paths": candidate_paths,
            "path_features": {t: target_path_probs[t] for t in sorted_scores.keys()},
        }

    def _generate_path_types(
        self, relations: List[str], length: int
    ) -> List[Tuple[str, ...]]:
        """Generates all relation sequences of specific length."""
        if length == 1:
            return [(r,) for r in relations]
        sub = self._generate_path_types(relations, length - 1)
        res = []
        for r in relations:
            for s in sub:
                res.append((r,) + s)
        return res
