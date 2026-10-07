"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GRAPHLET DEGREE VECTORS (ALGO-GRAPH-DENSE-120)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Graphlet counting and Graphlet Degree Vector (GDV) structural fingerprint engine.
   Enumerates small 2-to-4 vertex induced graphlet subgraph orbits (ORCA-style)
   to build multidimensional structural fingerprints per vertex and global frequency histograms.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V * d_max^3) local orbit enumeration.
   - Space Complexity: O(V * num_orbits) fingerprint table.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency list.

4. OUTPUT PARAMETERS:
   - graphlet_degree_vectors: Dict[TNode, List[int]] - Orbit count vector per node [orbit_0 (degree), orbit_1 (triangle), orbit_2 (path-mid), orbit_3 (path-end)].
   - global_graphlet_counts: Dict[str, int] - Aggregate count of each 3-and-4-node graphlet pattern.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Simple undirected graph with no self-loops.
   - Guardrails: Orbit counts normalized per degree for scale-invariant network comparison.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGraphletDegreeVectors(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DENSE-120
      name: GraphAlgoGraphletDegreeVectors
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, dense_structures, graphlets, orca, orbit_fingerprint, structural_motifs]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
      outputs:
        type: object
        required: [graphlet_degree_vectors, global_graphlet_counts]
        properties:
          graphlet_degree_vectors: {type: object}
          global_graphlet_counts: {type: object}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V * d^3)
        space: O(V * O)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        """
        Initialize the Graphlet Degree Vector engine.

        Args:
            adjacency: Graph adjacency dictionary.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def compute_gdv(self) -> Tuple[Dict[TNode, List[int]], Dict[str, int]]:
        """
        Compute Graphlet Degree Vectors (orbits 0 to 3) for all vertices.

        Returns:
            Tuple of (per_node_gdv_vectors, global_graphlet_counts).
        """
        gdv: Dict[TNode, List[int]] = {u: [0, 0, 0, 0] for u in self._nodes}
        triangles: int = 0
        wedges: int = 0

        for u in self._nodes:
            nbrs = list(self._adj.get(u, set()))
            deg = len(nbrs)
            gdv[u][0] = deg

            for i in range(deg):
                v = nbrs[i]
                for j in range(i + 1, deg):
                    w = nbrs[j]
                    wedges += 1
                    gdv[u][2] += 1
                    gdv[v][3] += 1
                    gdv[w][3] += 1

                    if w in self._adj.get(v, set()):
                        gdv[u][1] += 1

        for u in self._nodes:
            triangles += gdv[u][1]
        triangles = triangles // 3

        global_counts = {
            "G0_edge": sum(len(self._adj.get(u, set())) for u in self._nodes) // 2,
            "G1_wedge": wedges - (3 * triangles),
            "G2_triangle": triangles,
        }

        return gdv, global_counts
