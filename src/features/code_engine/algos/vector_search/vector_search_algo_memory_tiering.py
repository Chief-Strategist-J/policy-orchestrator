"""
================================================================================
ALGORITHM BLUEPRINT: MEMORY TIERING (RAM / MMAP / SSD) (ALGO-VEC-SRCH-107)
================================================================================

Memory tiering partitions vector index components across memory hierarchies based on
access frequency and latency criticality:
Tier 1 (RAM): Cluster centroids, coarse quantizers, upper graph levels, PQ lookup tables.
Tier 2 (MMAP / SSD): Quantized vector payload codes, inverted list offsets.
Tier 3 (Cold Disk / Object Store): Full-precision FP32 vectors for re-scoring on demand.
"""

from typing import Any, Dict, List, Optional


class VectorSearchAlgoMemoryTiering:
    """
    --- contract:
      id: ALGO-VEC-SRCH-107
      name: VectorSearchAlgoMemoryTiering
      category: vector
      complexity: O(|components|)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        components: list[dict[str, any]]
        ram_budget_mb: float
      output_schema:
        total_components: int
        ram_allocated_mb: float
        ssd_allocated_mb: float
        ram_budget_mb: float
        budget_exceeded: bool
        placement_plan: list[dict[str, any]]
    ---
    """

    @staticmethod
    def plan_tiering(
        components: List[Dict[str, Any]],
        ram_budget_mb: float = 1024.0,
    ) -> Dict[str, Any]:
        if not components:
            return {
                "total_components": 0,
                "ram_allocated_mb": 0.0,
                "ssd_allocated_mb": 0.0,
                "ram_budget_mb": ram_budget_mb,
                "budget_exceeded": False,
                "placement_plan": [],
            }

        sorted_components = sorted(
            components,
            key=lambda c: c.get("access_priority", 0),
            reverse=True,
        )

        ram_used = 0.0
        ssd_used = 0.0
        plan: List[Dict[str, Any]] = []

        for comp in sorted_components:
            name = comp.get("name", "unknown")
            size_mb = comp.get("size_mb", 0.0)
            pinned = comp.get("must_pin_ram", False)

            if pinned or (ram_used + size_mb <= ram_budget_mb):
                tier = "RAM"
                ram_used += size_mb
            else:
                tier = "SSD_MMAP"
                ssd_used += size_mb

            plan.append({
                "component": name,
                "size_mb": size_mb,
                "assigned_tier": tier,
                "access_priority": comp.get("access_priority", 0),
            })

        return {
            "total_components": len(components),
            "ram_allocated_mb": round(ram_used, 2),
            "ssd_allocated_mb": round(ssd_used, 2),
            "ram_budget_mb": ram_budget_mb,
            "budget_exceeded": ram_used > ram_budget_mb,
            "placement_plan": plan,
        }
