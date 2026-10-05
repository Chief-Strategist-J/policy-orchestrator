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
   - GET  /api/v1/agents: List all 1000+ declarative specialized agent manifests.
   - POST /api/v1/agents/{agent_id}/run: Execute a specific declarative specialized agent.
   - POST /api/v1/audit/scan: Execute deterministic invariant repository audit.
   - POST /api/v1/graph/build: Extract & build semantic policy knowledge graph.
   - POST /api/v1/graph/query: Execute declarative Cypher/pattern queries.
   - GET  /api/v1/graph/impact/{rule_id}: Query topological rule dependencies.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: Route declarations, dependency injections,
     and payload wrapping procedures are articulated in this header.
   - Standard Envelope: All routes return data encapsulated in `{meta, data, errors}`.
   - Open Standards & Pluggable Adapters: Configurable backends for LLM (OpenAI,
     Ollama, Mock), Vector (Qdrant, In-Memory), Graph (Neo4j, In-Memory), and Search.
================================================================================
"""

import os
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
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
from src.domain.ports.agent_manifest_port import AgentRole
from src.features.audit.service.audit_service import AuditService
from src.features.rag.service.rag_service import RAGService
from src.features.agent.service.agent_service import AgentService
from src.features.knowledge_graph.service.knowledge_graph_service import KnowledgeGraphService
from src.infra.adapters.knowledge.policy_rules_loader import PolicyRulesMarkdownLoader
from src.infra.adapters.vector.in_memory_vector_adapter import InMemoryCosineVectorAdapter
from src.infra.adapters.vector.qdrant_vector_adapter import QdrantVectorAdapter
from src.infra.adapters.graph.in_memory_graph_adapter import InMemoryGraphAdapter
from src.infra.adapters.graph.neo4j_adapter import Neo4jGraphAdapter
from src.infra.adapters.search.duckduckgo_search_adapter import DuckDuckGoSearchAdapter
from src.infra.adapters.search.mock_search_adapter import MockWebSearchAdapter
from src.infra.adapters.tools.in_memory_tool_registry_adapter import InMemoryToolRegistryAdapter
from src.infra.adapters.agent.in_memory_agent_registry_adapter import InMemoryAgentManifestRegistryAdapter
from src.infra.adapters.llm.openai_compatible_adapter import OpenAICompatibleAdapter
from src.infra.adapters.llm.mock_llm_adapter import MockLLMAdapter
from src.domain.models.algorithm_contract import (
    AlgorithmCategory,
    Purity,
    SideEffectScope,
    AlgorithmContract,
    TypeAdapterContract,
)
from src.infra.adapters.database import (
    InMemoryAlgorithmRegistryAdapter,
    SQLiteAlgorithmRegistryAdapter,
    AlloyDBAlgorithmRegistryAdapter,
    PostgresAlgorithmRegistryAdapter,
    DatabaseMigrationRunner,
)
from src.features.code_engine.service.algorithm_composer_service import AlgorithmComposerService

router = APIRouter(prefix="/api/v1")



class GraphQueryDTO(BaseModel):
    query: str = Field(..., description="Cypher or pattern matching query")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Query parameters")

def get_orchestrator_services() -> Dict[str, Any]:
    rules_dir = os.environ.get("POLICY_RULES_DIR", "../rules")
    llm_backend = os.environ.get("LLM_BACKEND", "mock")
    vector_backend = os.environ.get("VECTOR_BACKEND", "inmemory")
    graph_backend = os.environ.get("GRAPH_BACKEND", "inmemory")
    search_backend = os.environ.get("SEARCH_BACKEND", "mock")
    
    knowledge_source = PolicyRulesMarkdownLoader(base_rules_dir=rules_dir)
    
    if vector_backend == "qdrant":
        vector_store = QdrantVectorAdapter(
            url=os.environ.get("QDRANT_URL", "http://localhost:6333"),
            collection_name=os.environ.get("QDRANT_COLLECTION", "policy_rules"),
            vector_size=int(os.environ.get("VECTOR_SIZE", "64")),
        )
    else:
        vector_store = InMemoryCosineVectorAdapter()
    
    if graph_backend == "neo4j":
        graph_store = Neo4jGraphAdapter(
            uri=os.environ.get("NEO4J_URI", "http://localhost:7474"),
            user=os.environ.get("NEO4J_USER", "neo4j"),
            password=os.environ.get("NEO4J_PASSWORD", "password"),
        )
    else:
        graph_store = InMemoryGraphAdapter()

    if search_backend == "duckduckgo":
        search_provider = DuckDuckGoSearchAdapter()
    else:
        search_provider = MockWebSearchAdapter()

    tool_registry = InMemoryToolRegistryAdapter()
    agent_registry = InMemoryAgentManifestRegistryAdapter(load_builtins=True)

    db_url = os.environ.get("DATABASE_URL")
    auto_migrate = os.environ.get("AUTO_MIGRATE", "true").lower() == "true"

    if db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://")):
        if auto_migrate:
            try:
                migration_runner = DatabaseMigrationRunner(db_url)
                migration_runner.run_migrations()
                migration_runner.seed_algorithm_catalog()
            except Exception:
                pass
        algo_registry = AlloyDBAlgorithmRegistryAdapter(db_url)
    elif db_url and db_url.startswith("sqlite://"):
        if auto_migrate:
            try:
                migration_runner = DatabaseMigrationRunner(db_url)
                migration_runner.run_migrations()
                migration_runner.seed_algorithm_catalog()
            except Exception:
                pass
        db_path = db_url.replace("sqlite:///", "")
        algo_registry = SQLiteAlgorithmRegistryAdapter(db_path)
    else:
        algo_registry = SQLiteAlgorithmRegistryAdapter(":memory:")
        if auto_migrate:
            try:
                migration_runner = DatabaseMigrationRunner("sqlite:///:memory:")
                migration_runner.run_migrations(conn=algo_registry._memory_conn)
                migration_runner.seed_algorithm_catalog(conn=algo_registry._memory_conn)
            except Exception:
                pass

    composer_svc = AlgorithmComposerService(algo_registry)


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
        search_provider=search_provider,
        tool_registry=tool_registry,
    )
    graph_svc = KnowledgeGraphService(
        graph_store=graph_store,
        knowledge_source=knowledge_source,
    )

    return {
        "rag": rag_svc,
        "audit": audit_svc,
        "agent": agent_svc,
        "graph": graph_svc,
        "agent_registry": agent_registry,
        "tool_registry": tool_registry,
        "algo_registry": algo_registry,
        "composer": composer_svc,
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

@router.get("/agents")
def list_declarative_agents(request: Request, category: Optional[str] = None) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    manifests = svcs["agent_registry"].list_manifests(category=category)
    return build_success_envelope(
        data={
            "total_agents": len(manifests),
            "agents": [
                {
                    "agent_id": m.agent_id,
                    "name": m.name,
                    "role": m.role.value,
                    "category": m.category,
                    "description": m.description,
                    "algorithms": m.algorithms,
                    "allowed_tools": m.allowed_tools,
                    "tags": m.tags,
                }
                for m in manifests
            ],
        },
        trace_id=trace_id,
    )

@router.post("/agents/{agent_id}/run")
def run_specialized_agent(agent_id: str, payload: AgentRunRequestDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    manifest = svcs["agent_registry"].get_manifest(agent_id)
    if not manifest:
        raise HTTPException(status_code=404, detail=f"Specialized Agent '{agent_id}' not found.")

    agent_req = AgentExecutionRequest(
        prompt=payload.prompt,
        target_directory=payload.target_directory,
        max_steps=payload.max_steps,
        temperature=payload.temperature,
        session_id=payload.session_id,
    )
    result = svcs["agent"].execute_agent_loop(agent_req, manifest=manifest)
    
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
            "agent_id": agent_id,
            "agent_name": manifest.name,
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

from src.features.code_engine.service.code_engine_service import CodeEngineService

class AlgoScanDTO(BaseModel):
    root_dir: str = Field(default=".", description="Root directory to scan")
    patterns: List[str] = Field(..., description="Patterns to search for")
    max_files: int = Field(default=1000, description="Max files to scan")

class FilePathDTO(BaseModel):
    file_path: str = Field(..., description="File path to analyze")

class DirectoryPathDTO(BaseModel):
    directory: str = Field(default=".", description="Directory path to analyze")

_code_engine_service: Optional[CodeEngineService] = None

def get_code_engine_service() -> CodeEngineService:
    global _code_engine_service
    if _code_engine_service is None:
        _code_engine_service = CodeEngineService()
    return _code_engine_service

class PatchOperationDTO(BaseModel):
    file_path: str = Field(..., description="File to patch")
    find_pattern: str = Field(..., description="Target pattern")
    replace_text: str = Field(..., description="Replacement text")
    expected_sha256: Optional[str] = Field(default=None, description="Precondition SHA-256")
    is_regex: bool = Field(default=False, description="Is regex pattern")

class BatchPatchRequestDTO(BaseModel):
    operations: List[PatchOperationDTO] = Field(..., description="List of patch operations")
    dry_run: bool = Field(default=False, description="Simulate patch without disk write")

class DiffRequestDTO(BaseModel):
    original_content: str = Field(..., description="Original text")
    modified_content: str = Field(..., description="Modified text")
    file_path: str = Field(default="file", description="File path identifier")

@router.post("/algos/search/scan")
@router.post("/algos/scan")
def scan_multipattern(payload: AlgoScanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    results = svc.scan_directory_multipattern(
        root_dir=payload.root_dir,
        patterns=payload.patterns,
        max_files=payload.max_files,
    )
    return build_success_envelope(
        data={"total_files_matched": len(results), "results": results},
        trace_id=trace_id,
    )

@router.post("/algos/observability/outline")
@router.post("/algos/outline")
def generate_file_outline(payload: FilePathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    if not os.path.isfile(payload.file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {payload.file_path}")
    outline = svc.inspect_file_outline(payload.file_path)
    return build_success_envelope(data=outline, trace_id=trace_id)

@router.post("/algos/observability/dependencies")
@router.post("/algos/dependencies")
def analyze_dependencies(payload: DirectoryPathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    report = svc.analyze_module_dependencies(payload.directory)
    return build_success_envelope(data=report, trace_id=trace_id)

@router.post("/algos/observability/lint-comments")
@router.post("/algos/lint-comments")
def lint_comments(payload: FilePathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    if not os.path.isfile(payload.file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {payload.file_path}")
    report = svc.lint_zero_inline_comments(payload.file_path)
    return build_success_envelope(data=report, trace_id=trace_id)

@router.post("/algos/update/patch")
def apply_patch(payload: BatchPatchRequestDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    raw_ops = [op.dict() for op in payload.operations]
    results = svc.apply_batch_patch(raw_ops, dry_run=payload.dry_run)
    return build_success_envelope(
        data={"total_operations": len(results), "dry_run": payload.dry_run, "results": results},
        trace_id=trace_id,
    )

@router.post("/algos/update/diff")
def generate_diff(payload: DiffRequestDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    diff = svc.generate_diff(
        original_content=payload.original_content,
        modified_content=payload.modified_content,
        file_path=payload.file_path,
    )
    return build_success_envelope(data=diff, trace_id=trace_id)

@router.post("/graph/build")
def build_graph(request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    summary = svcs["graph"].build_graph_from_rules()
    return build_success_envelope(data=summary, trace_id=trace_id)

@router.post("/graph/query")
def query_graph(payload: GraphQueryDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    res = svcs["graph"].query_cypher(payload.query, payload.parameters)
    return build_success_envelope(
        data={
            "records": res.records,
            "nodes_count": len(res.nodes),
            "relationships_count": len(res.relationships),
        },
        trace_id=trace_id,
    )

@router.get("/graph/impact/{rule_id}")
def get_rule_impact(rule_id: str, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    impact = svcs["graph"].get_rule_impact(rule_id)
    return build_success_envelope(data={"rule_id": rule_id, "impact": impact}, trace_id=trace_id)


class AlgoComposeRequestDTO(BaseModel):
    algo_ids: List[str] = Field(..., description="Ordered list of algorithm IDs to compose")
    strict_check: bool = Field(default=True, description="Enforce strict contract safety checks")


@router.get("/algos/contracts")
def list_algorithm_contracts(
    request: Request,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    purity: Optional[str] = None,
    side_effects: Optional[str] = None,
) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    
    cat_enum = AlgorithmCategory(category) if category else None
    purity_enum = Purity(purity) if purity else None
    se_enum = SideEffectScope(side_effects) if side_effects else None
    tags_filter = [tag] if tag else None

    contracts = svcs["algo_registry"].list_algorithms(
        category=cat_enum,
        tags=tags_filter,
        purity=purity_enum,
        side_effects=se_enum,
    )
    return build_success_envelope(
        data={"total_contracts": len(contracts), "contracts": [c.model_dump() for c in contracts]},
        trace_id=trace_id,
    )


@router.get("/algos/contracts/{algo_id}")
def get_algorithm_contract(algo_id: str, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    contract = svcs["algo_registry"].get_algorithm(algo_id)
    if not contract:
        raise HTTPException(status_code=404, detail=f"Algorithm contract '{algo_id}' not found.")
    return build_success_envelope(data=contract.model_dump(), trace_id=trace_id)


@router.get("/algos/adapters")
def list_type_adapters(request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    adapters = svcs["algo_registry"].list_adapters()
    return build_success_envelope(
        data={"total_adapters": len(adapters), "adapters": [a.model_dump() for a in adapters]},
        trace_id=trace_id,
    )


@router.post("/algos/compose")
def compose_algorithm_pipeline(payload: AlgoComposeRequestDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    try:
        plan = svcs["composer"].compose_pipeline(
            algo_ids=payload.algo_ids,
            strict_contract_check=payload.strict_check,
        )
        return build_success_envelope(data=plan, trace_id=trace_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

