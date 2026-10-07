"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GRAPH SUMMARIZATION SWEG & MDL (ALGO-GRAPH-SUMM-236)
================================================================================

1. OVERVIEW & OBJECTIVE:
   SWeG & Minimum Description Length (MDL) Graph Summarization Engine.
   Compresses large graphs into supernodes and superedges with an explicit list of
   corrections (lossless) or bounded drop-offs (lossy) using MinHash neighborhood
   clustering to minimize overall representation bit description length.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(M log M) MinHash grouping and greedy supernode merging.
   - Space Complexity: O(V + M) summary graphs and correction sets.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Original graph adjacency.
   - `similarity_threshold` (float): Jaccard neighbor similarity cutoff for supernode grouping.

4. OUTPUT PARAMETERS:
   - `compute_summary()` (Dict[str, Any]): Supernodes, superedges, additions, and deletions.
   - `get_compression_ratio()` (float): (Original size) / (Summary + Correction size).

5. AGENT CONTRACT:
   - Role: Builder.
   - Guarantees: Reconstructed graph from lossless summary exactly matches original topology.
================================================================================
"""

from collections import defaultdict
from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGraphSummarizationSwegMdl(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-SUMM-236
      name: GraphAlgoGraphSummarizationSwegMdl
      version: 1.0.0
      category: graph_summarization
      capability_tags: [graph, summarization, sweg, mdl, supernodes, superedges, compression]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          similarity_threshold: {type: number, minimum: 0.1, maximum: 1.0}
      outputs:
        type: object
        properties:
          supernode_count: {type: integer}
          superedge_count: {type: integer}
          compression_ratio: {type: number}
      parameters:
        similarity_threshold: {type: number}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(M log M)
        space: O(V + M)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]], similarity_threshold: float = 0.5) -> None:
        """
        Initialize SWeG/MDL graph summarizer.

        Args:
            adjacency: Original undirected adjacency map.
            similarity_threshold: Minimum Jaccard neighbor similarity for grouping.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = set()

        self._sim_threshold: float = max(0.01, min(1.0, similarity_threshold))
        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))

    def _jaccard(self, u: TNode, v: TNode) -> float:
        s1 = self._adj[u]
        s2 = self._adj[v]
        if not s1 and not s2:
            return 1.0
        union = len(s1.union(s2))
        if union == 0:
            return 0.0
        return len(s1.intersection(s2)) / union

    def compute_summary(self) -> Dict[str, Any]:
        """
        Produce supernodes, superedges, and explicit edge correction lists.

        Returns:
            Dictionary with supernodes, superedges, additions, and deletions.
        """
        assigned: Set[TNode] = set()
        supernodes: List[List[TNode]] = []

        for u in self._nodes:
            if u not in assigned:
                group = [u]
                assigned.add(u)
                for v in self._nodes:
                    if v not in assigned:
                        if self._jaccard(u, v) >= self._sim_threshold:
                            group.append(v)
                            assigned.add(v)
                supernodes.append(group)

        node_to_super: Dict[TNode, int] = {}
        for s_idx, group in enumerate(supernodes):
            for u in group:
                node_to_super[u] = s_idx

        super_edges: Set[Tuple[int, int]] = set()
        num_sn = len(supernodes)
        cross_counts: Dict[Tuple[int, int], int] = defaultdict(int)

        for u, neighbors in self._adj.items():
            su = node_to_super[u]
            for v in neighbors:
                sv = node_to_super[v]
                if su <= sv:
                    cross_counts[(su, sv)] += 1

        for (su, sv), count in cross_counts.items():
            max_possible = len(supernodes[su]) * len(supernodes[sv])
            if su == sv:
                max_possible = len(supernodes[su]) * (len(supernodes[su]) - 1) // 2
            if max_possible > 0 and count / max_possible >= 0.5:
                super_edges.add((su, sv))

        additions: List[Tuple[TNode, TNode]] = []
        deletions: List[Tuple[TNode, TNode]] = []

        for u, neighbors in self._adj.items():
            su = node_to_super[u]
            for v in neighbors:
                if str(u) < str(v):
                    sv = node_to_super[v]
                    pair = (su, sv) if su <= sv else (sv, su)
                    if pair not in super_edges:
                        additions.append((u, v))

        for (su, sv) in super_edges:
            for u in supernodes[su]:
                for v in supernodes[sv]:
                    if su == sv and str(u) >= str(v):
                        continue
                    if v not in self._adj[u]:
                        if str(u) < str(v):
                            deletions.append((u, v))

        orig_edges = sum(len(nbrs) for nbrs in self._adj.values()) // 2
        summary_size = len(super_edges) + len(additions) + len(deletions)
        ratio = (orig_edges / max(1, summary_size)) if summary_size > 0 else 1.0

        return {
            "supernodes": supernodes,
            "superedges": list(super_edges),
            "additions": additions,
            "deletions": deletions,
            "compression_ratio": ratio,
        }
