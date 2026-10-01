"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: AI POLICY AGENT ORCHESTRATION SERVICE
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module implements the autonomous AI Policy Agent reasoning engine.
   It executes multi-step ReAct (Reason + Act) / Chain-of-Thought workflows
   grounded in policy rules (`policies/rules/`). It connects domain ports and
   internal services as callable tools without any vendor lock-in.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All state transitions, trajectory step schemas,
     tool dispatch handlers, and guardrail policies are documented in this header.
     Method bodies are 100% comment-free and pure.
   - Grounded Policy Guardrail: System prompts mandate strict adherence to
     anti-corruption patterns, hexagonal architecture, zero inline comments,
     and open standards (W3C traceparent, CloudEvents, OpenAPI v3).
   - Pluggable Hexagonal Design: Injects LLMProviderPort, RAGService, and AuditService
     as abstract domain dependencies.

3. REASONING & TOOL DISPATCH PIPELINE:
   [User Request] ──> [Initialize Trajectory]
           │
           ▼
   [Build Grounded Prompt + System Guardrails]
           │
     ┌─────┴──────────────────────────────────────────────────────┐
     │  Iteration Loop (Max Steps: N)                             │
     │  1. Invoke LLM with available tools                        │
     │  2. If Tool Call -> Dispatch Tool -> Capture Observation   │
     │  3. Append Step -> Feed back into Chat History             │
     │  4. If Final Text Answer -> Terminate Loop                 │
     └─────┬──────────────────────────────────────────────────────┘
           │
           ▼
   [Assemble & Return Immutable AgentExecutionResult]
================================================================================
"""

import json
import time
import uuid
from typing import List, Dict, Any, Optional

from src.domain.ports.llm_port import (
    LLMProviderPort,
    ChatMessage,
    ToolDefinition,
)
from src.features.rag.service import rag_service
from src.features.rag.service.rag_service import RAGService
from src.features.rag.types.rag_types import RAGQueryRequest
from src.features.audit.service.audit_service import AuditService
from src.features.agent.types.agent_types import (
    AgentExecutionRequest,
    AgentExecutionResult,
    AgentStep,
    ToolCallRecord,
)

SYSTEM_POLICY_PROMPT = """You are the Senior Enterprise Policy & Architecture AI Agent.
Your mission is to enforce architectural invariants, zero-inline comments, open standards, and safe automated refactoring across all services.

Rules you MUST enforce:
1. Hexagonal Architecture: Domain logic must depend only on abstract ports. Adapters implement ports. No vendor lock-in.
2. Zero Inline Comments: No comments allowed inside function bodies or control flows. All documentation belongs in top-side blueprint docblocks.
3. Open Standards: CloudEvents 1.0, W3C Trace Context (traceparent), OpenAPI v3 envelopes ({meta, data, errors}).
4. Determinism & Safety: Verify findings and use provided tools before proposing modifications.
"""

class AgentService:
    def __init__(
        self,
        llm_provider: LLMProviderPort,
        rag_service: RAGService,
        audit_service: AuditService,
    ) -> None:
        self.llm_provider = llm_provider
        self.rag_service = rag_service
        self.audit_service = audit_service
        self._tools = self._register_tools()

    def _register_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(
                name="search_policy_rules",
                description="Search grounded markdown policy contracts, architecture rules, and edge-case checklists.",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language query about rules, open standards, or invariants",
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional category (e.g. edgeCases, folderStructure, openStandards-scalling)",
                        },
                    },
                    "required": ["query"],
                },
            ),
            ToolDefinition(
                name="run_repo_audit",
                description="Scan repository files for invariant violations, dual writes, inline comments, or leak risks.",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "target_dir": {
                            "type": "string",
                            "description": "Directory path to audit",
                        },
                    },
                    "required": ["target_dir"],
                },
            ),
            ToolDefinition(
                name="generate_refactoring_plan",
                description="Formulate a step-by-step AST refactoring plan addressing identified policy violations.",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "issue_description": {
                            "type": "string",
                            "description": "Summary of the rule violation or refactoring goal",
                        },
                        "target_files": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of file paths requiring refactoring",
                        },
                    },
                    "required": ["issue_description", "target_files"],
                },
            ),
        ]

    def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        if name == "search_policy_rules":
            query = arguments.get("query", "")
            category = arguments.get("category")
            res = self.rag_service.retrieve_context(
                RAGQueryRequest(query=query, category_filter=category, top_k=3)
            )
            return {
                "total_found": res.total_found,
                "sources": [d.source_file for d in res.documents],
                "context": res.formatted_context_block,
            }

        elif name == "run_repo_audit":
            target_dir = arguments.get("target_dir", ".")
            findings = self.audit_service.audit_repository(target_dir)
            return {
                "total_violations": len(findings),
                "findings": [
                    {
                        "rule_id": f.rule_id,
                        "severity": f.severity,
                        "file": f.file,
                        "line": f.line,
                        "snippet": f.snippet,
                        "recommendation": f.recommendation,
                    }
                    for f in findings[:15]
                ],
            }

        elif name == "generate_refactoring_plan":
            issue = arguments.get("issue_description", "")
            files = arguments.get("target_files", [])
            return {
                "status": "PLAN_GENERATED",
                "issue": issue,
                "files": files,
                "steps": [
                    "1. Extract function-body inline comments into top-side blueprint.",
                    "2. Wrap payload responses in standard {meta, data, errors} envelope.",
                    "3. Validate ports and adapters dependency boundaries.",
                    "4. Execute dry-run invariant audit and pytest verification.",
                ],
            }

        return {"error": f"Unknown tool: {name}"}

    def execute_agent_loop(self, request: AgentExecutionRequest) -> AgentExecutionResult:
        start_time = time.perf_counter()
        session_id = request.session_id or f"sess_{uuid.uuid4().hex[:12]}"
        
        grounded_sources: List[str] = []
        steps: List[AgentStep] = []
        total_tokens = 0

        initial_rag = self.rag_service.retrieve_context(
            RAGQueryRequest(query=request.prompt, top_k=2)
        )
        for doc in initial_rag.documents:
            grounded_sources.append(doc.source_file)

        messages = [
            ChatMessage(role="system", content=SYSTEM_POLICY_PROMPT),
            ChatMessage(
                role="user",
                content=(
                    f"Task: {request.prompt}\n"
                    f"Target Directory: {request.target_directory}\n\n"
                    f"Grounded Policy Rules Context:\n{initial_rag.formatted_context_block}\n"
                ),
            ),
        ]

        final_response_text = ""
        status = "COMPLETED"

        for step_idx in range(1, request.max_steps + 1):
            gen_res = self.llm_provider.generate(
                messages=messages,
                temperature=request.temperature,
                tools=self._tools,
            )
            total_tokens += gen_res.prompt_tokens + gen_res.completion_tokens

            if gen_res.tool_calls:
                tool_records: List[ToolCallRecord] = []
                for tc in gen_res.tool_calls:
                    t_name = tc.get("function", {}).get("name", "")
                    raw_args = tc.get("function", {}).get("arguments", "{}")
                    try:
                        t_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    except Exception:
                        t_args = {}

                    t_start = time.perf_counter()
                    t_output = self._execute_tool(t_name, t_args)
                    t_duration = (time.perf_counter() - t_start) * 1000.0

                    tool_records.append(
                        ToolCallRecord(
                            tool_name=t_name,
                            arguments=t_args,
                            output=t_output,
                            duration_ms=round(t_duration, 2),
                            status="SUCCESS",
                        )
                    )

                    messages.append(
                        ChatMessage(
                            role="assistant",
                            content="",
                            tool_calls=[tc],
                        )
                    )
                    messages.append(
                        ChatMessage(
                            role="tool",
                            name=t_name,
                            tool_call_id=tc.get("id", f"call_{step_idx}"),
                            content=json.dumps(t_output),
                        )
                    )

                step_record = AgentStep(
                    step_number=step_idx,
                    thought=gen_res.content or f"Executing {len(tool_records)} tool(s).",
                    action="tool_calls",
                    observation=f"Completed execution of {[r.tool_name for r in tool_records]}",
                    tool_calls=tool_records,
                )
                steps.append(step_record)

            else:
                final_response_text = gen_res.content
                step_record = AgentStep(
                    step_number=step_idx,
                    thought="Final answer formulated based on policy analysis.",
                    action="finalize",
                    observation="Execution complete.",
                    tool_calls=[],
                )
                steps.append(step_record)
                break

        if not final_response_text and steps:
            final_response_text = "Analysis completed. Review reasoning steps and tool findings."

        total_duration = (time.perf_counter() - start_time) * 1000.0

        return AgentExecutionResult(
            session_id=session_id,
            status=status,
            final_response=final_response_text,
            steps=steps,
            total_steps=len(steps),
            total_tokens=total_tokens,
            grounded_sources=list(set(grounded_sources)),
            duration_ms=round(total_duration, 2),
        )
