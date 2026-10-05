"""
================================================================================
ALGORITHM BLUEPRINT: CARDINALITY-SAFE METRIC LABEL SANITIZER (ALGO-VEC-OBS-188)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Validates and sanitizes Prometheus/OTel metric dimension labels to prevent
   time-series cardinality explosions (strips UUIDs, query text, raw timestamps).

2. MATHEMATICAL FORMULATION:
   TotalSeriesCount = product_{label in Labels} |UniqueValues(label)|
   MaxSafeCardinalityLimit = 10,000 series per metric family
================================================================================
"""

import re
from typing import Any, Dict, List, Optional, Set


class VectorObservabilityAlgoCardinalitySafeLabels:
    """
    --- contract:
      id: ALGO-VEC-OBS-188
      name: VectorObservabilityAlgoCardinalitySafeLabels
      category: observability
      complexity: O(L)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        labels: dict[str, str]
        allowed_label_keys: Optional[list[str]]
        max_label_value_length: int
      output_schema:
        sanitized_labels: dict[str, str]
        dropped_keys: list[str]
        is_cardinality_safe: bool
        rejection_reasons: list[str]
    ---
    """

    @classmethod
    def sanitize(
        cls,
        labels: Dict[str, str],
        allowed_label_keys: Optional[List[str]] = None,
        max_label_value_length: int = 64,
    ) -> Dict[str, Any]:
        if not labels:
            return {
                "sanitized_labels": {},
                "dropped_keys": [],
                "is_cardinality_safe": True,
                "rejection_reasons": [],
            }

        allowed_keys_set = set(allowed_label_keys or ["environment", "tenant_tier", "index_name", "status_code", "stage", "model_version"])
        sanitized: Dict[str, str] = {}
        dropped: List[str] = []
        reasons: List[str] = []

        uuid_pattern = re.compile(r"^[0-9a-fA-F-]{36}$")
        numeric_id_pattern = re.compile(r"^\d{6,}$")

        for k, v in labels.items():
            str_val = str(v).strip()

            if k not in allowed_keys_set:
                dropped.append(k)
                reasons.append(f"Label key '{k}' is not in allowed bounded cardinality list")
                continue

            if uuid_pattern.match(str_val) or numeric_id_pattern.match(str_val):
                dropped.append(k)
                reasons.append(f"Label '{k}' contains unbounded high-cardinality ID: '{str_val}'")
                continue

            if len(str_val) > max_label_value_length:
                sanitized[k] = str_val[:max_label_value_length]
            else:
                sanitized[k] = str_val

        is_safe = len(dropped) == 0

        return {
            "sanitized_labels": sanitized,
            "dropped_keys": dropped,
            "is_cardinality_safe": is_safe,
            "rejection_reasons": reasons,
        }
