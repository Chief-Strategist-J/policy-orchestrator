"""
================================================================================
ALGORITHM BLUEPRINT: EXACTLY-ONCE INGESTION VIA IDEMPOTENCY KEYS (ALGO-VEC-UPD-129)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Validates version sequences and deduplication tokens on incoming vector writes
   to guarantee exactly-once application despite at-least-once message delivery.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorUpdateAlgoIdempotencyKeys:
    """
    --- contract:
      id: ALGO-VEC-UPD-129
      name: VectorUpdateAlgoIdempotencyKeys
      category: update
      complexity: O(1)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        record_id: str
        incoming_version: int
        idempotency_token: str
        stored_version: Optional[int]
        seen_tokens: list[str]
      output_schema:
        accept_write: bool
        rejection_reason: Optional[str]
        updated_version: int
        updated_tokens: list[str]
    ---
    """

    @classmethod
    def evaluate(
        cls,
        record_id: str,
        incoming_version: int,
        idempotency_token: str,
        stored_version: Optional[int] = None,
        seen_tokens: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        tokens = set(seen_tokens or [])

        if idempotency_token in tokens:
            return {
                "accept_write": False,
                "rejection_reason": "DUPLICATE_TOKEN_SEEN",
                "updated_version": stored_version or 0,
                "updated_tokens": sorted(list(tokens)),
            }

        if stored_version is not None and incoming_version <= stored_version:
            return {
                "accept_write": False,
                "rejection_reason": "STALE_VERSION_NUMBER",
                "updated_version": stored_version,
                "updated_tokens": sorted(list(tokens)),
            }

        tokens.add(idempotency_token)
        return {
            "accept_write": True,
            "rejection_reason": None,
            "updated_version": incoming_version,
            "updated_tokens": sorted(list(tokens)),
        }
