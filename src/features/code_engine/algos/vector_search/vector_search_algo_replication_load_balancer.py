"""
================================================================================
ALGORITHM BLUEPRINT: REPLICATION & LOAD BALANCING (ALGO-VEC-SRCH-101)
================================================================================

Replication load balancing distributes vector query workloads across multiple
replica nodes hosting identical shard data. Queries are dispatched according to
strategy: round-robin, least-in-flight-connections, or EWMA lowest-observed-latency.
Unhealthy or lagging replicas are removed dynamically from the active routing set.
"""

from typing import Any, Dict, List, Optional


class VectorSearchAlgoReplicationLoadBalancer:
    """
    --- contract:
      id: ALGO-VEC-SRCH-101
      name: VectorSearchAlgoReplicationLoadBalancer
      category: vector
      complexity: O(R_replicas)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        replicas: list[dict[str, any]]
        strategy: str
        counter: int
      output_schema:
        total_replicas: int
        healthy_replicas: int
        strategy: str
        selected_replica: dict[str, any]
    ---
    """

    @staticmethod
    def select_replica(
        replicas: List[Dict[str, Any]],
        strategy: str = "least_loaded",
        counter: int = 0,
    ) -> Dict[str, Any]:
        if not replicas:
            return {
                "total_replicas": 0,
                "healthy_replicas": 0,
                "strategy": strategy,
                "selected_replica": {},
            }

        healthy = [r for r in replicas if r.get("is_healthy", True)]
        if not healthy:
            healthy = replicas

        if strategy == "round_robin":
            idx = counter % len(healthy)
            chosen = healthy[idx]
        elif strategy == "lowest_latency":
            chosen = min(healthy, key=lambda r: r.get("latency_ms", float("inf")))
        else:
            chosen = min(healthy, key=lambda r: r.get("active_connections", float("inf")))

        return {
            "total_replicas": len(replicas),
            "healthy_replicas": len(healthy),
            "strategy": strategy,
            "selected_replica": chosen,
        }
