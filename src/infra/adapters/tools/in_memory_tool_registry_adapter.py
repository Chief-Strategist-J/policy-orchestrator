"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: IN-MEMORY TOOL REGISTRY ADAPTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module implements ToolRegistryPort to manage, persist, and expose
   reusable tools (AST searchers, web scrapers, repository inspectors) created
   by the agent. Once generated, tools are cataloged with schemas and descriptions
   so they can be dynamically discovered and executed across runs.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: Tool storage indexing, execution isolation,
     and tool definition conversions are articulated in this blueprint.
     Class methods and functions are 100% comment-free and pure.
================================================================================
"""

from typing import List, Dict, Any, Optional

from src.domain.ports.llm_port import ToolDefinition
from src.domain.ports.tool_registry_port import (
    ToolRegistryPort,
    DynamicToolRecord,
)

class InMemoryToolRegistryAdapter(ToolRegistryPort):
    def __init__(self) -> None:
        self._tools: Dict[str, DynamicToolRecord] = {}

    def register_tool(self, tool_record: DynamicToolRecord) -> bool:
        self._tools[tool_record.name] = tool_record
        return True

    def get_tool(self, name: str) -> Optional[DynamicToolRecord]:
        return self._tools.get(name)

    def list_tools(self, category: Optional[str] = None) -> List[DynamicToolRecord]:
        if not category:
            return list(self._tools.values())
        return [t for t in self._tools.values() if t.category == category]

    def get_tool_definitions(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(
                name=t.name,
                description=t.description,
                parameters_schema=t.parameters_schema,
            )
            for t in self._tools.values()
        ]
