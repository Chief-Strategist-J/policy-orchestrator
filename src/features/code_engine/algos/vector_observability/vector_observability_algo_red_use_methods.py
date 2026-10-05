"""
================================================================================
ALGORITHM BLUEPRINT: RED AND USE METHODS HEALTH AUDITOR (ALGO-VEC-OBS-179)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Implements unified health auditing evaluating service-level RED (Rate, Errors, Duration)
   and resource-level USE (Utilization, Saturation, Errors) across vector components.

2. MATHEMATICAL FORMULATION:
   ErrorRate = Errors / TotalRequests
   SaturationWarning = QueuedWork > 0 and Utilization > max_target_utilization
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoRedUseMethods:
    """
    --- contract:
      id: ALGO-VEC-OBS-179
      name: VectorObservabilityAlgoRedUseMethods
      category: observability
      complexity: O(1)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        service_red: dict[str, Any]
        resource_use: dict[str, Any]
      output_schema:
        overall_health_status: str
        red_metrics_summary: dict[str, Any]
        use_metrics_summary: dict[str, Any]
        critical_alerts: list[str]
    ---
    """

    @classmethod
    def evaluate(
        cls,
        service_red: Dict[str, Any],
        resource_use: Dict[str, Any],
    ) -> Dict[str, Any]:
        total_reqs = float(service_red.get("total_requests", 100))
        error_count = float(service_red.get("error_count", 0))
        duration_p99_ms = float(service_red.get("duration_p99_ms", 20.0))
        rate_qps = float(service_red.get("requests_per_second", 50.0))

        error_rate = error_count / total_reqs if total_reqs > 0 else 0.0

        cpu_util = float(resource_use.get("cpu_utilization_percent", 40.0))
        mem_util = float(resource_use.get("memory_utilization_percent", 60.0))
        queue_len = int(resource_use.get("queue_saturation_count", 0))
        resource_errors = int(resource_use.get("io_error_count", 0))

        alerts: List[str] = []
        if error_rate > 0.01:
            alerts.append(f"RED alert: Error rate is {error_rate*100:.2f}% (exceeds 1.0%)")
        if duration_p99_ms > 200.0:
            alerts.append(f"RED alert: p99 Latency is {duration_p99_ms:.1f}ms (exceeds 200ms)")
        if cpu_util > 85.0 or mem_util > 90.0:
            alerts.append(f"USE alert: High utilization (CPU {cpu_util}%, Mem {mem_util}%)")
        if queue_len > 50:
            alerts.append(f"USE alert: Resource saturation queue depth ({queue_len}) indicates thread pool starvation")
        if resource_errors > 0:
            alerts.append(f"USE alert: {resource_errors} resource I/O errors detected")

        if len(alerts) >= 2 or error_rate > 0.05:
            status = "CRITICAL"
        elif len(alerts) == 1:
            status = "DEGRADED"
        else:
            status = "HEALTHY"

        return {
            "overall_health_status": status,
            "red_metrics_summary": {
                "requests_per_second": rate_qps,
                "error_rate": round(error_rate, 4),
                "p99_duration_ms": duration_p99_ms,
            },
            "use_metrics_summary": {
                "cpu_percent": cpu_util,
                "memory_percent": mem_util,
                "queue_saturation": queue_len,
                "resource_errors": resource_errors,
            },
            "critical_alerts": alerts,
        }
