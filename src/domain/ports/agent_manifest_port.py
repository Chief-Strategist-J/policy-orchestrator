"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DECLARATIVE AGENT MANIFEST PORT (HEXAGONAL)
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module defines the vendor-neutral Abstract Port and data models for
   Declarative Specialized Policy Agents. It enables registering, managing, and
   instantiating 1000+ distinct agents (Scout, Planner, Editor, Verifier, Reporter,
   and 22+ Algorithm Agents) from declarative data specifications without rewriting
   code for every new agent.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All agent schema attributes, capability flags,
     and dispatch lifecycle steps are articulated in this header.
     Interface declarations remain 100% comment-free and pure.
   - Declarative Agent Architecture: Each agent is a frozen data manifest declaring:
     agent_id, title, role, system_prompt, allowed_tools, category, algorithms_used.
   - Scalable to 1000+ Agents: Supports in-memory, YAML, and dynamic database
     manifest catalogs.

3. METHOD CONTRACTS:
   - register_manifest(): Registers or updates a declarative agent definition.
   - get_manifest(): Retrieves an agent by its unique agent_id.
   - list_manifests(): Lists all registered manifests filtered by role or category.
================================================================================
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

class AgentRole(str, Enum):
    SCOUT = "SCOUT"
    PLANNER = "PLANNER"
    EDITOR = "EDITOR"
    VERIFIER = "VERIFIER"
    REPORTER = "REPORTER"
    COORDINATOR = "COORDINATOR"

@dataclass(frozen=True)
class AgentManifest:
    agent_id: str
    name: str
    role: AgentRole
    category: str
    description: str
    system_prompt: str
    allowed_tools: List[str] = field(default_factory=list)
    algorithms: List[int] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

class AgentManifestRegistryPort(ABC):
    @abstractmethod
    def register_manifest(self, manifest: AgentManifest) -> bool:
        pass

    @abstractmethod
    def get_manifest(self, agent_id: str) -> Optional[AgentManifest]:
        pass

    @abstractmethod
    def list_manifests(
        self,
        category: Optional[str] = None,
        role: Optional[AgentRole] = None
    ) -> List[AgentManifest]:
        pass

    @abstractmethod
    def count(self) -> int:
        pass
