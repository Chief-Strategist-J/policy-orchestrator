"""
================================================================================
ALGORITHM BLUEPRINT: ADMISSION CONTROL & RATE LIMITING (ALGO-VEC-SRCH-109)
================================================================================

Admission control protects retrieval nodes from saturation during traffic surges
via token-bucket rate limiting, concurrency bulkheads, and adaptive load shedding.
Under high resource saturation, the engine downgrades retrieval complexity (e.g.
reducing ef_search or skipping heavy cross-encoders) rather than failing requests,
ensuring graceful availability degradation.
"""

from typing import Any, Dict, List, Optional
import time


class VectorSearchAlgoAdmissionControl:
    """
    --- contract:
      id: ALGO-VEC-SRCH-109
      name: VectorSearchAlgoAdmissionControl
      category: vector
      complexity: O(1)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        current_tokens: float
        max_tokens: float
        refill_rate_per_sec: float
        last_refill_timestamp: float
        current_concurrency: int
        max_concurrency: int
        request_cost: float
      output_schema:
        admitted: bool
        degraded_mode: bool
        recommended_ef_search: int
        new_token_balance: float
        retry_after_seconds: float
    ---
    """

    @staticmethod
    def evaluate_admission(
        current_tokens: float,
        max_tokens: float,
        refill_rate_per_sec: float,
        last_refill_timestamp: float,
        current_concurrency: int,
        max_concurrency: int,
        request_cost: float = 1.0,
        now: Optional[float] = None,
    ) -> Dict[str, Any]:
        if now is None:
            now = time.time()

        elapsed = max(0.0, now - last_refill_timestamp)
        tokens = min(max_tokens, current_tokens + elapsed * refill_rate_per_sec)

        if current_concurrency >= max_concurrency:
            return {
                "admitted": False,
                "degraded_mode": False,
                "recommended_ef_search": 0,
                "new_token_balance": round(tokens, 2),
                "retry_after_seconds": 1.0,
            }

        if tokens < request_cost:
            deficit = request_cost - tokens
            retry_wait = deficit / refill_rate_per_sec if refill_rate_per_sec > 0 else 5.0
            return {
                "admitted": False,
                "degraded_mode": False,
                "recommended_ef_search": 0,
                "new_token_balance": round(tokens, 2),
                "retry_after_seconds": round(retry_wait, 2),
            }

        new_tokens = tokens - request_cost
        concurrency_ratio = current_concurrency / max(1, max_concurrency)

        degraded = concurrency_ratio > 0.8
        recommended_ef = 16 if degraded else 64

        return {
            "admitted": True,
            "degraded_mode": degraded,
            "recommended_ef_search": recommended_ef,
            "new_token_balance": round(new_tokens, 2),
            "retry_after_seconds": 0.0,
        }
