"""
================================================================================
ALGORITHM BLUEPRINT: RETRIEVAL TRACE LOGGING & SAMPLING SANITIZER (ALGO-VEC-OBS-192)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Collects structured retrieval execution traces with deterministic hash-based sampling,
   PII redaction, and version binding (model_version, index_version, snapshot_seq).

2. MATHEMATICAL FORMULATION:
   SamplingHash = SHA256(query_id) % 10000
   SampleCondition = (SamplingHash < sample_rate * 10000) or is_error or is_slow
================================================================================
"""

import hashlib
import re
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoRetrievalTraceLogging:
    """
    --- contract:
      id: ALGO-VEC-OBS-192
      name: VectorObservabilityAlgoRetrievalTraceLogging
      category: observability
      complexity: O(N)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        trace_payload: dict[str, Any]
        sample_rate: float
        max_duration_threshold_ms: float
      output_schema:
        is_sampled: bool
        sanitized_log_entry: Optional[dict[str, Any]]
        redaction_applied: bool
    ---
    """

    @classmethod
    def process_and_sample(
        cls,
        trace_payload: Dict[str, Any],
        sample_rate: float = 0.05,
        max_duration_threshold_ms: float = 200.0,
    ) -> Dict[str, Any]:
        if not trace_payload:
            return {
                "is_sampled": False,
                "sanitized_log_entry": None,
                "redaction_applied": False,
            }

        q_id = str(trace_payload.get("query_id", "q-default"))
        duration = float(trace_payload.get("duration_ms", 0.0))
        is_error = bool(trace_payload.get("is_error", False))

        h_val = int(hashlib.sha256(q_id.encode("utf-8")).hexdigest()[:8], 16) % 10000
        is_sampled = (h_val < int(sample_rate * 10000)) or is_error or (duration >= max_duration_threshold_ms)

        if not is_sampled:
            return {
                "is_sampled": False,
                "sanitized_log_entry": None,
                "redaction_applied": False,
            }

        raw_query = str(trace_payload.get("query_text", ""))
        redacted_query = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL_REDACTED]", raw_query)
        redacted_query = re.sub(r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b", "[SSN_REDACTED]", redacted_query)
        redacted_query = re.sub(r"\b(?:\d[ -]*?){13,16}\b", "[CARD_REDACTED]", redacted_query)
        was_redacted = redacted_query != raw_query

        sanitized_entry = {
            "query_id": q_id,
            "query_text_sanitized": redacted_query,
            "query_hash": hashlib.sha256(raw_query.encode("utf-8")).hexdigest(),
            "model_version": trace_payload.get("model_version", "1.0.0"),
            "index_version": trace_payload.get("index_version", "v1"),
            "snapshot_seq": int(trace_payload.get("snapshot_seq", 0)),
            "retrieved_result_ids": trace_payload.get("retrieved_result_ids", [])[:50],
            "duration_ms": duration,
            "is_error": is_error,
        }

        return {
            "is_sampled": True,
            "sanitized_log_entry": sanitized_entry,
            "redaction_applied": was_redacted,
        }
