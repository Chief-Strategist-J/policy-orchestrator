"""
================================================================================
ALGORITHM BLUEPRINT: PARTITION-AWARE SHARD ROUTING (ALGO-VEC-SRCH-100)
================================================================================

Partition-aware shard routing organizes vector data onto distributed shards by
spatial cluster centroids. When a query vector arrives, the coordinator computes
distances only to the cluster centroids, identifying the top-p closest centroids
and routing the query exclusively to the subset of shards hosting those clusters,
drastically reducing network fan-out and total compute.
"""

from typing import Any, Dict, List, Optional
import math


class VectorSearchAlgoPartitionAwareRouting:
    """
    --- contract:
      id: ALGO-VEC-SRCH-100
      name: VectorSearchAlgoPartitionAwareRouting
      category: vector
      complexity: O(C * D + p log C)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        centroids: list[list[float]]
        centroid_to_shard_map: dict[str, str]
        query_vector: list[float]
        num_target_shards: int
      output_schema:
        total_centroids: int
        num_target_shards: int
        selected_shards: list[str]
        selected_centroids: list[dict[str, any]]
    ---
    """

    @staticmethod
    def _l2_dist(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(min(len(a), len(b)))))

    @staticmethod
    def route_to_shards(
        centroids: List[List[float]],
        centroid_to_shard_map: Dict[str, str],
        query_vector: List[float],
        num_target_shards: int = 2,
    ) -> Dict[str, Any]:
        if not centroids or not query_vector:
            return {
                "total_centroids": len(centroids),
                "num_target_shards": num_target_shards,
                "selected_shards": [],
                "selected_centroids": [],
            }

        centroid_distances = []
        for c_idx, c_vec in enumerate(centroids):
            d = VectorSearchAlgoPartitionAwareRouting._l2_dist(query_vector, c_vec)
            shard_id = centroid_to_shard_map.get(str(c_idx), f"shard_{c_idx % max(1, num_target_shards)}")
            centroid_distances.append({
                "centroid_id": c_idx,
                "distance": round(d, 6),
                "shard_id": shard_id,
            })

        centroid_distances.sort(key=lambda x: x["distance"])

        selected_shards_set = set()
        chosen_shards = []
        for cd in centroid_distances:
            sid = cd["shard_id"]
            if sid not in selected_shards_set:
                selected_shards_set.add(sid)
                chosen_shards.append(sid)
                if len(chosen_shards) >= num_target_shards:
                    break

        return {
            "total_centroids": len(centroids),
            "num_target_shards": num_target_shards,
            "selected_shards": chosen_shards,
            "selected_centroids": centroid_distances[:len(chosen_shards) * 2],
        }
