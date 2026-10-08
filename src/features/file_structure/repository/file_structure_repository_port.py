"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FILE STRUCTURE REPOSITORY PORT (HEXAGONAL)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Defines the abstract data access contract for persisting and querying file
   structure metadata, nodes, directed dependencies, and architectural mappings.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All method contracts and exceptions are
     documented in this header. Class declarations remain 100% comment-free.
================================================================================
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class FileStructureRepositoryPort(ABC):
    @abstractmethod
    def save_node(
        self,
        node_id: str,
        label: str,
        file_path: str,
        feature_name: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        pass

    @abstractmethod
    def get_node_by_id(self, node_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def save_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        pass

    @abstractmethod
    def list_upstream_dependencies(self, target_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_downstream_dependents(self, source_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def clear_all(self) -> None:
        pass

KnowledgeGraphRepositoryPort = FileStructureRepositoryPort
