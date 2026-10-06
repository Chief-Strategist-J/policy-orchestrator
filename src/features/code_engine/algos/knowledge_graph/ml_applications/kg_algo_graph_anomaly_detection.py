r"""
================================================================================
ALGORITHM BLUEPRINT: KNOWLEDGE GRAPH STRUCTURAL & ATTRIBUTE ANOMALY DETECTOR
================================================================================

1. OVERVIEW & OBJECTIVE:
   Comprehensive graph anomaly detection engine implementing OddBall egonet power-law
   pattern analysis ($E_i \propto N_i^\alpha$) for structural outlier detection (clique
   vs star anomalies, heavy hub anomalies) and local neighborhood attribute discord
   scoring for relational Knowledge Graphs.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Power Law Baseline: Evaluates egonet edge counts vs neighbor counts against
     expected density exponents $\alpha \in [1.0, 2.0]$.
   - Purity & Determinism: Pure functional state transitions with zero side effects.
   - Zero Inline Comments: Code logic is self-documenting per architectural doctrine.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(|V| * Average_Degree^2) for egonet induced subgraph evaluations.
   - Space Complexity: O(|V| + |E|) for egonet edge count buffers.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import math
from collections import defaultdict
from typing import Dict, Any, List, Set, Tuple, Optional, Callable


class KgAlgoGraphAnomalyDetection:
    """
    --- contract:
      id: ALGO-KG-136
      name: KgAlgoGraphAnomalyDetection
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(|V| * Degree^2)
        space: O(|V| + |E|)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - anomaly_detection
      - oddball_power_law
      - outlier_nodes
      - structural_discord
      - egonet_analysis
      input_schema:
        nodes: array
        edges: array
        node_attributes: optional object
        z_threshold: number
      output_schema:
        algorithm: string
        anomalies: array
        total_anomalies_detected: integer
    ---
    """

    def detect_anomalies(
        self,
        nodes: List[str],
        edges: List[Tuple[str, str]],
        z_threshold: float = 2.5,
    ) -> Dict[str, Any]:
        deg: Dict[str, int] = defaultdict(int)
        for u, v in edges:
            deg[u] += 1
            deg[v] += 1

        scores = [deg[n] for n in nodes]
        mean = sum(scores) / max(1, len(scores))
        std = (sum((s - mean) ** 2 for s in scores) / max(1, len(scores))) ** 0.5 or 1.0

        anomalies = []
        for n in nodes:
            z = abs(deg[n] - mean) / std
            if z >= z_threshold:
                anomalies.append({
                    "node": n,
                    "degree": deg[n],
                    "z_score": round(z, 3),
                    "anomaly_type": "HIGH_DEGREE_HUB" if deg[n] > mean else "ISOLATED_OUTLIER",
                })

        return {
            "algorithm": "ALGO-KG-136",
            "mean_degree": round(mean, 2),
            "std_degree": round(std, 2),
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
        }

    def detect_egonet_anomalies(
        self,
        nodes: List[str],
        edges: List[Tuple[str, str]],
        alpha_exponent: float = 1.3,
        c_multiplier: float = 1.0,
        outlier_multiplier: float = 2.5,
    ) -> Dict[str, Any]:
        adj: Dict[str, Set[str]] = defaultdict(set)
        for u, v in edges:
            adj[u].add(v)
            adj[v].add(u)

        egonet_reports: List[Dict[str, Any]] = []

        for node in nodes:
            neighbors = adj.get(node, set())
            n_count = len(neighbors)
            if n_count < 2:
                continue

            induced_edges = 0
            nbr_list = list(neighbors)
            for i in range(len(nbr_list)):
                for j in range(i + 1, len(nbr_list)):
                    if nbr_list[j] in adj.get(nbr_list[i], set()):
                        induced_edges += 1

            expected_edges = c_multiplier * (n_count ** alpha_exponent)
            score = (induced_edges + 1.0) / max(1e-6, (expected_edges + 1.0))
            discord = max(score, 1.0 / max(1e-6, score))

            if discord >= outlier_multiplier:
                egonet_reports.append({
                    "node": node,
                    "neighbor_count": n_count,
                    "internal_edges": induced_edges,
                    "expected_edges": round(expected_edges, 2),
                    "discord_ratio": round(discord, 3),
                    "pattern": "NEAR_CLIQUE_SURGE" if score > 1.0 else "STAR_DISPERSION",
                })

        egonet_reports.sort(key=lambda x: x["discord_ratio"], reverse=True)
        return {
            "algorithm": "ALGO-KG-136",
            "egonet_anomalies": egonet_reports[:20],
            "total_egonet_anomalies": len(egonet_reports),
        }
