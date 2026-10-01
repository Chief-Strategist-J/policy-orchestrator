# AGENTS.md — Autonomous Meta-Agent Operating Contract & Self-Improvement Protocol

This document defines the strict, non-negotiable operational doctrine for the **AI Policy Meta-Agent (Agent of Agents)** operating within this workspace.

---

## 🎯 1. Core Mission: 1000% Faster Shipping with 100% Architectural Consistency

The Meta-Agent orchestrates sub-agents, tools, and refactoring pipelines across multi-repo environments. Its purpose is to eliminate architectural drift, eliminate boilerplate re-inventions, and enforce ironclad invariants across all codebase assets.

### Five Fundamental Invariants:
1. **Hexagonal Architecture (Ports & Adapters)**:
   - Domain business logic MUST depend strictly on abstract domain ports (`src/domain/ports/`).
   - Concrete databases, HTTP clients, LLM providers, and file walkers MUST live exclusively in infrastructure adapters (`src/infra/adapters/`).
   - ZERO vendor lock-in is permitted.
2. **Zero-Inline-Comment Doctrine**:
   - ZERO comments permitted inside function bodies, loop blocks, or conditional handlers.
   - All documentation, algorithmic blueprints, complexity metrics, and safety contracts MUST live in standardized top-side module docblocks.
3. **Open Standards Alignment**:
   - All network calls must extract and propagate W3C `traceparent` headers.
   - Event models must adhere to CloudEvents 1.0 specifications.
   - REST responses must follow the uniform `{meta, data, errors}` envelope.
4. **Tool Generation, Caching & Reusability**:
   - If a custom AST code searcher, regex scanner, or web scraper is created, it MUST be registered to the `ToolRegistryPort` to prevent repetitive re-generation.
5. **Grounded Invariant Verification**:
   - The agent MUST retrieve context from `policies/rules/` (via GraphRAG/Hybrid RAG) and cross-verify with live internet RFCs/CVEs before executing mutations.

---

## 🔄 2. Self-Improvement & Learning Loop

```
┌──────────────────────────────────────────────────────────────┐
│                  Self-Improvement Pipeline                   │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
            [1. Audit & Identify Violation / Gap]
                               │
                               ▼
        [2. Query Grounded Policy Rules & Live RFCs]
                               │
                               ▼
          [3. Check Reusable Tool Cache in Registry]
            ├── If Found: Reuse existing tool
            └── If Missing: Generate & Register new tool
                               │
                               ▼
        [4. Execute Safe Refactoring / AST Transformation]
                               │
                               ▼
        [5. Run Verification Suite (Pytest / Linters)]
                               │
                               ▼
        [6. Propose Policy Rule Enhancement if New Trap]
```

### Self-Improvement Rules:
- **Heuristic Extraction**: When a new failure mode or edge case is discovered in code, the agent must not only fix the code but also record the invariant into `policies/rules/edgeCases/`.
- **Tool Optimization**: When an existing tool in the `ToolRegistry` is slow or inaccurate, the agent refactors the tool record and bumps its version rather than creating duplicate tools.
- **AST-Level Precision**: Prefer AST parser modifications over blind regex replacements to guarantee syntax correctness.

---

## 🛠️ 3. Reusable Tooling & Scraper Protocols

When generating code searchers or web scrapers:
1. **Naming Standard**: `search_<lang>_<pattern>` (e.g. `search_python_naked_sleep`, `search_go_goroutine_leak`, `scrape_rfc_standard`).
2. **Persistence**: Call `register_reusable_tool` tool to persist the tool definition and parameters schema into the registry.
3. **Zero Redundancy**: Before proposing new scripts, check `list_tools` to see if a verified tool already exists.

---

## 🔍 4. Multi-Project Bulk Update & Refactoring Checklist

When executing batch modifications across multiple services:
- [ ] **Step 1 — Pre-Flight Invariant Scan**: Run `run_repo_audit` across target repositories.
- [ ] **Step 2 — Dependency Topological Sort**: Use `KnowledgeGraphService` to determine change sequence (core packages first, downstream features second).
- [ ] **Step 3 — Dry-Run Validation**: Generate refactoring diffs without disk mutations; verify AST validity.
- [ ] **Step 4 — Atomic Disk Write**: Apply code edits with Zero-Inline-Comment formatting.
- [ ] **Step 5 — Automated Unit & Integration Testing**: Run `python -m unittest discover` to ensure 100% test pass rate.
- [ ] **Step 6 — Multi-Repo Submodule Synchronization**: Commit and push changes in submodule order (leaf submodule first, parent repository last).

---

## ⚡ 5. Terminal CLI Command Quick Reference

```bash
# Grounded Hybrid Policy RAG Search
python3 src/api/cli/main.py rag search --query "dual write transactional outbox"

# Autonomous AI Agent Task Execution
python3 src/api/cli/main.py agent "Audit repository and register missing AST searchers"

# Invariant Policy Contract Validation
python3 src/api/cli/main.py policy-check

# Launch Orchestrator REST API
python3 src/api/cli/main.py serve --host 0.0.0.0 --port 8000
```
