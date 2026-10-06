"""
================================================================================
ALGORITHM BLUEPRINT: HEDGED REQUESTS (TAIL-LATENCY RESILIENCE DISPATCHER)
================================================================================

1. OVERVIEW:
   Hedged Requests is a latency-mitigation strategy for read-only distributed
   search queries. When an initial request to Replica A exceeds a latency threshold
   (typically p95 latency), a secondary speculative duplicate is dispatched to
   Replica B. Whichever replica returns first fulfills the caller's request while
   the lagging call is discarded, cutting tail latency (p99/p99.9) significantly.

2. OPERATIONAL RULES & INVARIANTS:
   - Read-Only Invariant: Hedging is strictly permitted ONLY on idempotent, read-only
     search queries. Mutating writes (file edits, commits) MUST NEVER be hedged.
   - Delay Gating: Hedging delay is dynamically calculated from rolling p95 latency.
   - Cancellation: Fast replica arrival triggers immediate cancellation of pending sibling.

3. COMPLEXITY ANALYSIS:
   - Tail Latency Reduction: 50%-80% reduction in p99.9 latency at cost of 2%-5% additional network traffic.
   - Resource Overhead: Negligible on healthy cluster tiers.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside function bodies.
================================================================================
"""

import time
from typing import Dict, List, Any, Optional, Callable


class SearchEngineHedgedRequestsAlgo:
    """
    Implements latency-hedged query simulation and replica response arbitration.
    """

    def arbitrate_replicas(
        self,
        primary_latency_ms: float,
        backup_latency_ms: float,
        hedge_delay_ms: float,
        primary_payload: Any,
        backup_payload: Any
    ) -> Dict[str, Any]:
        """
        Determines the winning replica response given hedged dispatch timings.
        """
        if primary_latency_ms <= hedge_delay_ms:
            return {
                "winner": "primary",
                "backup_triggered": False,
                "effective_latency_ms": primary_latency_ms,
                "winner_payload": primary_payload,
                "latency_saved_ms": 0.0
            }

        total_backup_time = hedge_delay_ms + backup_latency_ms
        if primary_latency_ms <= total_backup_time:
            return {
                "winner": "primary",
                "backup_triggered": True,
                "effective_latency_ms": primary_latency_ms,
                "winner_payload": primary_payload,
                "latency_saved_ms": 0.0
            }
        else:
            saved = primary_latency_ms - total_backup_time
            return {
                "winner": "backup",
                "backup_triggered": True,
                "effective_latency_ms": total_backup_time,
                "winner_payload": backup_payload,
                "latency_saved_ms": round(saved, 2)
            }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes hedged request simulation across mock replica latencies.
        """
        primary_latency = float(payload.get("primary_latency_ms", 120.0))
        backup_latency = float(payload.get("backup_latency_ms", 30.0))
        hedge_delay = float(payload.get("hedge_delay_ms", 50.0))
        p_data = payload.get("primary_data", {"result": "primary_data"})
        b_data = payload.get("backup_data", {"result": "backup_data"})

        arbitration = self.arbitrate_replicas(
            primary_latency_ms=primary_latency,
            backup_latency_ms=backup_latency,
            hedge_delay_ms=hedge_delay,
            primary_payload=p_data,
            backup_payload=b_data
        )

        return {
            "algorithm": "ALGO-SRCH-75",
            "hedge_parameters": {
                "primary_latency_ms": primary_latency,
                "backup_latency_ms": backup_latency,
                "hedge_delay_ms": hedge_delay
            },
            "arbitration_result": arbitration
        }
