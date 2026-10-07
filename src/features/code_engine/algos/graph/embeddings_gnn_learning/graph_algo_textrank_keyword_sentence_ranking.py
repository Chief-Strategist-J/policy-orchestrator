"""ALGORITHM & ARCHITECTURE BLUEPRINT: TEXTRANK KEYWORD & SENTENCE RANKING (ALGO-GRAPH-RANK-285)

1. OVERVIEW & OBJECTIVE
TextRank is a graph-based ranking model for unsupervised keyword extraction and sentence summarization.
It models tokens or sentences as graph vertices and co-occurrence windows or semantic similarities (BM25/cosine)
as weighted edges, computing stationary random walk distributions via Power Iteration to rank structural importance.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V| + |E|) for token/sentence co-occurrence graphs.
- Time Complexity: O(T_iter * |E| + N_tokens * W) where W is co-occurrence sliding window size.
- Invariants:
  - Transition probability matrix is stochastic (outbound edge weights normalized to 1.0).
  - PageRank scores are non-negative and sum to 1.0 across all graph vertices.

3. INPUT PARAMETERS:
- tokens_or_sentences: Sequence[TNode] sequence of text units (words, lemmas, or sentences).
- window_size: int co-occurrence context window length (e.g. 2 to 5 for keywords).
- damping: float random surfer damping factor (typically 0.85).
- max_iterations: int power iteration convergence cutoff.
- tolerance: float stationary distribution change threshold.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'ranks': Dict[TNode, float] stationary TextRank centrality score per unique element.
  - 'top_ranked': List[tuple[TNode, float]] ordered sequence of top-scoring tokens/sentences.
  - 'converged': bool power iteration convergence indicator.
  - 'iterations': int count of execution iterations.

5. AGENT CONTRACT:
- Strict zero-inline-comment doctrine.
- Generic over token/sentence identifier type `TNode`.
"""

from __future__ import annotations

import collections
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoTextrankKeywordSentenceRanking(Generic[TNode]):
    """Graph-based TextRank algorithm for unsupervised keyword extraction and sentence ranking.

    ```yaml
    contract:
      id: ALGO-GRAPH-RANK-285
      name: GraphAlgoTextrankKeywordSentenceRanking
      inputs:
        - name: tokens_or_sentences
          type: Sequence[TNode]
          description: Sequential list of tokens, phrases, or sentence objects.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: TextRank importance scores and ordered top-scoring items.
      parameters:
        window_size: int (default 3)
        damping: float (default 0.85)
        max_iterations: int (default 100)
        tolerance: float (default 1e-6)
      capability_tags:
        - GRAPH_RANKING
        - TEXTRANK
        - KEYWORD_EXTRACTION
        - PAGERANK
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(T * |E| + N * W)
        space: O(|V| + |E|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        tokens_or_sentences: Sequence[TNode],
        window_size: int = 3,
        damping: float = 0.85,
        max_iterations: int = 100,
        tolerance: float = 1e-6,
    ) -> Dict[str, Any]:
        """Builds co-occurrence graph and runs power-iteration TextRank scoring."""
        items = list(tokens_or_sentences)
        n_items = len(items)
        if n_items == 0:
            return {"ranks": {}, "top_ranked": [], "converged": True, "iterations": 0}

        unique_nodes = list(dict.fromkeys(items))
        n_nodes = len(unique_nodes)
        if n_nodes == 1:
            only_node = unique_nodes[0]
            return {
                "ranks": {only_node: 1.0},
                "top_ranked": [(only_node, 1.0)],
                "converged": True,
                "iterations": 0,
            }

        edge_weights: Dict[TNode, Dict[TNode, float]] = collections.defaultdict(lambda: collections.defaultdict(float))

        for i in range(n_items):
            u = items[i]
            for j in range(i + 1, min(n_items, i + window_size + 1)):
                v = items[j]
                if u != v:
                    edge_weights[u][v] += 1.0
                    edge_weights[v][u] += 1.0

        out_degrees: Dict[TNode, float] = {
            u: sum(edge_weights[u].values()) for u in unique_nodes
        }

        scores: Dict[TNode, float] = {u: 1.0 / float(n_nodes) for u in unique_nodes}
        converged = False
        iteration = 0

        for it in range(max_iterations):
            iteration = it + 1
            new_scores: Dict[TNode, float] = {}
            max_delta = 0.0

            for u in unique_nodes:
                rank_sum = 0.0
                for v, w in edge_weights[u].items():
                    deg_v = out_degrees.get(v, 0.0)
                    if deg_v > 0.0:
                        rank_sum += (w / deg_v) * scores[v]

                val = (1.0 - damping) / float(n_nodes) + damping * rank_sum
                new_scores[u] = val
                delta = abs(val - scores[u])
                if delta > max_delta:
                    max_delta = delta

            scores = new_scores
            if max_delta < tolerance:
                converged = True
                break

        total_rank = sum(scores.values())
        if total_rank > 0.0:
            scores = {u: s / total_rank for u, s in scores.items()}

        sorted_ranks = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return {
            "ranks": scores,
            "top_ranked": sorted_ranks,
            "converged": converged,
            "iterations": iteration,
        }
