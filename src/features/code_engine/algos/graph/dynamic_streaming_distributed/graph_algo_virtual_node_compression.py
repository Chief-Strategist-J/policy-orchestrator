"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: VIRTUAL NODE BICLIQUE COMPRESSION (ALGO-GRAPH-SUMM-237)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Virtual Node Biclique Compression Engine.
   Detects dense complete bipartite subgraphs (bicliques S x T) and replaces |S| * |T|
   cross-edges with |S| + |T| star edges routed through a synthesized virtual intermediate
   node, drastically reducing edge counts in web graphs and social affiliation networks.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(M * d_max) biclique mining and topological replacement.
   - Space Complexity: O(V + M) compressed graph topology with virtual node IDs.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Original directed/bipartite adjacency.
   - `min_biclique_size` (int): Minimum |S| * |T| product required to introduce virtual node.

4. OUTPUT PARAMETERS:
   - `compress()` (Tuple[Dict[Any, List[Any]], List[Any]]): Compressed adjacency and list of created virtual nodes.
   - `get_edge_reduction_count()` (int): Net edges saved.

5. AGENT CONTRACT:
   - Role: Builder.
   - Guarantees: Paths through virtual nodes preserve reachability between all u in S and v in T.
================================================================================
"""

from collections import defaultdict
from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoVirtualNodeCompression(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-SUMM-237
      name: GraphAlgoVirtualNodeCompression
      version: 1.0.0
      category: graph_summarization
      capability_tags: [graph, summarization, virtual_nodes, biclique_compression, edge_reduction]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          min_biclique_size: {type: integer, minimum: 4}
      outputs:
        type: object
        properties:
          compressed_edges: {type: integer}
          virtual_node_count: {type: integer}
      parameters:
        min_biclique_size: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(M * d)
        space: O(V + M)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]], min_biclique_size: int = 4) -> None:
        """
        Initialize virtual node biclique compressor.

        Args:
            adjacency: Directed graph adjacency.
            min_biclique_size: Minimum |S| * |T| edge volume to justify virtual node insertion.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = set()

        self._min_size: int = max(4, min_biclique_size)

    def compress(self) -> Tuple[Dict[Any, List[Any]], List[str], int]:
        """
        Execute biclique discovery and virtual node substitution.

        Returns:
            Tuple of (compressed_adjacency_map, virtual_nodes_created, net_edge_savings).
        """
        nbr_patterns: Dict[Tuple[TNode, ...], List[TNode]] = defaultdict(list)
        for u, nbrs in self._adj.items():
            if len(nbrs) >= 2:
                pattern = tuple(sorted(list(nbrs), key=lambda x: str(x)))
                nbr_patterns[pattern].append(u)

        compressed_adj: Dict[Any, Set[Any]] = {u: set(nbrs) for u, nbrs in self._adj.items()}
        virtual_nodes: List[str] = []
        v_idx = 0
        net_savings = 0

        for pattern, sources in nbr_patterns.items():
            s_len = len(sources)
            t_len = len(pattern)
            orig_edges = s_len * t_len
            new_edges = s_len + t_len

            if orig_edges >= self._min_size and orig_edges >= new_edges:
                v_node = f"__virtual_biclique_{v_idx}__"
                v_idx += 1
                virtual_nodes.append(v_node)
                compressed_adj[v_node] = set(pattern)

                for u in sources:
                    for v in pattern:
                        compressed_adj[u].discard(v)
                    compressed_adj[u].add(v_node)

                net_savings += (orig_edges - new_edges)

        final_adj: Dict[Any, List[Any]] = {u: list(nbrs) for u, nbrs in compressed_adj.items()}
        return final_adj, virtual_nodes, net_savings
