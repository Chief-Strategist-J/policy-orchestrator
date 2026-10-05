"""
================================================================================
ALGORITHM BLUEPRINT: FAITHFULNESS & GROUNDEDNESS RAG EVALUATOR (ALGO-VEC-OBS-167)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Deconstructs generated answers into atomic claims and verifies textual entailment
   against retrieved context passages to detect hallucinations and measure groundedness.

2. MATHEMATICAL FORMULATION:
   FaithfulnessScore = |Supported Claims| / |Total Claims|
   HallucinationRate = 1.0 - FaithfulnessScore
================================================================================
"""

import re
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoFaithfulnessGroundedness:
    """
    --- contract:
      id: ALGO-VEC-OBS-167
      name: VectorObservabilityAlgoFaithfulnessGroundedness
      category: observability
      complexity: O(C * P)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        answer_text: str
        retrieved_passages: list[str]
        claims: Optional[list[str]]
      output_schema:
        faithfulness_score: float
        hallucination_rate: float
        total_claims: int
        supported_claims: list[str]
        unsupported_claims: list[str]
        is_grounded: bool
    ---
    """

    @classmethod
    def evaluate(
        cls,
        answer_text: str,
        retrieved_passages: List[str],
        claims: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if not answer_text.strip():
            return {
                "faithfulness_score": 1.0,
                "hallucination_rate": 0.0,
                "total_claims": 0,
                "supported_claims": [],
                "unsupported_claims": [],
                "is_grounded": True,
            }

        extracted_claims: List[str] = []
        if claims is not None and len(claims) > 0:
            extracted_claims = [c.strip() for c in claims if c.strip()]
        else:
            raw_sentences = re.split(r"(?<=[.!?])\s+", answer_text)
            extracted_claims = [s.strip() for s in raw_sentences if len(s.strip()) > 5]

        if not extracted_claims:
            return {
                "faithfulness_score": 1.0,
                "hallucination_rate": 0.0,
                "total_claims": 0,
                "supported_claims": [],
                "unsupported_claims": [],
                "is_grounded": True,
            }

        combined_context = " ".join(retrieved_passages).lower()
        supported: List[str] = []
        unsupported: List[str] = []

        for claim in extracted_claims:
            words = [w.lower() for w in re.findall(r"\w+", claim) if len(w) > 3]
            if not words:
                supported.append(claim)
                continue

            matched_words = sum(1 for w in words if w in combined_context)
            match_ratio = matched_words / float(len(words))

            if match_ratio >= 0.60 or claim.lower() in combined_context:
                supported.append(claim)
            else:
                unsupported.append(claim)

        faithfulness = len(supported) / float(len(extracted_claims))
        hallucination = 1.0 - faithfulness
        is_grounded = faithfulness >= 0.85 and len(unsupported) == 0

        return {
            "faithfulness_score": round(faithfulness, 4),
            "hallucination_rate": round(hallucination, 4),
            "total_claims": len(extracted_claims),
            "supported_claims": supported,
            "unsupported_claims": unsupported,
            "is_grounded": is_grounded,
        }
