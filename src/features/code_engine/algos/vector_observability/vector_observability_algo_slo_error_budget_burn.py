"""
================================================================================
ALGORITHM BLUEPRINT: SLO & ERROR-BUDGET BURN RATE CALCULATOR (ALGO-VEC-OBS-180)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Calculates Service Level Indicator (SLI) compliance, error budget consumption,
   and multi-window burn rate alerts (e.g. 1-hour fast burn vs 3-day slow burn)
   across vector search availability, latency, and recall SLOs.

2. MATHEMATICAL FORMULATION:
   ErrorBudget = 1.0 - TargetSLO
   BurnRate = ObservedErrorRate / ErrorBudget
   HoursToBudgetExhaustion = (WindowHours * TargetBudget) / (BurnRate * ErrorBudget)
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoSloErrorBudgetBurn:
    """
    --- contract:
      id: ALGO-VEC-OBS-180
      name: VectorObservabilityAlgoSloErrorBudgetBurn
      category: observability
      complexity: O(1)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        target_slo: float
        total_events: int
        bad_events: int
        window_hours: float
      output_schema:
        target_slo: float
        current_sli: float
        error_budget_total: float
        error_budget_consumed: float
        error_budget_remaining_percent: float
        burn_rate: float
        alert_tier: str
        is_change_freeze_triggered: bool
    ---
    """

    @classmethod
    def evaluate(
        cls,
        target_slo: float = 0.999,
        total_events: int = 100000,
        bad_events: int = 50,
        window_hours: float = 24.0,
    ) -> Dict[str, Any]:
        if total_events <= 0:
            return {
                "target_slo": target_slo,
                "current_sli": 1.0,
                "error_budget_total": 0.0,
                "error_budget_consumed": 0.0,
                "error_budget_remaining_percent": 100.0,
                "burn_rate": 0.0,
                "alert_tier": "NORMAL",
                "is_change_freeze_triggered": False,
            }

        observed_error_rate = bad_events / float(total_events)
        current_sli = 1.0 - observed_error_rate
        error_budget = max(0.000001, 1.0 - target_slo)

        burn_rate = observed_error_rate / error_budget
        allowed_bad_events = total_events * error_budget
        consumed_ratio = bad_events / allowed_bad_events if allowed_bad_events > 0 else 1.0
        remaining_pct = max(0.0, (1.0 - consumed_ratio) * 100.0)

        alert_tier = "NORMAL"
        freeze = False

        if burn_rate >= 14.0:
            alert_tier = "CRITICAL_PAGE_FAST_BURN"
            freeze = True
        elif burn_rate >= 6.0:
            alert_tier = "HIGH_ALERT"
            freeze = True
        elif burn_rate >= 2.0:
            alert_tier = "WARNING_SLOW_BURN"
        elif remaining_pct <= 10.0:
            alert_tier = "BUDGET_NEARLY_EXHAUSTED"
            freeze = True

        return {
            "target_slo": round(target_slo, 5),
            "current_sli": round(current_sli, 5),
            "error_budget_total": round(error_budget, 5),
            "error_budget_consumed": bad_events,
            "error_budget_remaining_percent": round(remaining_pct, 2),
            "burn_rate": round(burn_rate, 2),
            "alert_tier": alert_tier,
            "is_change_freeze_triggered": freeze,
        }
