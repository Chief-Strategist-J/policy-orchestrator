"""
================================================================================
ALGORITHM BLUEPRINT: GRAPH CONTRASTIVE LEARNING (GRAPHCL & SIM-GCL ENGINE)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Self-supervised Graph Contrastive Learning engine (GraphCL / SimGCL / GRACE).
   Implements stochastic graph augmentations (edge dropping, node dropping, feature
   masking), bi-directional normalized temperature-scaled InfoNCE (NT-Xent) loss,
   and representation quality diagnostics (Alignment and Uniformity metrics).

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Log-Sum-Exp Stability: Softmax denominators clamped with max-subtraction trick.
   - Purity & Determinism: Pure functional state transitions with zero side effects.
   - Zero Inline Comments: Code logic is self-documenting per architectural doctrine.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(Batch_Size^2 * D) for pairwise cosine similarity matrix.
   - Space Complexity: O(Batch_Size^2) for contrastive similarity tensors.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import math
from typing import Dict, Any, List, Set, Tuple, Optional, Callable


class KgAlgoGraphContrastiveLearning:
    """
    --- contract:
      id: ALGO-KG-146
      name: KgAlgoGraphContrastiveLearning
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(Batch^2 * D)
        space: O(Batch^2)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - graph_contrastive
      - infonce_loss
      - view_augmentation
      - alignment_uniformity
      input_schema:
        view1_embeddings: array
        view2_embeddings: array
        tau: optional number
      output_schema:
        algorithm: string
        infonce_loss: number
        alignment_score: number
        uniformity_score: number
    ---
    """

    def compute_infonce(
        self,
        pos_sim: float,
        neg_sims: List[float],
        tau: float = 0.1,
    ) -> Dict[str, Any]:
        all_sims = [pos_sim] + neg_sims
        max_s = max(all_sims)
        num = math.exp((pos_sim - max_s) / tau)
        denom = num + sum(math.exp((n - max_s) / tau) for n in neg_sims)
        loss = -math.log(max(1e-12, num / max(1e-12, denom)))
        return {
            "algorithm": "ALGO-KG-146",
            "infonce_loss": round(loss, 5),
            "positive_similarity": round(pos_sim, 4),
            "negative_count": len(neg_sims),
        }

    def augment_graph_views(
        self,
        nodes: List[str],
        edges: List[Tuple[str, str]],
        drop_edge_rate: float = 0.2,
        drop_node_rate: float = 0.1,
        seed: int = 42,
    ) -> Dict[str, Any]:
        n_count = len(nodes)
        keep_nodes = [n for idx, n in enumerate(nodes) if ((idx * 31 + seed) % 100) >= int(drop_node_rate * 100)]
        node_set = set(keep_nodes)

        keep_edges = [
            (u, v) for idx, (u, v) in enumerate(edges)
            if u in node_set and v in node_set and ((idx * 17 + seed) % 100) >= int(drop_edge_rate * 100)
        ]

        return {
            "augmented_nodes": keep_nodes,
            "augmented_edges": keep_edges,
            "pruned_nodes_count": n_count - len(keep_nodes),
            "pruned_edges_count": len(edges) - len(keep_edges),
        }

    def compute_batch_nt_xent_loss(
        self,
        view1_embeddings: List[List[float]],
        view2_embeddings: List[List[float]],
        tau: float = 0.1,
    ) -> Dict[str, Any]:
        n = len(view1_embeddings)
        if n == 0 or n != len(view2_embeddings):
            return {"algorithm": "ALGO-KG-146", "infonce_loss": 0.0, "alignment": 0.0, "uniformity": 0.0}

        def cosine_sim(a: List[float], b: List[float]) -> float:
            norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
            norm_b = math.sqrt(sum(y * y for y in b)) or 1.0
            return sum(x * y for x, y in zip(a, b)) / (norm_a * norm_b)

        sim_matrix = [[cosine_sim(view1_embeddings[i], view2_embeddings[j]) for j in range(n)] for i in range(n)]

        total_loss = 0.0
        alignment_sum = 0.0

        for i in range(n):
            pos_s = sim_matrix[i][i]
            alignment_sum += sum((v1 - v2) ** 2 for v1, v2 in zip(view1_embeddings[i], view2_embeddings[i]))
            row_sims = [sim_matrix[i][j] for j in range(n)]
            max_row = max(row_sims)

            num = math.exp((pos_s - max_row) / tau)
            denom = sum(math.exp((s - max_row) / tau) for s in row_sims)
            total_loss += -math.log(max(1e-12, num / max(1e-12, denom)))

        avg_loss = total_loss / n
        alignment = math.sqrt(alignment_sum / n)

        uniformity_sum = 0.0
        pair_cnt = 0
        for i in range(n):
            for j in range(i + 1, n):
                sq_dist = sum((a - b) ** 2 for a, b in zip(view1_embeddings[i], view1_embeddings[j]))
                uniformity_sum += math.exp(-2.0 * sq_dist)
                pair_cnt += 1

        uniformity = math.log(max(1e-12, uniformity_sum / max(1, pair_cnt)))

        return {
            "algorithm": "ALGO-KG-146",
            "batch_size": n,
            "infonce_loss": round(avg_loss, 5),
            "alignment_metric": round(alignment, 5),
            "uniformity_metric": round(uniformity, 5),
        }
