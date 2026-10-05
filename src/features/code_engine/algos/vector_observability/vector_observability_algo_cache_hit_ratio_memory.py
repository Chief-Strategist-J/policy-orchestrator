"""
================================================================================
ALGORITHM BLUEPRINT: CACHE HIT RATIO & MEMORY PRESSURE AUDITOR (ALGO-VEC-OBS-185)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Monitors multi-tier cache effectiveness (embedding cache, query cache, OS page cache)
   and page fault / eviction pressure to detect working set overflow.

2. MATHEMATICAL FORMULATION:
   HitRatio = Hits / (Hits + Misses)
   MemoryPressureWarning = MajorPageFaultRate > threshold or EvictionRate > threshold
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoCacheHitRatioMemory:
    """
    --- contract:
      id: ALGO-VEC-OBS-185
      name: VectorObservabilityAlgoCacheHitRatioMemory
      category: observability
      complexity: O(1)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        cache_metrics: dict[str, Any]
        memory_stats: dict[str, Any]
        min_acceptable_hit_ratio: float
      output_schema:
        hit_ratio: float
        is_hit_ratio_healthy: bool
        memory_utilization_percent: float
        is_working_set_fitting_ram: bool
        recommendations: list[str]
    ---
    """

    @classmethod
    def evaluate(
        cls,
        cache_metrics: Dict[str, Any],
        memory_stats: Dict[str, Any],
        min_acceptable_hit_ratio: float = 0.80,
    ) -> Dict[str, Any]:
        hits = float(cache_metrics.get("hits", 0))
        misses = float(cache_metrics.get("misses", 0))
        evictions = int(cache_metrics.get("evictions_per_sec", 0))

        total_ops = hits + misses
        hit_ratio = hits / total_ops if total_ops > 0 else 1.0

        ram_used_gb = float(memory_stats.get("ram_used_gb", 8.0))
        ram_total_gb = float(memory_stats.get("ram_total_gb", 16.0))
        major_faults_per_sec = int(memory_stats.get("major_page_faults_per_sec", 0))

        ram_util = (ram_used_gb / ram_total_gb) * 100.0 if ram_total_gb > 0 else 0.0

        fits_ram = (major_faults_per_sec < 10) and (ram_util < 90.0)
        recs: List[str] = []

        if hit_ratio < min_acceptable_hit_ratio:
            recs.append("Increase cache capacity or inspect query parameter variance")
        if not fits_ram:
            recs.append("Memory pressure detected: consider scalar/product quantization (SQ/PQ) or horizontal sharding")
        if evictions > 100:
            recs.append(f"High cache eviction rate ({evictions}/sec) indicates thrashing")

        return {
            "hit_ratio": round(hit_ratio, 4),
            "is_hit_ratio_healthy": hit_ratio >= min_acceptable_hit_ratio,
            "memory_utilization_percent": round(ram_util, 2),
            "is_working_set_fitting_ram": fits_ram,
            "recommendations": recs,
        }
