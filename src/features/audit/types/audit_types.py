"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: AUDIT DOMAIN TYPES & DATA MODELS
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module defines the immutable, strongly-typed domain representations,
   enums, and value objects representing static analysis rules, security checks,
   severity tiers, and detected invariant findings across repositories.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All algorithmic requirements, data invariants,
     and model constraints are declared exclusively in this top-side blueprint.
     Class and field declarations remain 100% comment-free and pure.
   - Frozen Value Objects: All data models use frozen dataclasses to guarantee
     thread-safe, side-effect-free data propagation.
   - Strict Enums: Severity tiers and rule categories are constrained to rigid enums.

3. DATA INVARIANTS:
   - Line numbers must be positive integers (line >= 1).
   - Rule identifiers conform to alphanumeric uppercase namespaces (e.g. `SEC-001`).
================================================================================
"""

from dataclasses import dataclass
from enum import Enum
from typing import Set, Pattern

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class RuleCategory(str, Enum):
    CONCURRENCY = "Concurrency"
    SECURITY = "Security"
    DATABASE = "Database"
    PLATFORM = "Platform"
    OBSERVABILITY = "Observability"
    ARCHITECTURE = "Architecture"

@dataclass(frozen=True)
class AuditRule:
    rule_id: str
    category: RuleCategory
    severity: Severity
    description: str
    pattern: Pattern
    extensions: Set[str]
    recommendation: str

@dataclass(frozen=True)
class AuditFinding:
    rule_id: str
    category: str
    severity: str
    description: str
    file: str
    line: int
    snippet: str
    recommendation: str
