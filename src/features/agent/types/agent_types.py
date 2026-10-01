"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: AI AGENT DOMAIN TYPES
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module defines immutable dataclasses for the AI Policy Agent runtime,
   including execution trajectories, reasoning steps (Thoughts, Actions,
   Observations), tool execution records, and final policy decisions.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All state transitions, trajectory step schemas,
     and tool binding types are articulated in this header.
   - ReAct / CoT Execution Tracking: Captures chain-of-thought, tool invocation,
     tool response, and synthesized final answer.
================================================================================
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class ToolCallRecord:
    tool_name: str
    arguments: Dict[str, Any]
    output: Any
    duration_ms: float
    status: str

@dataclass(frozen=True)
class AgentStep:
    step_number: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    tool_calls: List[ToolCallRecord] = field(default_factory=list)

@dataclass(frozen=True)
class AgentExecutionRequest:
    prompt: str
    target_directory: str = "."
    max_steps: int = 10
    temperature: float = 0.2
    session_id: Optional[str] = None
    extra_context: Optional[str] = None

@dataclass(frozen=True)
class AgentExecutionResult:
    session_id: str
    status: str
    final_response: str
    steps: List[AgentStep]
    total_steps: int
    total_tokens: int
    grounded_sources: List[str]
    duration_ms: float
