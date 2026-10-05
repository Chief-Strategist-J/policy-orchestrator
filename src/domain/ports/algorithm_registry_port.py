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
    def register_algorithm(self, contract: AlgorithmContract) -> None:
        """Register or update an algorithm contract in the catalog."""
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
    def register_adapter(self, adapter: TypeAdapterContract) -> None:
        """Register a G4 Type Adapter."""
        pass

    @abstractmethod
    def get_adapters_for_types(self, source_type: str, target_type: str) -> List[TypeAdapterContract]:
        """Find compatible type conversion adapters between source and target types."""
        pass

    @abstractmethod
    def list_adapters(self) -> List[TypeAdapterContract]:
        """List all registered type adapters."""
        pass
