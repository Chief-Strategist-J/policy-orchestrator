"""
================================================================================
ALGORITHM BLUEPRINT: CANARY QUERIES & SYNTHETIC PROBES HARNESS (ALGO-VEC-OBS-195)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Executes synthetic alive and invariant probes (search canary, write-to-read probe,
   delete probe, cross-tenant isolation probe) to continuously verify live serving state.

2. MATHEMATICAL FORMULATION:
   ProbePassRatio = PassedProbes / TotalProbes
   IsolationViolation = (CrossTenantReturnedCount > 0)
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoCanaryProbes:
    """
    --- contract:
      id: ALGO-VEC-OBS-195
      name: VectorObservabilityAlgoCanaryProbes
      category: observability
      complexity: O(P)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        canary_query_results: list[dict[str, Any]]
        isolation_probe_results: list[dict[str, Any]]
        write_freshness_seconds: Optional[float]
        max_allowed_freshness_seconds: float
      output_schema:
        is_all_probes_healthy: bool
        search_canary_pass_rate: float
        is_isolation_verified: bool
        probe_details: list[dict[str, Any]]
    ---
    """

    @classmethod
    def evaluate(
        cls,
        canary_query_results: List[Dict[str, Any]],
        isolation_probe_results: List[Dict[str, Any]],
        write_freshness_seconds: Optional[float] = None,
        max_allowed_freshness_seconds: float = 30.0,
    ) -> Dict[str, Any]:
        details: List[Dict[str, Any]] = []
        canary_passed = 0
        total_canaries = len(canary_query_results)

        for cq in canary_query_results:
            q_name = str(cq.get("canary_name", "canary"))
            expected_id = str(cq.get("expected_top_id", ""))
            actual_top_id = str(cq.get("actual_top_id", ""))
            passed = (expected_id == actual_top_id) and bool(expected_id)
            if passed:
                canary_passed += 1
            details.append({"probe_type": "SEARCH_CANARY", "name": q_name, "passed": passed})

        canary_pass_rate = canary_passed / float(total_canaries) if total_canaries > 0 else 1.0

        isolation_clean = True
        for iso in isolation_probe_results:
            tenant_a = str(iso.get("tenant_a", "A"))
            tenant_b_records_found = int(iso.get("tenant_b_records_found", 0))
            passed = (tenant_b_records_found == 0)
            if not passed:
                isolation_clean = False
            details.append({"probe_type": "ISOLATION_PROBE", "tenant": tenant_a, "passed": passed, "leaked_records": tenant_b_records_found})

        freshness_clean = True
        if write_freshness_seconds is not None:
            passed = write_freshness_seconds <= max_allowed_freshness_seconds
            if not passed:
                freshness_clean = False
            details.append({"probe_type": "WRITE_FRESHNESS", "lag_seconds": write_freshness_seconds, "passed": passed})

        all_healthy = (canary_pass_rate == 1.0) and isolation_clean and freshness_clean

        return {
            "is_all_probes_healthy": all_healthy,
            "search_canary_pass_rate": round(canary_pass_rate, 4),
            "is_isolation_verified": isolation_clean,
            "probe_details": details,
        }
