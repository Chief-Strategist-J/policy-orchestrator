"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SLPA OVERLAPPING COMMUNITIES (ALGO-GRAPH-COMM-154)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Speaker-Listener Label Propagation Algorithm (SLPA) for overlapping community detection.
   Maintains a persistent memory of received community labels per vertex.
   In each communication round, neighbor speakers emit labels weighted by memory frequency,
   and listener nodes adopt the most frequent incoming label. Thresholding memory proportions
   by retention threshold r extracts overlapping community memberships.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(T * m) linear communication rounds.
   - Space Complexity: O(V * T) label memory storage.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - num_rounds_t: int - Number of communication iterations T (default: 20).
   - retention_threshold_r: float - Minimum frequency threshold r in (0.0, 1.0) (default: 0.2).
   - rng_seed: int - Random seed (default: 42).

4. OUTPUT PARAMETERS:
   - overlapping_communities: Dict[TNode, List[int]] - Multiple community IDs per node.
   - community_memberships: Dict[int, List[TNode]] - Nodes belonging to each community.
   - num_communities: int - Total unique overlapping communities.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Graph with at least one vertex.
   - Guardrails: Post-processing thresholding eliminates low-frequency transient labels.
================================================================================
"""

import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoSlpaOverlappingCommunities(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-COMM-154
      name: GraphAlgoSlpaOverlappingCommunities
      version: 1.0.0
      category: graph_communities_spectral
      capability_tags: [graph, communities, slpa, overlapping_communities, label_propagation, memory_networks]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          num_rounds_t: {type: integer, default: 20}
          retention_threshold_r: {type: number, default: 0.2}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [overlapping_communities, community_memberships, num_communities]
        properties:
          overlapping_communities: {type: object}
          community_memberships: {type: object}
          num_communities: {type: integer}
      parameters:
        num_rounds_t: {type: integer, default: 20}
        retention_threshold_r: {type: number, default: 0.2}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(T * m)
        space: O(V * T)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        num_rounds_t: int = 20,
        retention_threshold_r: float = 0.2,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the SLPA Overlapping Community detector.

        Args:
            adjacency: Graph adjacency dictionary.
            num_rounds_t: Communication rounds T.
            retention_threshold_r: Label retention frequency cutoff r.
            rng_seed: Deterministic random seed.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._t: int = num_rounds_t
        self._r: float = retention_threshold_r
        self._rng_seed: int = rng_seed
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def detect_overlapping_communities(self) -> Tuple[Dict[TNode, List[int]], Dict[int, List[TNode]], int]:
        """
        Execute Speaker-Listener Label Propagation.

        Returns:
            Tuple of (node_communities_map, community_members_map, total_communities_count).
        """
        n = len(self._nodes)
        if n == 0:
            return {}, {}, 0

        rng = random.Random(self._rng_seed)
        memory: Dict[TNode, List[int]] = {u: [i] for i, u in enumerate(self._nodes)}

        for _ in range(self._t):
            shuffled_nodes = list(self._nodes)
            rng.shuffle(shuffled_nodes)

            for u in shuffled_nodes:
                nbrs = list(self._adj.get(u, set()))
                if not nbrs:
                    continue

                heard_labels: Dict[int, int] = {}
                for v in nbrs:
                    spoken_label = rng.choice(memory[v])
                    heard_labels[spoken_label] = heard_labels.get(spoken_label, 0) + 1

                max_count = max(heard_labels.values())
                best_labels = [lbl for lbl, count in heard_labels.items() if count == max_count]
                chosen_label = rng.choice(best_labels)
                memory[u].append(chosen_label)

        node_comms: Dict[TNode, List[int]] = {}
        total_memory_size = float(self._t + 1)

        for u in self._nodes:
            counts: Dict[int, int] = {}
            for lbl in memory[u]:
                counts[lbl] = counts.get(lbl, 0) + 1

            valid_labels = [lbl for lbl, count in counts.items() if (float(count) / total_memory_size) >= self._r]
            if not valid_labels:
                top_label = max(counts.keys(), key=lambda l: counts[l])
                valid_labels = [top_label]
            node_comms[u] = sorted(valid_labels)

        all_unique_labels = sorted(list({lbl for lbls in node_comms.values() for lbl in lbls}))
        compact_id = {old: new for new, old in enumerate(all_unique_labels)}

        final_node_comms: Dict[TNode, List[int]] = {u: [compact_id[lbl] for lbl in lbls] for u, lbls in node_comms.items()}
        comm_members: Dict[int, List[TNode]] = {c: [] for c in compact_id.values()}

        for u, lbls in final_node_comms.items():
            for c in lbls:
                comm_members[c].append(u)

        for c in comm_members:
            comm_members[c] = sorted(comm_members[c], key=lambda x: str(x))

        return final_node_comms, comm_members, len(comm_members)
