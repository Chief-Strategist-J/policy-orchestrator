"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FILE STRUCTURE DOMAIN TYPES & CONSTANTS
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module defines domain models, taxonomy types, risk level constants, and
   weight vectors for the File Structure, Scaffolding, and Knowledge Graph subsystems.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Single Responsibility Principle (SRP): Contains only data structures,
     enums, and constants. Zero business logic, zero IO, and zero framework imports.
   - Zero Magic Numbers: All calculation weights, risk thresholds, and default
     depths are centralized as named immutable constants.
   - Zero-Inline-Comment Doctrine: Header contains complete domain taxonomy.
================================================================================
"""

from typing import Final, Set

DEFAULT_MAX_TRAVERSAL_DEPTH: Final[int] = 6

WEIGHT_CONTRACT_NODE: Final[float] = 3.0
WEIGHT_HANDLER_NODE: Final[float] = 2.0
WEIGHT_DB_MIGRATION_NODE: Final[float] = 2.0
WEIGHT_SERVICE_NODE: Final[float] = 1.5
WEIGHT_PORT_NODE: Final[float] = 1.5
WEIGHT_DEFAULT_NODE: Final[float] = 1.0

RISK_SCORE_THRESHOLD_HIGH: Final[float] = 4.0
RISK_SCORE_THRESHOLD_MEDIUM: Final[float] = 2.0

RISK_LEVEL_LEVEL_0: Final[str] = "Level 0: Isolated Business Logic Scope"
RISK_LEVEL_LEVEL_1: Final[str] = "Level 1: Local Feature Scope"
RISK_LEVEL_LEVEL_2: Final[str] = "Level 2: Storage & Persistence Migration Risk"
RISK_LEVEL_LEVEL_3: Final[str] = "Level 3: Public Contract Boundary Risk"

CRITICAL_STORAGE_LABELS: Final[Set[str]] = {"DatabaseMigration", "NamedQuery"}
HIGH_RISK_INGRESS_LABELS: Final[Set[str]] = {"Contract", "IngressHandler", "IngressRouter"}
ISOLATED_LOGIC_LABELS: Final[Set[str]] = {"RuleSet", "StateMachine", "WorkflowEngine"}
LOCAL_FEATURE_LABELS: Final[Set[str]] = {"SchemaACL", "RepositoryPort", "DomainModel", "RepositoryAdapter"}
