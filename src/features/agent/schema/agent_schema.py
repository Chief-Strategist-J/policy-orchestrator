"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: AI AGENT API DTO SCHEMAS
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module defines Pydantic DTO models for AI Agent execution endpoints,
   chat interactions, and tool audit summaries.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: Validation constraints, response serialization,
     and model defaults are captured in this header.
   - OpenAPI Contract Alignment: Directly serializes into standard JSON envelopes.
================================================================================
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AgentRunRequestDTO(BaseModel):
    prompt: str = Field(..., description="Prompt or task for the AI Policy Agent")
    target_directory: str = Field(".", description="Repository target directory to analyze/refactor")
    max_steps: int = Field(8, ge=1, le=20, description="Maximum reasoning steps")
    temperature: float = Field(0.2, ge=0.0, le=1.0, description="Model generation temperature")
    session_id: Optional[str] = Field(None, description="Optional session tracking ID")

class ToolExecutionDTO(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    output: Any
    duration_ms: float
    status: str

class AgentStepDTO(BaseModel):
    step_number: int
    thought: str
    action: Optional[str] = None
    observation: Optional[str] = None
    tool_calls: List[ToolExecutionDTO] = Field(default_factory=list)

class AgentRunResponseDTO(BaseModel):
    session_id: str
    status: str
    final_response: str
    steps: List[AgentStepDTO]
    total_steps: int
    total_tokens: int
    grounded_sources: List[str]
    duration_ms: float
