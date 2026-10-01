"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DYNAMIC TOOL REGISTRY & CACHE PORT (HEXAGONAL)
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module defines the vendor-neutral Abstract Port for dynamic agent tool
   registration, AST searcher caching, and reusable scraper storage. It allows
   the Meta-Agent Orchestrator to generate specialized scraping/search tools once,
   persist them, and reuse them across multi-project workspaces without redundant
   tool recreation.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: Tool execution contracts, signature schemas,
     and persistence rules are captured in this top header block.
   - Dynamic Tool Ingestion: Persists tool name, docstring, parameter schema,
     and executable code block for deterministic reuse across agent runs.

3. METHOD CONTRACTS:
   - register_tool(): Persists a new or optimized tool definition and handler.
   - get_tool(): Fetches registered tool by unique name.
   - list_tools(): Lists all cached and reusable agent tools.
   - execute_tool(): Dynamically executes a registered tool with input validation.
================================================================================
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable

from src.domain.ports.llm_port import ToolDefinition

@dataclass(frozen=True)
class DynamicToolRecord:
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    category: str
    source_code: str
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class ToolRegistryPort(ABC):
    @abstractmethod
    def register_tool(self, tool_record: DynamicToolRecord) -> bool:
        pass

    @abstractmethod
    def get_tool(self, name: str) -> Optional[DynamicToolRecord]:
        pass

    @abstractmethod
    def list_tools(self, category: Optional[str] = None) -> List[DynamicToolRecord]:
        pass

    @abstractmethod
    def get_tool_definitions(self) -> List[ToolDefinition]:
        pass
