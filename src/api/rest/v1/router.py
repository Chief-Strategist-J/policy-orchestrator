"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 ROUTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides HTTP REST endpoints for the Policy Orchestrator:
   - GET  /api/v1/health: Readiness and liveness probing.
   - POST /api/v1/rag/search: Grounded semantic search over policy markdown rules.
   - POST /api/v1/rag/index: Trigger full re-indexing of policy knowledge base.
   - POST /api/v1/agent/run: Execute autonomous AI Agent policy reasoning workflow.
   - POST /api/v1/audit/scan: Execute deterministic invariant repository audit.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: Route declarations, dependency injections,
     and payload wrapping procedures are articulated in this header.
   - Standard Envelope: All routes return data encapsulated in `{meta, data, errors}`.
   - OpenTelemetry Trace Extraction: Extracts W3C `traceparent` or generates trace_id.
================================================================================
"""

import os
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException

from src.api.rest.envelope import build_success_envelope, build_error_envelope
from src.features.rag.schema.rag_schema import (
    RAGSearchRequestDTO,
    IndexingStatusDTO,
)
from src.features.rag.types.rag_types import RAGQueryRequest
from src.features.agent.schema.agent_schema import (
    AgentRunRequestDTO,
)
from src.features.agent.types.agent_types import AgentExecutionRequest
from src.features.audit.service.audit_service import AuditService
from src.features.rag.service.rag_service import RAGService
from src.features.agent.service.agent_service import AgentService
from src.infra.adapters.knowledge.policy_rules_loader import PolicyRulesMarkdownLoader
from src.infra.adapters.vector.in_memory_vector_adapter import InMemoryCosineVectorAdapter
from src.infra.adapters.llm.openai_compatible_adapter import OpenAICompatibleAdapter
from src.infra.adapters.llm.mock_llm_adapter import MockLLMAdapter

router = APIRouter(prefix="/api/v1")

def get_orchestrator_services() -> Dict[str, Any]:
    rules_dir = os.environ.get("POLICY_RULES_DIR", "../rules")
    llm_backend = os.environ.get("LLM_BACKEND", "mock")
    
    knowledge_source = PolicyRulesMarkdownLoader(base_rules_dir=rules_dir)
    vector_store = InMemoryCosineVectorAdapter()
    
    if llm_backend == "openai":
        llm_provider = OpenAICompatibleAdapter(
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            model_name=os.environ.get("OPENAI_MODEL", "gpt-4o"),
        )
    elif llm_backend == "ollama":
        llm_provider = OpenAICompatibleAdapter(
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            api_key="EMPTY",
            model_name=os.environ.get("OLLAMA_MODEL", "llama3.2"),
        )
    else:
        llm_provider = MockLLMAdapter()

    rag_svc = RAGService(
        knowledge_source=knowledge_source,
        vector_store=vector_store,
        llm_provider=llm_provider,
    )
    audit_svc = AuditService()
    agent_svc = AgentService(
        llm_provider=llm_provider,
        rag_service=rag_svc,
        audit_service=audit_svc,
    )

    return {
        "rag": rag_svc,
        "audit": audit_svc,
        "agent": agent_svc,
    }

_SERVICES = None

def get_services() -> Dict[str, Any]:
    global _SERVICES
    if _SERVICES is None:
        _SERVICES = get_orchestrator_services()
    return _SERVICES

@router.get("/health")
def health_check(request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id") or request.headers.get("traceparent")
    return build_success_envelope(
        data={"status": "healthy", "service": "policy-orchestrator", "version": "0.1.0"},
        trace_id=trace_id,
    )

@router.post("/rag/index")
def index_policies(request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    count = svcs["rag"].index_all_rules()
    return build_success_envelope(
        data={"indexed_documents": count, "status": "COMPLETED"},
        trace_id=trace_id,
    )

@router.post("/rag/search")
def search_policies(payload: RAGSearchRequestDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    rag_req = RAGQueryRequest(
        query=payload.query,
        top_k=payload.top_k,
        category_filter=payload.category_filter,
        min_relevance_score=payload.min_score,
    )
    res = svcs["rag"].retrieve_context(rag_req)
    
    docs_data = [
        {
            "id": d.id,
            "source_file": d.source_file,
            "section_title": d.section_title,
            "content": d.content,
            "category": d.category,
            "rrf_score": d.rrf_score,
            "metadata": d.metadata,
        }
        for d in res.documents
    ]
    return build_success_envelope(
        data={
            "query": res.query,
            "total_found": res.total_found,
            "documents": docs_data,
            "formatted_context_block": res.formatted_context_block,
            "latency_ms": res.latency_ms,
        },
        trace_id=trace_id,
    )

@router.post("/agent/run")
def run_agent(payload: AgentRunRequestDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    agent_req = AgentExecutionRequest(
        prompt=payload.prompt,
        target_directory=payload.target_directory,
        max_steps=payload.max_steps,
        temperature=payload.temperature,
        session_id=payload.session_id,
    )
    result = svcs["agent"].execute_agent_loop(agent_req)
    
    steps_data = [
        {
            "step_number": s.step_number,
            "thought": s.thought,
            "action": s.action,
            "observation": s.observation,
            "tool_calls": [
                {
                    "tool_name": tc.tool_name,
                    "arguments": tc.arguments,
                    "output": tc.output,
                    "duration_ms": tc.duration_ms,
                    "status": tc.status,
                }
                for tc in s.tool_calls
            ],
        }
        for s in result.steps
    ]
    return build_success_envelope(
        data={
            "session_id": result.session_id,
            "status": result.status,
            "final_response": result.final_response,
            "steps": steps_data,
            "total_steps": result.total_steps,
            "total_tokens": result.total_tokens,
            "grounded_sources": result.grounded_sources,
            "duration_ms": result.duration_ms,
        },
        trace_id=trace_id,
    )

@router.post("/audit/scan")
def scan_repository(request: Request, target_directory: str = ".") -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    findings = svcs["audit"].audit_repository(target_directory)
    findings_data = [
        {
            "rule_id": f.rule_id,
            "category": f.category,
            "severity": f.severity,
            "description": f.description,
            "file": f.file,
            "line": f.line,
            "snippet": f.snippet,
            "recommendation": f.recommendation,
        }
        for f in findings
    ]
    return build_success_envelope(
        data={"total_findings": len(findings), "findings": findings_data},
        trace_id=trace_id,
    )
