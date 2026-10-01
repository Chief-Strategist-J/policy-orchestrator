#!/usr/bin/env python3
"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: POLICY ORCHESTRATOR CLI ENTRYPOINT
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides the unified command-line interface for the
   policy-orchestrator system. It dispatches commands for:
   - `audit`: Scans repository invariants and architecture rules.
   - `rag`: Grounded semantic retrieval over policy markdown rules.
   - `agent`: Autonomous AI agent execution for analysis and safe refactoring.
   - `refactor`: Batch AST / regex code refactoring.
   - `policy-check`: Engineering contract verification.
   - `serve`: Launches Uvicorn REST API server.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All subcommand dispatch logic, arguments,
     and terminal formatting routines are documented solely in this top-side header.
     Functions and loops remain 100% comment-free and pure.
   - Posix Exit Codes: 0 for success, 1 for violations/errors.
================================================================================
"""

import sys
import os
from pathlib import Path

REPO_ROOT = str(Path(__file__).resolve().parent.parent.parent.parent)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import json
import argparse
from dataclasses import asdict
from typing import List

from src.features.audit.service.audit_service import AuditService
from src.features.refactor.service.refactor_service import RefactorService
from src.features.policy_sync.service.policy_sync_service import PolicySyncService
from src.features.rag.service.rag_service import RAGService
from src.features.rag.types.rag_types import RAGQueryRequest
from src.features.agent.service.agent_service import AgentService
from src.features.agent.types.agent_types import AgentExecutionRequest
from src.infra.adapters.knowledge.policy_rules_loader import PolicyRulesMarkdownLoader
from src.infra.adapters.vector.in_memory_vector_adapter import InMemoryCosineVectorAdapter
from src.infra.adapters.llm.openai_compatible_adapter import OpenAICompatibleAdapter
from src.infra.adapters.llm.mock_llm_adapter import MockLLMAdapter

def _init_rag_and_agent(rules_dir: str, backend: str):
    knowledge_source = PolicyRulesMarkdownLoader(base_rules_dir=rules_dir)
    vector_store = InMemoryCosineVectorAdapter()

    if backend == "openai":
        llm_provider = OpenAICompatibleAdapter(
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            model_name=os.environ.get("OPENAI_MODEL", "gpt-4o"),
        )
    elif backend == "ollama":
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
    return rag_svc, agent_svc

def handle_audit_command(args: argparse.Namespace) -> int:
    service = AuditService()
    findings = service.audit_repository(args.root)

    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
        return 1 if any(f.severity in {"CRITICAL", "HIGH"} for f in findings) else 0

    print(f"\n{'='*75}")
    print(f"🔍 POLICY ORCHESTRATOR AUDIT: {len(findings)} Total Findings")
    print(f"{'='*75}\n")

    if not findings:
        print("✅ Repository is 100% clean. Zero invariant violations detected.")
        return 0

    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        matched = [f for f in findings if f.severity == sev]
        if matched:
            print(f"\n--- [{sev}] ({len(matched)} issues) ---")
            for item in matched:
                print(f"  [{item.rule_id}] {item.file}:{item.line}")
                print(f"     Description: {item.description}")
                print(f"     Snippet    : {item.snippet}")
                print(f"     Fix        : {item.recommendation}\n")

    return 1 if any(f.severity in {"CRITICAL", "HIGH"} for f in findings) else 0

def handle_rag_command(args: argparse.Namespace) -> int:
    rag_svc, _ = _init_rag_and_agent(args.rules_dir, args.backend)
    
    if args.action == "index":
        count = rag_svc.index_all_rules()
        print(f"✅ Indexed {count} policy chunks into vector index.")
        return 0

    res = rag_svc.retrieve_context(
        RAGQueryRequest(
            query=args.query,
            top_k=args.top_k,
            category_filter=args.category,
        )
    )

    if args.json:
        print(json.dumps(asdict(res), indent=2))
        return 0

    print(f"\n{'='*75}")
    print(f"📚 GROUNDED POLICY RETRIEVAL: {res.total_found} Matches ({res.latency_ms} ms)")
    print(f"{'='*75}\n")
    print(res.formatted_context_block)
    return 0

def handle_agent_command(args: argparse.Namespace) -> int:
    _, agent_svc = _init_rag_and_agent(args.rules_dir, args.backend)
    req = AgentExecutionRequest(
        prompt=args.prompt,
        target_directory=args.target_dir,
        max_steps=args.max_steps,
    )
    result = agent_svc.execute_agent_loop(req)

    if args.json:
        print(json.dumps(asdict(result), indent=2))
        return 0

    print(f"\n{'='*75}")
    print(f"🤖 AI POLICY AGENT EXECUTION: {result.status} ({result.duration_ms} ms)")
    print(f"{'='*75}\n")
    print(f"Session ID : {result.session_id}")
    print(f"Steps Taken: {result.total_steps}")
    print(f"Sources    : {', '.join(result.grounded_sources) if result.grounded_sources else 'None'}\n")

    for step in result.steps:
        print(f"Step {step.step_number}: {step.thought}")
        if step.tool_calls:
            for tc in step.tool_calls:
                print(f"  🔧 Tool: {tc.tool_name} -> {tc.status}")

    print(f"\n--- Final Answer ---\n{result.final_response}\n")
    return 0

def handle_refactor_command(args: argparse.Namespace) -> int:
    service = RefactorService()
    exts = set(e.strip().lower() for e in args.ext.split(","))
    result = service.execute_batch_replace(
        root_dir=args.root,
        find_pattern=args.find,
        replace_text=args.replace,
        extensions=exts,
        is_regex=args.regex,
        dry_run=not args.apply,
    )

    if args.json:
        print(json.dumps(asdict(result), indent=2))
        return 0

    status = "[APPLIED]" if args.apply else "[DRY-RUN]"
    print(f"\n⚡ BATCH REFACTOR {status}: {result.total_occurrences} occurrences in {result.modified_files} files.\n")
    for d in result.details:
        state = "Modified" if d.modified else "Would modify"
        print(f"  - {d.file_path}: {d.occurrences} matches ({state})")

    return 0

def handle_policy_check_command(args: argparse.Namespace) -> int:
    service = PolicySyncService()
    report = service.audit_policy_contract(args.path)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
        return 1 if report.non_compliant_count > 0 else 0

    print(f"\n{'='*75}")
    print(f"📜 POLICY CONTRACT AUDIT REPORT: {report.total_algorithms_found} Total Algorithms")
    print(f"   Compliant: {report.fully_compliant_count} | Non-Compliant: {report.non_compliant_count}")
    print(f"{'='*75}\n")

    if report.non_compliant_count > 0:
        print("Non-compliant algorithm entries requiring optimization:")
        for a in report.audits:
            if not a.is_fully_compliant:
                missing = []
                if not a.has_definition: missing.append("definition")
                if not a.has_complexity: missing.append("complexity")
                if a.step_count < 4: missing.append(f"steps({a.step_count})")
                if not a.has_agent_role: missing.append("agent_role")
                print(f"  - [Algorithm {a.algorithm_id}] {a.title} (Missing: {', '.join(missing)})")
        return 1

    print("✅ All algorithm entries strictly conform to the engineering contract standard.")
    return 0

from src.features.search_engine.service.search_engine_service import SearchEngineService

def handle_algo_command(args: argparse.Namespace) -> int:
    svc = SearchEngineService()

    if args.action == "scan":
        patterns = [p.strip() for p in args.patterns.split(",") if p.strip()]
        results = svc.scan_directory_multipattern(args.root, patterns)
        if args.json:
            print(json.dumps(results, indent=2))
            return 0
        print(f"\n{'='*75}")
        print(f"🔎 MULTI-PATTERN ALGO SCAN: {len(results)} Files Matched")
        print(f"{'='*75}\n")
        for res in results:
            print(f"📁 {res['file']} ({res['match_count']} matches)")
            for m in res["matches"][:3]:
                print(f"   Line {m['line']} [{m['pattern']}]: {m['context']}")
        return 0

    elif args.action == "outline":
        res = svc.inspect_file_outline(args.file)
        if args.json:
            print(json.dumps(res, indent=2))
            return 0
        print(res["markdown"])
        return 0

    elif args.action == "lint-comments":
        res = svc.lint_zero_inline_comments(args.file)
        if args.json:
            print(json.dumps(res, indent=2))
            return 0 if res["is_compliant"] else 1
        status = "✅ COMPLIANT" if res["is_compliant"] else "❌ VIOLATION"
        print(f"\n{'='*75}")
        print(f"🛡️ ZERO-INLINE-COMMENT DOCTRINE: {status}")
        print(f"   File: {res['file']}")
        print(f"   Banned Inline Comments: {res['banned_inline_count']}")
        print(f"   TODOs/FIXMEs: {res['todos_count']}")
        print(f"{'='*75}\n")
        for c in res["banned_comments"]:
            print(f"   Line {c['line']}: {c['text']}")
        return 0 if res["is_compliant"] else 1

    elif args.action == "dependencies":
        res = svc.analyze_module_dependencies(args.directory)
        if args.json:
            print(json.dumps(res, indent=2))
            return 0
        print(f"\n{'='*75}")
        print(f"🕸️ IMPORT DEPENDENCY GRAPH: {res['total_modules']} Modules, {res['total_edges']} Edges")
        print(f"   Has Cycles: {'⚠️ YES' if res['has_cycles'] else '✅ NO'}")
        print(f"{'='*75}\n")
        if res["cycles"]:
            print("Detected Cycles:")
            for cycle in res["cycles"]:
                print(f"  🔁 {' -> '.join(cycle)}")
        print(f"\nTopological Build Order ({len(res['topological_order'])} modules):")
        print(f"  {' -> '.join(res['topological_order'][:10])}{' ...' if len(res['topological_order']) > 10 else ''}")
        return 0

    return 0

def handle_serve_command(args: argparse.Namespace) -> int:
    import uvicorn
    os.environ["POLICY_RULES_DIR"] = args.rules_dir
    os.environ["LLM_BACKEND"] = args.backend
    uvicorn.run("src.api.rest.app:app", host=args.host, port=args.port, reload=args.reload)
    return 0

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="policy-orchestrator",
        description="Repository Invariant Auditor, AI Agent & Policy Orchestrator",
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    audit_parser = subparsers.add_parser("audit", help="Run multi-vector invariant scan")
    audit_parser.add_argument("--root", default=".", help="Root directory")
    audit_parser.add_argument("--json", action="store_true", help="Output findings as JSON")

    algo_parser = subparsers.add_parser("algo", help="Execute 22 core algorithms & code analyzers")
    algo_parser.add_argument("action", choices=["scan", "outline", "lint-comments", "dependencies"], help="Algorithm action")
    algo_parser.add_argument("--root", default=".", help="Root directory")
    algo_parser.add_argument("--patterns", default="TODO,FIXME,error,critical", help="Comma-separated patterns")
    algo_parser.add_argument("--file", default="src/api/cli/main.py", help="File to inspect")
    algo_parser.add_argument("--directory", default="src", help="Directory to analyze")
    algo_parser.add_argument("--json", action="store_true", help="Output as JSON")

    rag_parser = subparsers.add_parser("rag", help="Retrieve or index grounded policy rules")
    rag_parser.add_argument("action", choices=["search", "index"], help="RAG action")
    rag_parser.add_argument("--query", default="", help="Search query")
    rag_parser.add_argument("--category", default=None, help="Policy category filter")
    rag_parser.add_argument("--top-k", type=int, default=5, help="Number of documents to retrieve")
    rag_parser.add_argument("--rules-dir", default="../rules", help="Path to rules folder")
    rag_parser.add_argument("--backend", default="mock", choices=["mock", "openai", "ollama"], help="LLM backend")
    rag_parser.add_argument("--json", action="store_true", help="Output as JSON")

    agent_parser = subparsers.add_parser("agent", help="Run autonomous AI policy agent")
    agent_parser.add_argument("prompt", help="Task prompt for the agent")
    agent_parser.add_argument("--target-dir", default=".", help="Directory to analyze")
    agent_parser.add_argument("--max-steps", type=int, default=8, help="Maximum reasoning steps")
    agent_parser.add_argument("--rules-dir", default="../rules", help="Path to rules folder")
    agent_parser.add_argument("--backend", default="mock", choices=["mock", "openai", "ollama"], help="LLM backend")
    agent_parser.add_argument("--json", action="store_true", help="Output as JSON")

    refactor_parser = subparsers.add_parser("refactor", help="Execute safe batch search-and-replace")
    refactor_parser.add_argument("--root", default=".", help="Root directory")
    refactor_parser.add_argument("--find", required=True, help="Pattern to find")
    refactor_parser.add_argument("--replace", required=True, help="Replacement string")
    refactor_parser.add_argument("--ext", default=".go,.ts,.js,.py,.sql", help="Extensions")
    refactor_parser.add_argument("--regex", action="store_true", help="Treat pattern as regex")
    refactor_parser.add_argument("--apply", action="store_true", help="Apply mutations")
    refactor_parser.add_argument("--json", action="store_true", help="Output summary as JSON")

    policy_parser = subparsers.add_parser("policy-check", help="Audit markdown contracts")
    policy_parser.add_argument("--path", default="policies/rules/edgeCases/algos/agent-operating-contract.md", help="Contract path")
    policy_parser.add_argument("--json", action="store_true", help="Output report as JSON")

    serve_parser = subparsers.add_parser("serve", help="Launch FastAPI REST server")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Bind host")
    serve_parser.add_argument("--port", type=int, default=8000, help="Bind port")
    serve_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    serve_parser.add_argument("--rules-dir", default="../rules", help="Path to rules folder")
    serve_parser.add_argument("--backend", default="mock", choices=["mock", "openai", "ollama"], help="LLM backend")

    args = parser.parse_args()

    dispatch = {
        "audit": handle_audit_command,
        "algo": handle_algo_command,
        "rag": handle_rag_command,
        "agent": handle_agent_command,
        "refactor": handle_refactor_command,
        "policy-check": handle_policy_check_command,
        "serve": handle_serve_command,
    }

    handler = dispatch.get(args.subcommand)
    if handler:
        sys.exit(handler(args))

if __name__ == "__main__":
    main()
