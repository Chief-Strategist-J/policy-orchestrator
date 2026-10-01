"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MOCK / OFFLINE LLM ADAPTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides a deterministic, zero-cost, fully offline implementation
   of LLMProviderPort. It produces syntactically valid structured policy audit
   summaries, refactoring plans, and deterministic embeddings for CI testing.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All mock generation algorithms, deterministic
     hashing embeddings, and rule simulation branches are documented here.
   - Deterministic Seed Embeddings: Maps words to reproducible normalized vector
     representations without downloading heavy weights.

3. METHOD CONTRACTS:
   - generate(): Returns deterministic policy assessment or simulated tool call.
   - generate_stream(): Streams tokens using a generator.
   - get_embeddings(): Returns deterministic 64-dimensional pseudo-embeddings.
================================================================================
"""

import hashlib
import math
from typing import List, Dict, Any, Optional, Generator

from src.domain.ports.llm_port import (
    LLMProviderPort,
    ChatMessage,
    ToolDefinition,
    LLMGenerationResponse,
)

class MockLLMAdapter(LLMProviderPort):
    def __init__(self, dimension: int = 64) -> None:
        self.dimension = dimension

    def generate(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.2,
        max_tokens: int = 2048,
        tools: Optional[List[ToolDefinition]] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> LLMGenerationResponse:
        last_msg = messages[-1].content if messages else ""
        
        if tools and "audit" in last_msg.lower():
            return LLMGenerationResponse(
                content="Triggering automated repository invariant audit.",
                tool_calls=[
                    {
                        "id": "call_audit_001",
                        "type": "function",
                        "function": {
                            "name": "run_repo_audit",
                            "arguments": '{"target_dir": "policies/policy-orchestrator"}',
                        },
                    }
                ],
                finish_reason="tool_calls",
                prompt_tokens=50,
                completion_tokens=25,
                model_name="mock-policy-agent",
            )

        response_content = (
            f"[Policy Agent Offline Response]\n"
            f"Analyzed {len(messages)} message(s). Policy invariants and open standards enforced.\n"
            f"Grounding query: {last_msg[:120]}"
        )
        return LLMGenerationResponse(
            content=response_content,
            finish_reason="stop",
            prompt_tokens=40,
            completion_tokens=30,
            model_name="mock-policy-agent",
        )

    def generate_stream(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.2,
        max_tokens: int = 2048,
        tools: Optional[List[ToolDefinition]] = None,
    ) -> Generator[str, None, None]:
        tokens = ["Policy", " verification", " completed.", " Status:", " PASS."]
        for token in tokens:
            yield token

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        results = []
        for text in texts:
            vec = [0.0] * self.dimension
            tokens = text.lower().split()
            for token in tokens:
                h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
                slot = h % self.dimension
                sign = 1.0 if ((h >> 8) & 1) else -1.0
                vec[slot] += sign
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            results.append([x / norm for x in vec])
        return results
