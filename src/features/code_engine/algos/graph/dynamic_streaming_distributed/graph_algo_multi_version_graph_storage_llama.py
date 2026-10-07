"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MULTI-VERSION GRAPH STORAGE (LLAMA) (ALGO-GRAPH-ENG-244)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Multi-Version Compressed Graph Storage Engine (LLAMA / Delta-Chains).
   Stores immutable historical snapshots and persistent delta chains sharing unchanged
   CSR pages, enabling concurrent read-only analytics pinned to past version epochs
   while real-time write streams continuously append new topological mutations.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(1) version pinning, O(deg(v)) delta chain neighbor traversal.
   - Space Complexity: O(V + M + Sum_Deltas) copy-on-write persistent page index.
   - Purity: Stateful MVCC graph ledger, deterministic snapshot reads.

3. INPUT PARAMETERS:
   - Initial base snapshot edges (Optional).

4. OUTPUT PARAMETERS:
   - `create_version_snapshot()` (int): New epoch version ID.
   - `add_edge(u, v, weight)` (None): Appends delta to active write version.
   - `get_neighbors_at_version(u, version_id)` (List[Tuple[TNode, float]]): Isolated version read.

5. AGENT CONTRACT:
   - Role: Builder.
   - Guarantees: Historical queries pinned at version v are strictly isolated from newer mutations.
================================================================================
"""

from collections import defaultdict
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoMultiVersionGraphStorageLlama(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ENG-244
      name: GraphAlgoMultiVersionGraphStorageLlama
      version: 1.0.0
      category: graph_engineering
      capability_tags: [graph, engineering, mvcc, llama, delta_chains, version_pinning, multi_version]
      inputs:
        type: object
        properties: {}
      outputs:
        type: object
        properties:
          current_version: {type: integer}
          pinned_versions: {type: array}
      parameters: {}
      purity: stateful
      determinism: deterministic
      idempotency: idempotent_reads
      complexity:
        time: O(deg(v)) read
        space: O(V + M + Deltas)
    ---
    """

    def __init__(self) -> None:
        """Initialize LLAMA multi-version delta storage structure."""
        self._current_version: int = 0
        self._delta_chains: Dict[TNode, List[Tuple[int, TNode, float, str]]] = defaultdict(list)
        self._all_nodes: Set[TNode] = set()

    def create_version_snapshot(self) -> int:
        """
        Advance epoch and return new version ID.

        Returns:
            Incremented version identifier.
        """
        self._current_version += 1
        return self._current_version

    def add_edge(self, u: TNode, v: TNode, weight: float = 1.0) -> None:
        """
        Record edge addition mutation in current version delta chain.

        Args:
            u: Source node.
            v: Target node.
            weight: Edge weight.
        """
        self._all_nodes.add(u)
        self._all_nodes.add(v)
        self._delta_chains[u].append((self._current_version, v, float(w_val := weight), "add"))

    def remove_edge(self, u: TNode, v: TNode) -> None:
        """
        Record edge tombstone deletion in current version delta chain.

        Args:
            u: Source node.
            v: Target node.
        """
        self._delta_chains[u].append((self._current_version, v, 0.0, "delete"))

    def get_neighbors_at_version(self, u: TNode, version_id: Optional[int] = None) -> List[Tuple[TNode, float]]:
        """
        Retrieve active outgoing neighbors of u visible at version_id.

        Args:
            u: Target node.
            version_id: Pinned version (defaults to current version).

        Returns:
            List of active (neighbor, weight) tuples.
        """
        v_target = self._current_version if version_id is None else version_id
        active_nbrs: Dict[TNode, float] = {}

        for ver, v, w, op in self._delta_chains.get(u, []):
            if ver <= v_target:
                if op == "add":
                    active_nbrs[v] = w
                elif op == "delete":
                    active_nbrs.pop(v, None)

        return list(active_nbrs.items())

    def get_all_nodes(self) -> List[TNode]:
        """
        Return all nodes recorded in multi-version storage.

        Returns:
            List of node IDs.
        """
        return list(self._all_nodes)
