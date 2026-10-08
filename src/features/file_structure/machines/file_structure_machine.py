"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FILE STRUCTURE STATE MACHINE AS DATA
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module declares the state lifecycle graph and transition invariants for
   File Structure Scaffolding, Validation, and Knowledge Graph indexing.
   States progress through deterministic guarded transitions:
   `IDLE -> SCAFFOLDING -> VALIDATING -> INDEXED -> STALE -> ERROR`.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: State DAG nodes, valid event triggers, and
     guard conditions are exhaustively captured in this blueprint.
================================================================================
"""

from typing import Dict, Set, Optional

FILE_STRUCTURE_STATE_TRANSITIONS: Dict[str, Set[str]] = {
    "IDLE": {"SCAFFOLDING", "VALIDATING", "SCANNING", "ERROR"},
    "SCAFFOLDING": {"VALIDATING", "INDEXED", "ERROR"},
    "VALIDATING": {"INDEXED", "ERROR"},
    "SCANNING": {"INDEXED", "ERROR"},
    "INDEXED": {"STALE", "SCAFFOLDING", "VALIDATING", "SCANNING", "ERROR"},
    "STALE": {"SCANNING", "SCAFFOLDING", "ERROR"},
    "ERROR": {"IDLE", "SCANNING", "SCAFFOLDING"},
}

class FileStructureLifecycleMachine:
    def __init__(self, initial_state: str = "IDLE") -> None:
        self.current_state = initial_state

    def can_transition_to(self, next_state: str) -> bool:
        valid_targets = FILE_STRUCTURE_STATE_TRANSITIONS.get(self.current_state, set())
        return next_state in valid_targets

    def transition_to(self, next_state: str, reason: Optional[str] = None) -> str:
        if not self.can_transition_to(next_state):
            raise ValueError(f"Illegal state transition from {self.current_state} to {next_state}")
        self.current_state = next_state
        return self.current_state

KnowledgeGraphLifecycleMachine = FileStructureLifecycleMachine
