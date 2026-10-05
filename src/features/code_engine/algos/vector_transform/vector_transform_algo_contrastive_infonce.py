"""
================================================================================
ALGORITHM BLUEPRINT: CONTRASTIVE TRAINING (INFONCE) (ALGO-VEC-TRFM-07)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Computes symmetric InfoNCE contrastive loss over a batch of query-document
   embedding pairs with in-batch negatives. Pulls matching positive representations
   together while repelling all other batch entries scaled by calibrated temperature τ.

2. ARCHITECTURAL ROLE:
   Transformer & Operator role (Layer 1). Evaluates representation alignment, embedding
   fine-tuning quality, and multi-vector separation metrics.

3. EXECUTION FLOW:
   a. Compute cosine similarity matrix between query batch Q and document batch D.
   b. Scale matrix entries by 1.0 / temperature (τ).
   c. Compute cross-entropy loss along query-to-doc and doc-to-query axes (symmetric InfoNCE).
   d. Compute batch accuracy (% where diagonal index is highest similarity).
================================================================================
"""

from typing import Any, Dict, List, Optional
import math


class VectorTransformAlgoContrastiveInfoNCE:
    """
    --- contract:
      id: ALGO-VEC-TRFM-07
      name: VectorTransformAlgoContrastiveInfoNCE
      category: transform
      complexity: O(B^2 * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        query_vectors: list[list[float]]
        document_vectors: list[list[float]]
        temperature: float
      output_schema:
        batch_size: int
        temperature: float
        infonce_loss: float
        top1_accuracy: float
        similarity_matrix: list[list[float]]
    ---
    """

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x ** 2 for x in a))
        norm_b = math.sqrt(sum(y ** 2 for y in b))
        denom = norm_a * norm_b
        return dot / denom if denom > 1e-12 else 0.0

    @staticmethod
    def compute_loss(
        query_vectors: List[List[float]],
        document_vectors: List[List[float]],
        temperature: float = 0.05,
    ) -> Dict[str, Any]:
        if not query_vectors or not document_vectors or len(query_vectors) != len(document_vectors):
            return {
                "batch_size": 0,
                "temperature": temperature,
                "infonce_loss": 0.0,
                "top1_accuracy": 0.0,
                "similarity_matrix": [],
            }

        b = len(query_vectors)
        sim_matrix: List[List[float]] = []

        for i in range(b):
            row: List[float] = []
            for j in range(b):
                s = VectorTransformAlgoContrastiveInfoNCE._cosine(query_vectors[i], document_vectors[j])
                row.append(round(s, 6))
            sim_matrix.append(row)

        total_loss = 0.0
        correct_count = 0

        for i in range(b):
            row_scaled = [s / max(temperature, 1e-6) for s in sim_matrix[i]]
            max_val = max(row_scaled)
            exp_row = [math.exp(v - max_val) for v in row_scaled]
            sum_exp = sum(exp_row)
            log_prob = (row_scaled[i] - max_val) - math.log(sum_exp)
            total_loss -= log_prob

            best_j = max(range(b), key=lambda j: sim_matrix[i][j])
            if best_j == i:
                correct_count += 1

        avg_loss = round(total_loss / b, 6)
        acc = round(correct_count / b, 4)

        return {
            "batch_size": b,
            "temperature": temperature,
            "infonce_loss": avg_loss,
            "top1_accuracy": acc,
            "similarity_matrix": sim_matrix,
        }
