"""
================================================================================
ALGORITHM BLUEPRINT: INCREMENTAL (STREAMING) PCA (ALGO-VEC-TRFM-30)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Updates principal components incrementally over streaming mini-batches of vector
   data without keeping the entire corpus in RAM (Ross et al., Incremental SVD).
   Maintains running mean, sample count, and singular components dynamically.

2. ARCHITECTURAL ROLE:
   Transformer & Operator role (Layer 1). Enables continuous adaptation of projection
   matrices in streaming pipelines as new documents arrive.

3. EXECUTION FLOW:
   a. Receive new mini-batch of vectors X_batch.
   b. Combine batch with previous running mean and components via QR decomposition.
   c. Truncate updated SVD to target_dim.
   d. Update running sample count and singular values.
   e. Return updated components and current projection of the batch.
================================================================================
"""

from typing import Any, Dict, List, Optional
import numpy as np


class VectorTransformAlgoIncrementalPCA:
    """
    --- contract:
      id: ALGO-VEC-TRFM-30
      name: VectorTransformAlgoIncrementalPCA
      category: transform
      complexity: O(B * D * k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        batch_vectors: list[list[float]]
        existing_components: list[list[float]]
        existing_mean: list[float]
        sample_count: int
        target_dim: int
      output_schema:
        total_samples_seen: int
        target_dim: int
        updated_mean: list[float]
        updated_components: list[list[float]]
        projected_batch: list[list[float]]
    ---
    """

    @staticmethod
    def partial_fit_transform(
        batch_vectors: List[List[float]],
        existing_components: Optional[List[List[float]]] = None,
        existing_mean: Optional[List[float]] = None,
        sample_count: int = 0,
        target_dim: int = 8,
    ) -> Dict[str, Any]:
        if not batch_vectors:
            return {
                "total_samples_seen": sample_count,
                "target_dim": target_dim,
                "updated_mean": existing_mean or [],
                "updated_components": existing_components or [],
                "projected_batch": [],
            }

        X_b = np.asarray(batch_vectors, dtype=np.float64)
        n_b, d = X_b.shape
        k = min(target_dim, d)

        mean_b = np.mean(X_b, axis=0)

        if existing_mean is None or sample_count == 0 or existing_components is None:
            new_count = n_b
            new_mean = mean_b
            X_centered = X_b - new_mean
            _, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
            new_components = Vt[:k, :]
        else:
            prev_mean = np.asarray(existing_mean, dtype=np.float64)
            prev_V = np.asarray(existing_components, dtype=np.float64)
            new_count = sample_count + n_b

            new_mean = (sample_count * prev_mean + n_b * mean_b) / new_count
            delta_mean = mean_b - prev_mean

            X_centered = X_b - new_mean
            stacked = np.vstack([
                prev_V * np.sqrt(sample_count),
                X_centered,
                np.sqrt((sample_count * n_b) / new_count) * delta_mean,
            ])
            _, _, Vt = np.linalg.svd(stacked, full_matrices=False)
            new_components = Vt[:k, :]

        projected = (X_b - new_mean) @ new_components.T

        return {
            "total_samples_seen": new_count,
            "target_dim": k,
            "updated_mean": [round(float(x), 6) for x in new_mean],
            "updated_components": [[round(float(x), 6) for x in row] for row in new_components],
            "projected_batch": [[round(float(x), 6) for x in row] for row in projected],
        }
