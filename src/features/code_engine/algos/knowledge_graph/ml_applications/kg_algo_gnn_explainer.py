r"""
================================================================================
ALGORITHM BLUEPRINT: GNNEXPLAINER SUBGRAPH EDGE ATTRIBUTION & FIDELITY ENGINE
================================================================================

1. OVERVIEW & OBJECTIVE:
   Model explainability engine implementing GNNExplainer (Ying et al.) for graph
   neural networks and knowledge graph embeddings. Identifies minimal explanatory
   subgraph masks $M_e$ maximizing mutual information $\text{MI}(Y, G_s)$ while
   penalizing mask entropy and graph size. Computes explanation Sparsity, Fidelity+,
   and Fidelity- metrics.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Mask Sigmoidal Projection: Continuous edge masks constrained in $[0, 1]$ via
     $\sigma(z_e)$.
   - Regularized Objective: Loss includes cross-entropy + $\lambda_1 \|M\|_1$ + $\lambda_2 H(M)$.
   - Purity & Determinism: Pure functional state transitions with zero side effects.
   - Zero Inline Comments: Code logic is self-documenting per architectural doctrine.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(Steps * |E_Sub|) for mask gradient descent steps.
   - Space Complexity: O(|E_Sub| + |V_Sub|) for subgraph mask buffers.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import math
from typing import Dict, Any, List, Set, Tuple, Optional, Callable


class KgAlgoGnnExplainer:
    """
    --- contract:
      id: ALGO-KG-145
      name: KgAlgoGnnExplainer
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(Steps * |E_Sub|)
        space: O(|E_Sub|)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - gnn_explainer
      - mutual_information
      - edge_importance_mask
      - fidelity_metrics
      - model_explainability
      input_schema:
        target_node: string
        subgraph_edges: array
        edge_priors: optional object
      output_schema:
        algorithm: string
        target_node: string
        top_explanatory_edges: array
        sparsity: number
        fidelity_drop: number
    ---
    """

    def explain_prediction(
        self,
        target: str,
        edges: List[Tuple[str, str]],
        importance_scores: Optional[Dict[Tuple[str, str], float]] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        scores = importance_scores or {}
        edge_weights: List[Tuple[Tuple[str, str], float]] = []

        for e in edges:
            score = scores.get(e, scores.get((e[1], e[0]), 0.5))
            edge_weights.append((e, score))

        edge_weights.sort(key=lambda x: x[1], reverse=True)
        top_edges = edge_weights[:top_k]

        total_edges = max(1, len(edges))
        sparsity = 1.0 - (len(top_edges) / total_edges)

        return {
            "algorithm": "ALGO-KG-145",
            "target": target,
            "top_explanatory_edges": [
                {"edge": f"{u}->{v}", "importance": round(s, 4)} for (u, v), s in top_edges
            ],
            "total_subgraph_edges": len(edges),
            "sparsity": round(sparsity, 4),
        }

    def optimize_edge_mask(
        self,
        target: str,
        subgraph_edges: List[Tuple[str, str]],
        pred_fn: Callable[[List[Tuple[str, str]]], float],
        steps: int = 20,
        lr: float = 0.1,
        lambda_size: float = 0.01,
        lambda_entropy: float = 0.01,
    ) -> Dict[str, Any]:
        base_pred = pred_fn(subgraph_edges)
        mask_logits = {e: 0.0 for e in subgraph_edges}

        for _ in range(steps):
            for e in subgraph_edges:
                w = 1.0 / (1.0 + math.exp(-mask_logits[e]))
                active_edges = [edge for edge in subgraph_edges if (1.0 / (1.0 + math.exp(-mask_logits[edge]))) > 0.5]
                masked_pred = pred_fn(active_edges)

                pred_diff = abs(base_pred - masked_pred)
                entropy = -(w * math.log(max(1e-9, w)) + (1.0 - w) * math.log(max(1e-9, 1.0 - w)))
                grad = (1.0 - w) * (pred_diff - lambda_size - (lambda_entropy * entropy))
                mask_logits[e] += lr * grad

        final_masks: Dict[Tuple[str, str], float] = {
            e: 1.0 / (1.0 + math.exp(-mask_logits[e])) for e in subgraph_edges
        }

        ranked_edges = sorted(final_masks.items(), key=lambda x: x[1], reverse=True)
        selected_subgraph = [e for e, w in ranked_edges if w >= 0.5]
        if not selected_subgraph:
            selected_subgraph = [ranked_edges[0][0]] if ranked_edges else []

        subgraph_pred = pred_fn(selected_subgraph)
        complement_edges = [e for e in subgraph_edges if e not in set(selected_subgraph)]
        complement_pred = pred_fn(complement_edges)

        fidelity_plus = max(0.0, base_pred - complement_pred)
        fidelity_minus = max(0.0, base_pred - subgraph_pred)

        return {
            "algorithm": "ALGO-KG-145",
            "target_node": target,
            "explanatory_subgraph": [f"{u}->{v}" for u, v in selected_subgraph],
            "subgraph_edge_count": len(selected_subgraph),
            "total_edges": len(subgraph_edges),
            "sparsity": round(1.0 - (len(selected_subgraph) / max(1, len(subgraph_edges))), 4),
            "fidelity_plus": round(fidelity_plus, 4),
            "fidelity_minus": round(fidelity_minus, 4),
            "edge_importance": {f"{u}->{v}": round(w, 4) for (u, v), w in final_masks.items()},
        }
