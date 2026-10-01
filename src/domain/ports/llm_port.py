"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: LLM PROVIDER PORT (HEXAGONAL ARCHITECTURE)
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module defines the vendor-neutral Abstract Port for Large Language Model
   (LLM) inference, structured text completions, function/tool calling, and
   vector embeddings. It guarantees 100% decoupling from specific LLM providers
   (OpenAI, Anthropic, vLLM, Ollama, DeepSeek, HuggingFace), preventing vendor
   lock-in as required by open.standard.md and api-structure.md.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All protocol specifications, message formats,
     and failure handling rules are documented in this top-side header.
     Interface declarations remain 100% comment-free and pure.
   - Ports & Adapters Isolation: Domain business logic depends solely on this
     abstract contract. Concrete HTTP SDKs live strictly in infra adapters.
   - Open Standard Schema Compatibility: Input/output message formats map
     directly to standard Chat Completion schemas.

3. METHOD CONTRACTS:
   - generate(): Computes non-streaming chat completion with optional tool calls.
   - generate_stream(): Streams tokens incrementally for real-time UI/agent loops.
   - get_embeddings(): Computes dense numerical vector embeddings for text chunks.
================================================================================
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Generator

@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None

@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters_schema: Dict[str, Any]

@dataclass(frozen=True)
class LLMGenerationResponse:
    content: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    finish_reason: str = "stop"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    model_name: str = "default"

class LLMProviderPort(ABC):
    @abstractmethod
    def generate(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.2,
        max_tokens: int = 2048,
        tools: Optional[List[ToolDefinition]] = None,
        stop_sequences: Optional[List[str]] = None
    ) -> LLMGenerationResponse:
        pass

    @abstractmethod
    def generate_stream(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.2,
        max_tokens: int = 2048,
        tools: Optional[List[ToolDefinition]] = None
    ) -> Generator[str, None, None]:
        pass

    @abstractmethod
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        pass
