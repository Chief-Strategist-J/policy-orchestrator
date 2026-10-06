"""
================================================================================
ALGORITHM BLUEPRINT: KNOWLEDGE GRAPH FRAUD RING & COLLUSION DETECTOR
================================================================================

1. OVERVIEW & OBJECTIVE:
   Comprehensive Knowledge Graph fraud detection engine identifying coordinated
   fraud rings, circular transaction laundering topologies, and shared-synthetic-
   identity collusion networks. Implements canonical cycle deduplication (isomorphism
   invariance), bipartite shared attribute projection, and risk-weighted ring scoring.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Canonical Form Invariance: Directed cycles are normalized to lexicographically
     minimal rotation to prevent duplicate cycle counting.
   - Purity & Determinism: Pure functional state transitions with zero side effects.
   - Zero Inline Comments: Code logic is self-documenting per architectural doctrine.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(V * (V + E) * Depth) for bounded elementary cycle enumeration.
   - Space Complexity: O(V + Cycles) for visited paths and detected ring storage.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import defaultdict
from typing import Dict, Any, List, Set, Tuple, Optional, Callable


class KgAlgoFraudRingDetection:
    """
    --- contract:
      id: ALGO-KG-137
      name: KgAlgoFraudRingDetection
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(V * (V + E) * Depth)
        space: O(V + Cycles)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - fraud_ring
      - circular_chains
      - synthetic_identity
      - bipartite_collusion
      input_schema:
        edges: array
        shared_attributes: optional object
        max_cycle_length: integer
      output_schema:
        algorithm: string
        circular_fraud_rings: array
        collusion_clusters: array
        total_rings_detected: integer
    ---
    """

    def find_cycles(
        self,
        edges: List[Tuple[str, str]],
        max_length: int = 4,
    ) -> Dict[str, Any]:
        adj: Dict[str, List[str]] = defaultdict(list)
        for u, v in edges:
            adj[u].append(v)

        canonical_cycles: Set[Tuple[str, ...]] = set()

        def normalize_cycle(path: List[str]) -> Tuple[str, ...]:
            nodes = path[:-1]
            min_idx = nodes.index(min(nodes))
            rotated = nodes[min_idx:] + nodes[:min_idx]
            return tuple(rotated)

        def dfs(start_node: str, current_node: str, current_path: List[str]):
            if len(current_path) > max_length:
                return

            for neighbor in adj.get(current_node, []):
                if neighbor == start_node and len(current_path) >= 3:
                    canon = normalize_cycle(current_path + [start_node])
                    canonical_cycles.add(canon)
                elif neighbor not in current_path:
                    dfs(start_node, neighbor, current_path + [neighbor])

        for start, _ in edges:
            dfs(start, start, [start])

        ring_list = [list(c) + [c[0]] for c in sorted(canonical_cycles)]
        return {
            "algorithm": "ALGO-KG-137",
            "fraud_ring_count": len(ring_list),
            "fraud_rings": ring_list[:20],
        }

    def detect_collusion_network(
        self,
        transaction_edges: List[Tuple[str, str, float]],
        shared_attributes: Optional[Dict[str, List[str]]] = None,
        max_cycle_length: int = 5,
    ) -> Dict[str, Any]:
        unweighted_edges = [(u, v) for u, v, _ in transaction_edges]
        cycle_res = self.find_cycles(unweighted_edges, max_length=max_cycle_length)

        shared_attr_clusters: List[Dict[str, Any]] = []
        if shared_attributes:
            attr_to_entities: Dict[str, Set[str]] = defaultdict(set)
            for entity, attrs in shared_attributes.items():
                for a in attrs:
                    attr_to_entities[a].add(entity)

            for attr_id, entities in attr_to_entities.items():
                if len(entities) >= 2:
                    shared_attr_clusters.append({
                        "attribute": attr_id,
                        "colluding_entities": sorted(list(entities)),
                        "cluster_size": len(entities),
                    })

        edge_amounts: Dict[Tuple[str, str], float] = {(u, v): w for u, v, w in transaction_edges}
        scored_rings: List[Dict[str, Any]] = []
        for ring in cycle_res["fraud_rings"]:
            ring_volume = 0.0
            for i in range(len(ring) - 1):
                ring_volume += edge_amounts.get((ring[i], ring[i + 1]), 1.0)
            risk_score = round(min(1.0, (len(ring) * 0.2) + (ring_volume / 10000.0)), 3)
            scored_rings.append({
                "ring_path": ring,
                "hop_count": len(ring) - 1,
                "total_flow_volume": round(ring_volume, 2),
                "risk_score": risk_score,
            })

        scored_rings.sort(key=lambda x: x["risk_score"], reverse=True)
        return {
            "algorithm": "ALGO-KG-137",
            "total_circular_rings": len(scored_rings),
            "top_risk_fraud_rings": scored_rings[:10],
            "shared_attribute_clusters": shared_attr_clusters[:10],
        }
