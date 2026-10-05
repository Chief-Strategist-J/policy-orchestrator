"""
================================================================================
ALGORITHM BLUEPRINT: RETRIEVAL FAILURE CLUSTERING (ALGO-VEC-OBS-194)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Clusters failed or low-score queries (no-hit queries, thumbs-down queries, OOD queries)
   by semantic vector distance to isolate shared root-cause topics or content gaps.

2. MATHEMATICAL FORMULATION:
   Leader-Follower Online Clustering: assigns query to nearest cluster if distance <= threshold,
   otherwise forms a new cluster.
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoFailureClustering:
    """
    --- contract:
      id: ALGO-VEC-OBS-194
      name: VectorObservabilityAlgoFailureClustering
      category: observability
      complexity: O(N * K * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        failed_queries: list[dict[str, Any]]
        cluster_distance_threshold: float
      output_schema:
        cluster_count: int
        clusters: list[dict[str, Any]]
        largest_failure_topic: Optional[str]
    ---
    """

    @classmethod
    def cluster_failures(
        cls,
        failed_queries: List[Dict[str, Any]],
        cluster_distance_threshold: float = 0.50,
    ) -> Dict[str, Any]:
        if not failed_queries:
            return {
                "cluster_count": 0,
                "clusters": [],
                "largest_failure_topic": None,
            }

        clusters: List[Dict[str, Any]] = []

        for q in failed_queries:
            q_id = str(q.get("query_id", "q"))
            q_text = str(q.get("query_text", ""))
            q_vec = q.get("vector", [])

            best_c_idx = -1
            min_dist = float("inf")

            for c_idx, cluster in enumerate(clusters):
                c_center = cluster["centroid"]
                if len(c_center) == len(q_vec) and q_vec:
                    dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(q_vec, c_center)))
                    if dist < min_dist:
                        min_dist = dist
                        best_c_idx = c_idx

            if best_c_idx >= 0 and min_dist <= cluster_distance_threshold:
                target_c = clusters[best_c_idx]
                target_c["query_ids"].append(q_id)
                target_c["sample_queries"].append(q_text)
                old_cnt = target_c["size"]
                new_cnt = old_cnt + 1
                target_c["size"] = new_cnt
                if q_vec:
                    target_c["centroid"] = [
                        (target_c["centroid"][d] * old_cnt + q_vec[d]) / float(new_cnt)
                        for d in range(len(q_vec))
                    ]
            else:
                clusters.append({
                    "cluster_id": f"cluster-{len(clusters)}",
                    "centroid": list(q_vec),
                    "size": 1,
                    "query_ids": [q_id],
                    "sample_queries": [q_text],
                })

        clusters.sort(key=lambda x: x["size"], reverse=True)
        largest_topic = clusters[0]["sample_queries"][0] if clusters and clusters[0]["sample_queries"] else None

        sanitized_clusters = []
        for c in clusters:
            sanitized_clusters.append({
                "cluster_id": c["cluster_id"],
                "size": c["size"],
                "query_ids": c["query_ids"][:20],
                "sample_queries": c["sample_queries"][:5],
            })

        return {
            "cluster_count": len(clusters),
            "clusters": sanitized_clusters,
            "largest_failure_topic": largest_topic,
        }
