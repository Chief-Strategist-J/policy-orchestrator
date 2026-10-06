"""
================================================================================
ALGORITHM BLUEPRINT: WEISFEILER-LEHMAN (1-WL) RELATIONAL GRAPH KERNEL ENGINE
================================================================================

1. OVERVIEW & OBJECTIVE:
   Weisfeiler-Lehman (1-WL) graph isomorphism and subtree pattern kernel engine.
   Computes deterministic multiset neighbor color compression across h iteration
   rounds, generates explicit graph subtree frequency histograms, and evaluates the
   normalized 1-WL inner product kernel metric between graph representations.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Multiset Invariance: Neighbor colors are sorted prior to hashing for permutation
     invariance.
   - Kernel Positive Semi-Definiteness: Normalized inner product strictly bounded in [0, 1].
   - Purity & Determinism: Pure functional state transitions with zero side effects.
   - Zero Inline Comments: Code logic is self-documenting per architectural doctrine.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(h * (|V| + |E|)) per graph evaluation.
   - Space Complexity: O(|V| + |Color_Vocabulary|) for color maps and histograms.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import hashlib
from collections import defaultdict
from typing import Dict, Any, List, Set, Tuple, Optional, Callable


class KgAlgoWeisfeilerLehmanKernel:
    """
    --- contract:
      id: ALGO-KG-140
      name: KgAlgoWeisfeilerLehmanKernel
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(H * (V + E))
        space: O(V + Vocabulary)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - wl_kernel
      - graph_isomorphism
      - subtree_patterns
      - kernel_similarity
      input_schema:
        nodes: array
        edges: array
        h_iterations: integer
      output_schema:
        algorithm: string
        color_histogram: object
        vocabulary_size: integer
    ---
    """

    def compute_wl_colors(
        self,
        nodes: List[str],
        edges: List[Tuple[str, str]],
        h: int = 2,
        initial_labels: Optional[Dict[str, str]] = None,
    ) -> Dict[str, int]:
        adj: Dict[str, List[str]] = defaultdict(list)
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        colors: Dict[str, str] = {}
        for n in nodes:
            colors[n] = initial_labels.get(n, "0") if initial_labels else "0"

        histogram: Dict[str, int] = defaultdict(int)
        for n in nodes:
            histogram[colors[n]] += 1

        for _ in range(h):
            new_colors: Dict[str, str] = {}
            for n in nodes:
                neighbor_colors = sorted([colors[nbr] for nbr in adj.get(n, [])])
                signature = f"{colors[n]}|" + ",".join(neighbor_colors)
                digest = hashlib.md5(signature.encode("utf-8")).hexdigest()[:8]
                new_colors[n] = digest
                histogram[digest] += 1
            colors = new_colors

        return dict(histogram)

    def compute_kernel_similarity(
        self,
        graph1: Tuple[List[str], List[Tuple[str, str]]],
        graph2: Tuple[List[str], List[Tuple[str, str]]],
        h: int = 2,
    ) -> Dict[str, Any]:
        nodes1, edges1 = graph1
        nodes2, edges2 = graph2

        hist1 = self.compute_wl_colors(nodes1, edges1, h=h)
        hist2 = self.compute_wl_colors(nodes2, edges2, h=h)

        shared_keys = set(hist1.keys()).union(set(hist2.keys()))

        dot_product = sum(hist1.get(k, 0) * hist2.get(k, 0) for k in shared_keys)
        norm1 = sum(v * v for v in hist1.values()) ** 0.5 or 1.0
        norm2 = sum(v * v for v in hist2.values()) ** 0.5 or 1.0

        normalized_kernel = dot_product / (norm1 * norm2)

        return {
            "algorithm": "ALGO-KG-140",
            "iterations": h,
            "raw_kernel_score": dot_product,
            "normalized_similarity": round(normalized_kernel, 5),
            "graph1_features_count": len(hist1),
            "graph2_features_count": len(hist2),
            "isomorphic_candidate": normalized_kernel >= 0.99999 and len(nodes1) == len(nodes2) and len(edges1) == len(edges2),
        }
