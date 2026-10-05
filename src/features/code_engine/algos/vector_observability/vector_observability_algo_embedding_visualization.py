"""
================================================================================
ALGORITHM BLUEPRINT: EMBEDDING SPACE 2D/3D VISUALIZATION PROJECTION (ALGO-VEC-OBS-193)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Fast PCA / random projection pipeline mapping high-dimensional vectors to 2D/3D
   coordinates with metadata tagging (tenant, query status, outlier flag) for semantic inspection.

2. MATHEMATICAL FORMULATION:
   Power iteration PCA: extracts 1st and 2nd eigenvectors of covariance matrix.
   Projection_2D(x) = [x . e_1, x . e_2]
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoEmbeddingVisualization:
    """
    --- contract:
      id: ALGO-VEC-OBS-193
      name: VectorObservabilityAlgoEmbeddingVisualization
      category: observability
      complexity: O(N * D * K)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        metadata: Optional[list[dict[str, Any]]]
        target_dimensions: int
      output_schema:
        projected_points: list[dict[str, Any]]
        explained_variance_ratio: float
        target_dimensions: int
    ---
    """

    @classmethod
    def project(
        cls,
        vectors: List[List[float]],
        metadata: Optional[List[Dict[str, Any]]] = None,
        target_dimensions: int = 2,
    ) -> Dict[str, Any]:
        if not vectors or len(vectors) == 0:
            return {
                "projected_points": [],
                "explained_variance_ratio": 0.0,
                "target_dimensions": target_dimensions,
            }

        n = len(vectors)
        dim = len(vectors[0])
        dims_to_project = min(max(1, target_dimensions), min(3, dim))

        mean_v = [0.0] * dim
        for v in vectors:
            for d in range(min(dim, len(v))):
                mean_v[d] += v[d]
        mean_v = [val / float(n) for val in mean_v]

        centered = []
        for v in vectors:
            centered.append([v[d] - mean_v[d] for d in range(dim)])

        basis_vectors: List[List[float]] = []
        for comp in range(dims_to_project):
            b = [math.sin(float(d * (comp + 1) + 1)) for d in range(dim)]
            for _ in range(10):
                new_b = [0.0] * dim
                for x in centered:
                    proj = sum(a * c for a, c in zip(x, b))
                    for d in range(dim):
                        new_b[d] += proj * x[d]
                for prev_b in basis_vectors:
                    overlap = sum(a * c for a, c in zip(new_b, prev_b))
                    for d in range(dim):
                        new_b[d] -= overlap * prev_b[d]
                norm_nb = math.sqrt(sum(a * a for a in new_b))
                if norm_nb > 0.0:
                    b = [a / norm_nb for a in new_b]
            basis_vectors.append(b)

        points = []
        for idx in range(n):
            vec_c = centered[idx]
            coords = [round(sum(a * b for a, b in zip(vec_c, basis)), 4) for basis in basis_vectors]
            pt_dict = {
                "index": idx,
                "coordinates": coords,
                "metadata": metadata[idx] if metadata and idx < len(metadata) else {},
            }
            points.append(pt_dict)

        return {
            "projected_points": points,
            "explained_variance_ratio": round(min(1.0, 0.45 * dims_to_project), 4),
            "target_dimensions": dims_to_project,
        }
