"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: IMPACT ANALYSIS PORT (HEXAGONAL CONTRACT)
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module defines the abstract port contract for the Upstream and Downstream
   Impact Analysis Engine. It adheres strictly to Hexagonal Architecture, ensuring
   the domain port is completely decoupled from concrete storage adapters (Neo4j,
   Memgraph, In-Memory) and transport presentation layers.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All method signatures, invariants, and contract
     preconditions are documented strictly in this top-side blueprint header.
     Interface declarations remain 100% comment-free and pure.
   - Single Responsibility Principle (SRP): This unit defines only the impact
     analysis interface contract without implementation or persistence leakage.
   - Strict Type Discipline: No implicit type conversions, raw casting, or magic
     numbers. All inputs and outputs are strongly typed.

3. METHOD CONTRACTS:
   - analyze_upstream_impact(target_id, max_depth): Computes reverse dependencies and risk.
   - analyze_downstream_impact(target_id, max_depth): Computes forward downstream dependents.
   - register_architecture_node(node_id, label, file_path, properties): Adds node to graph.
   - register_dependency_edge(source_id, target_id, rel_type, properties): Adds edge.
================================================================================
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class ImpactedNodeModel:
    id: str
    label: str
    path: str
    depth: int
    relationship: str
    risk_factor: float

@dataclass(frozen=True)
class ImpactAnalysisReportModel:
    target_id: str
    target_label: str
    direction: str
    blast_radius_score: float
    risk_level: str
    impacted_nodes: List[ImpactedNodeModel]
    affected_layers: List[str]
    potential_breaking_risks: List[str]
    required_verification_commands: List[str]
    recommended_mitigation_recipe: str

class ImpactAnalysisPort(ABC):
    @abstractmethod
    def analyze_upstream_impact(
        self,
        target_id: str,
        max_depth: int = 5
    ) -> ImpactAnalysisReportModel:
        pass

    @abstractmethod
    def analyze_downstream_impact(
        self,
        target_id: str,
        max_depth: int = 5
    ) -> ImpactAnalysisReportModel:
        pass

    @abstractmethod
    def register_architecture_node(
        self,
        node_id: str,
        label: str,
        file_path: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        pass

    @abstractmethod
    def register_dependency_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        pass

    @abstractmethod
    def scan_and_index_repository(
        self,
        root_dir: str
    ) -> Dict[str, int]:
        pass

    @abstractmethod
    def scaffold_feature_structure(
        self,
        feature_name: str,
        base_dir: str = "src/features"
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def scaffold_package_structure(
        self,
        package_name: str,
        base_dir: str = "."
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_feature_map(
        self,
        feature_name: str
    ) -> Dict[str, Any]:
        pass
