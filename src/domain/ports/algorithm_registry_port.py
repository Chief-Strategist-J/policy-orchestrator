"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ALGORITHM REGISTRY PORT
================================================================================

1. OVERVIEW & OBJECTIVE:
   Domain port interface for persisting, discovering, and querying Layer 1
   Algorithm Contracts and G4 Type Adapters in the Capability Registry (G2).

2. ARCHITECTURAL PATTERN:
   - Hexagonal Architecture / Dependency Inversion Principle.
   - Query filters support tag containment, capability search, and operational properties.
================================================================================
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from src.domain.models.algorithm_contract import (
    AlgorithmContract,
    TypeAdapterContract,
    AlgorithmCategory,
    Purity,
    SideEffectScope,
)


class AlgorithmRegistryPort(ABC):
    @abstractmethod
    def register_algorithm(self, contract: AlgorithmContract) -> AlgorithmContract:
        """Register or update an algorithm contract in the catalog (Upsert semantics)."""
        pass

    @abstractmethod
    def upsert_algorithm(self, contract: AlgorithmContract) -> AlgorithmContract:
        """Explicit upsert: creates the algorithm contract if not present, otherwise updates it."""
        pass

    @abstractmethod
    def get_algorithm(self, algo_id: str) -> Optional[AlgorithmContract]:
        """Fetch an algorithm contract by its unique canonical ID."""
        pass

    @abstractmethod
    def list_algorithms(
        self,
        category: Optional[AlgorithmCategory] = None,
        tags: Optional[List[str]] = None,
        purity: Optional[Purity] = None,
        side_effects: Optional[SideEffectScope] = None,
        is_active: bool = True,
    ) -> List[AlgorithmContract]:
        """Query algorithm contracts matching structured and dynamic filter criteria."""
        pass

    @abstractmethod
    def update_algorithm(self, algo_id: str, updates: Dict[str, Any]) -> Optional[AlgorithmContract]:
        """Update specific fields of an existing algorithm contract."""
        pass

    @abstractmethod
    def delete_algorithm(self, algo_id: str, hard_delete: bool = False) -> bool:
        """Delete an algorithm contract (soft delete is_active=False by default, or hard delete)."""
        pass

    @abstractmethod
    def register_adapter(self, adapter: TypeAdapterContract) -> TypeAdapterContract:
        """Register or update a G4 Type Adapter (Upsert semantics)."""
        pass

    @abstractmethod
    def upsert_adapter(self, adapter: TypeAdapterContract) -> TypeAdapterContract:
        """Explicit upsert for a type adapter."""
        pass

    @abstractmethod
    def get_adapters_for_types(self, source_type: str, target_type: str) -> List[TypeAdapterContract]:
        """Find compatible type conversion adapters between source and target types."""
        pass

    @abstractmethod
    def list_adapters(self) -> List[TypeAdapterContract]:
        """List all registered type adapters."""
        pass

    @abstractmethod
    def delete_adapter(self, adapter_id: str) -> bool:
        """Delete a type adapter from the catalog."""
        pass

