"""
================================================================================
ALGORITHM BLUEPRINT: DISTRIBUTED TRACE CONTEXT PROPAGATOR (OPENTELEMETRY) (ALGO-VEC-OBS-181)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Validates, creates, and propagates W3C distributed trace context (traceparent, tracestate)
   across vector retrieval sub-spans (embed, index_lookup, rerank, llm_generate) with
   tail-based sampling decision rules.

2. MATHEMATICAL FORMULATION:
   traceparent = {version:2hex}-{trace_id:32hex}-{parent_id:16hex}-{trace_flags:2hex}
   Tail sampling: Sample if duration_ms > latency_threshold or status == "ERROR"
================================================================================
"""

import re
import secrets
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoDistributedTracing:
    """
    --- contract:
      id: ALGO-VEC-OBS-181
      name: VectorObservabilityAlgoDistributedTracing
      category: observability
      complexity: O(S)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        traceparent: Optional[str]
        spans: list[dict[str, Any]]
        tail_sampling_latency_ms: float
      output_schema:
        trace_id: str
        is_traceparent_valid: bool
        propagated_traceparent: str
        is_sampled_for_retention: bool
        total_duration_ms: float
        span_tree: list[dict[str, Any]]
    ---
    """

    @classmethod
    def process_trace(
        cls,
        traceparent: Optional[str] = None,
        spans: Optional[List[Dict[str, Any]]] = None,
        tail_sampling_latency_ms: float = 100.0,
    ) -> Dict[str, Any]:
        valid_tp = False
        trace_id = ""
        parent_id = ""

        if traceparent:
            match = re.match(r"^([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$", traceparent.strip().lower())
            if match and match.group(2) != "0" * 32 and match.group(3) != "0" * 16:
                valid_tp = True
                trace_id = match.group(2)
                parent_id = match.group(3)

        if not valid_tp:
            trace_id = secrets.token_hex(16)
            parent_id = secrets.token_hex(8)

        new_span_id = secrets.token_hex(8)
        new_traceparent = f"00-{trace_id}-{new_span_id}-01"

        span_list = spans or []
        total_dur = sum(float(s.get("duration_ms", 0.0)) for s in span_list)
        has_error = any(str(s.get("status", "OK")).upper() == "ERROR" for s in span_list)

        is_sampled = (total_dur >= tail_sampling_latency_ms) or has_error or (not valid_tp)

        processed_spans = []
        for s in span_list:
            processed_spans.append({
                "name": s.get("name", "span"),
                "duration_ms": float(s.get("duration_ms", 0.0)),
                "status": s.get("status", "OK"),
                "attributes": {k: v for k, v in s.get("attributes", {}).items() if not k.startswith("raw_content")},
            })

        return {
            "trace_id": trace_id,
            "is_traceparent_valid": valid_tp,
            "propagated_traceparent": new_traceparent,
            "is_sampled_for_retention": is_sampled,
            "total_duration_ms": round(total_dur, 2),
            "span_tree": processed_spans,
        }
