"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ASSORTATIVITY COEFFICIENT (ALGO-GRAPH-NET-133)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Degree and categorical attribute assortativity coefficient calculator.
   Computes Pearson correlation coefficient r in [-1.0, 1.0] of degrees across edge endpoints.
   Assortative networks (r > 0, hubs connect to hubs) exhibit core redundancy;
   Disassortative networks (r < 0, hubs connect to leaves) are vulnerable to targeted hub disruption.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(E) single linear pass over edge endpoints.
   - Space Complexity: O(V) degree cache.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - attributes: Optional[Dict[TNode, str]] - Optional discrete node attributes for mixing matrix.

4. OUTPUT PARAMETERS:
   - degree_assortativity: float - Pearson degree correlation coefficient in [-1.0, 1.0].
   - attribute_assortativity: Optional[float] - Discrete modularity attribute assortativity.
   - mean_degree: float - Average vertex degree across the graph.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Undirected or directed graph with at least one edge.
   - Guardrails: Handles uniform degree graphs (variance = 0) returning r = 0.0.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoAssortativityCoefficient(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-NET-133
      name: GraphAlgoAssortativityCoefficient
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, network_measures, assortativity, pearson_correlation, mixing_matrix, hub_connectivity]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          attributes: {type: object}
      outputs:
        type: object
        required: [degree_assortativity, mean_degree]
        properties:
          degree_assortativity: {type: number}
          attribute_assortativity: {type: number}
          mean_degree: {type: number}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(E)
        space: O(V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        attributes: Optional[Dict[TNode, str]] = None,
    ) -> None:
        """
        Initialize the Assortativity analyzer.

        Args:
            adjacency: Graph adjacency dictionary.
            attributes: Optional node attribute dictionary.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._attrs: Optional[Dict[TNode, str]] = attributes
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def compute_assortativity(self) -> Tuple[float, Optional[float], float]:
        """
        Compute degree assortativity and attribute mixing coefficient.

        Returns:
            Tuple of (degree_assortativity, attribute_assortativity, mean_degree).
        """
        degrees: Dict[TNode, float] = {u: float(len(self._adj.get(u, set()))) for u in self._nodes}
        edges: List[Tuple[float, float]] = []

        for u in self._nodes:
            for v in self._adj.get(u, set()):
                if str(u) < str(v):
                    edges.append((degrees[u], degrees[v]))
                    edges.append((degrees[v], degrees[u]))

        if not edges:
            return 0.0, None, 0.0

        m = float(len(edges))
        sum_x = sum(x for x, _ in edges)
        sum_y = sum(y for _, y in edges)
        sum_xy = sum(x * y for x, y in edges)
        sum_x2 = sum(x * x for x, _ in edges)
        sum_y2 = sum(y * y for _, y in edges)

        num = (m * sum_xy) - (sum_x * sum_y)
        denom_sq = ((m * sum_x2) - (sum_x ** 2)) * ((m * sum_y2) - (sum_y ** 2))

        if denom_sq > 1e-12:
            r = num / math.sqrt(denom_sq)
        else:
            r = 0.0

        mean_deg = sum(degrees.values()) / float(len(self._nodes)) if self._nodes else 0.0

        attr_r: Optional[float] = None
        if self._attrs is not None:
            attr_matches = 0
            for u in self._nodes:
                for v in self._adj.get(u, set()):
                    if str(u) < str(v) and self._attrs.get(u) == self._attrs.get(v):
                        attr_matches += 1
            total_undir_edges = len(edges) // 2
            attr_r = (float(attr_matches) / float(total_undir_edges)) if total_undir_edges > 0 else 0.0

        return r, attr_r, mean_deg
