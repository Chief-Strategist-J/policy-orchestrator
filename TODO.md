# Policy Orchestrator & AI Meta-Agent: Master Roadmap & Algorithm Engine

This document tracks the comprehensive architecture, completed capabilities, the **1000+ Declarative Agent Catalog**, and the prioritized roadmap for the **Policy Orchestrator, Advanced GraphRAG, and AI Meta-Agent Engine** (`policies/policy-orchestrator`).

---

## 🏛️ Architectural Doctrine & Invariants

1. **Hexagonal Architecture (Ports & Adapters)**:
   - Domain business logic is 100% decoupled from concrete external SDKs, vector engines, and databases.
   - External dependencies (LLMs, Vector Stores, Graph Stores, Web Search, Tool Registries, Agent Registries) implement abstract domain ports.
2. **Zero-Inline-Comment Doctrine**:
   - Zero comments permitted inside function bodies, loop blocks, or conditional handlers.
   - All documentation, algorithmic blueprints, complexity metrics, and safety contracts live in top-side standardized module headers.
3. **Open Standards**:
   - W3C Distributed Trace Context (`traceparent` header propagation).
   - CloudEvents 1.0 event model alignment.
   - OpenAPI v3.1 contract conformance with uniform `{meta, data, errors}` response envelopes.
4. **Declarative Agent Scaling (Template for 1000+ Specialized Agents)**:
   - Agents are declared as frozen `AgentManifest` data structures (specifying `agent_id`, `role`, `system_prompt`, `allowed_tools`, and `algorithms`).
   - Zero boilerplate code duplication: 1000+ agents can be loaded from YAML manifests or dynamic registries instantly.

---

## 📊 Current Status & Feature Matrix

| Subsystem | Component | Status | Port / Contract | Adapters |
| :--- | :--- | :---: | :--- | :--- |
| **Domain** | LLM Engine | ✅ Completed | `LLMProviderPort` | `OpenAICompatibleAdapter` (vLLM/Ollama/DeepSeek/OpenAI), `MockLLMAdapter` |
| **Domain** | Vector Database | ✅ Completed | `VectorStorePort` | `InMemoryCosineVectorAdapter`, `QdrantVectorAdapter` |
| **Domain** | Graph Database | ✅ Completed | `GraphStorePort` | `InMemoryGraphAdapter`, `Neo4jGraphAdapter` (openCypher/Memgraph) |
| **Domain** | Live Search & Scraper | ✅ Completed | `WebSearchPort` | `DuckDuckGoSearchAdapter`, `MockWebSearchAdapter` |
| **Domain** | Tool Registry & Cache| ✅ Completed | `ToolRegistryPort` | `InMemoryToolRegistryAdapter` (Dynamic AST & Scraper Store) |
| **Domain** | Declarative Agent Manifests | ✅ Completed | `AgentManifestRegistryPort` | `InMemoryAgentManifestRegistryAdapter` (27+ Builtin Agents, scalable to 1000+) |
| **Domain** | Knowledge Source | ✅ Completed | `KnowledgeSourcePort`| `PolicyRulesMarkdownLoader` (Parses `policies/rules/`) |
| **Feature** | Invariant Audit | ✅ Completed | `AuditService` | Multi-vector pattern rules, severity triage |
| **Feature** | Hybrid RAG | ✅ Completed | `RAGService` | BM25 lexical search + dense vector + Reciprocal Rank Fusion (RRF) |
| **Feature** | Knowledge Graph | ✅ Completed | `KnowledgeGraphService`| Automatic entity & dependency extraction, BFS shortest path |
| **Feature** | AI Policy Meta-Agent | ✅ Completed | `AgentService` | ReAct reasoning loop, specialized agent execution, safety guardrails |
| **Delivery**| REST API | ✅ Completed | FastAPI v1 Router | Envelope `{meta, data, errors}`, trace context middleware, OpenAPI 3.1 |
| **Delivery**| CLI Utility | ✅ Completed | `python -m src.api.cli` | `audit`, `rag`, `agent`, `refactor`, `policy-check`, `serve` |
| **DevOps**  | Dockerization | ✅ Completed | Dockerfile + Compose | Multi-stage non-root runtime, Qdrant & Neo4j integration |

---

## 🤖 Declarative Agent Engine & Algorithm Registry (22 Algos + 5 Pipeline Roles)

All agents are declaratively defined in [`src/features/agent/registry/builtin_agents.py`](file:///home/btpl-lap-22/live/llm-obs-infra/policies/policy-orchestrator/src/features/agent/registry/builtin_agents.py) and managed via [`AgentManifestRegistryPort`](file:///home/btpl-lap-22/live/llm-obs-infra/policies/policy-orchestrator/src/domain/ports/agent_manifest_port.py).

### Core Pipeline Agents (5 Roles)
| Agent ID | Name | Role | Category | Primary Responsibility |
| :--- | :--- | :--- | :--- | :--- |
| `agent_scout` | Scout Agent | `SCOUT` | `core_pipeline` | File enumeration, ignore-list pruning, path filtering, and fast regex scanning. |
| `agent_planner` | Planner Agent | `PLANNER` | `core_pipeline` | Dependency analysis, SHA-256 precondition hashing, match count declaration, DAG creation. |
| `agent_editor` | Editor Agent | `EDITOR` | `core_pipeline` | AST-safe code transformations, Zero-Inline-Comment extraction, envelope wrapping. |
| `agent_verifier`| Verifier Agent | `VERIFIER` | `core_pipeline` | Invariant audits, pytest test suites, live RFC/CVE verification, zero-regression proof. |
| `agent_reporter`| Reporter Agent | `REPORTER` | `core_pipeline` | Structured diff summaries, OpenAPI changelogs, metric telemetry. |

### 22 Algorithm Specialized Agents (From `agent-operating-contract.md`)
| Algo # | Agent ID | Specialized Agent Name | Category | Algorithm & Data Structure |
| :---: | :--- | :--- | :--- | :--- |
| **1** | `algo_01_recursive_walk` | Recursive Walk Agent | `file_discovery` | DFS subtree walk with $O(\text{depth})$ path arena and early pruning |
| **2** | `algo_02_work_stealing_walker` | Work-Stealing Walker Agent | `file_discovery` | Lock-free Chase-Lev deques and thread-pinned I/O for monorepos |
| **3** | `algo_03_git_aware_walker` | Git-Aware Walker Agent | `file_discovery` | Git index reader parsing tracked tree and ignoring dirty worktrees |
| **4** | `algo_04_glob_matcher` | Glob Matcher Agent | `file_discovery` | Double-star glob trie matching path allowlists and denylists |
| **5** | `algo_05_binary_classifier` | Binary/Text Classifier Agent | `file_discovery` | Null-byte ($0x00$) and UTF-8 validity scanner guarding against binary writes |
| **6** | `algo_06_content_type_prober` | Content-Type Prober Agent | `file_discovery` | Magic byte header signatures and shebang interpreter detector |
| **7** | `algo_07_size_line_bouncer` | Size & Line Bouncer Agent | `file_discovery` | Hard file size ($\le 10\text{MB}$) and line count limiter preventing OOMs |
| **8** | `algo_08_generated_code_classifier` | Generated Code Classifier Agent | `file_discovery` | Token scanner identifying generated files (protobuf, openapi, mocks) |
| **9** | `algo_09_trigram_index` | Trigram Index Agent | `pattern_search` | N-gram inverted index for sub-millisecond candidate filtering |
| **10** | `algo_10_simd_memchr` | SIMD Literal Scanner Agent | `pattern_search` | Vectorized AVX-512/NEON byte matcher for exact string scanning |
| **11** | `algo_11_aho_corasick` | Aho-Corasick Multi-Pattern Agent | `pattern_search` | Finite state machine trie searching hundreds of keyword rules in $O(N)$ |
| **12** | `algo_12_lazy_dfa` | Lazy DFA Regex Agent | `pattern_search` | On-demand state transition regex engine with zero exponential backtracking |
| **13** | `algo_13_streaming_chunk_scanner` | Streaming Chunk Scanner Agent | `pattern_search` | Sliding window boundary scanner handling multi-line cross-chunk matches |
| **14** | `algo_14_context_snippet_collector` | Context Snippet Collector Agent | `pattern_search` | Surrounding line collector formatting syntax-highlighted issue snippets |
| **15** | `algo_15_mmap_scanner` | Memory-Mapped IO Scanner Agent | `pattern_search` | Zero-copy virtual memory scanner for extreme search throughput |
| **16** | `algo_16_position_span_tracker` | Position & Span Tracker Agent | `pattern_search` | Byte offset to line/column indexer computing exact replacement spans |
| **17** | `algo_17_tree_sitter_ast` | Tree-Sitter AST Scanner Agent | `structural_ast` | Grammar-based parser building concrete syntax trees across languages |
| **18** | `algo_18_cst_matcher` | Concrete Syntax Tree Matcher Agent | `structural_ast` | Lossless CST matcher preserving comments, whitespace, and formatting |
| **19** | `algo_19_symbol_scope_resolver` | Symbol Scope Resolver Agent | `structural_ast` | Lexical environment and symbol shadow resolver preventing scope conflicts |
| **20** | `algo_20_comment_extractor` | Comment & Docstring Extractor Agent | `structural_ast` | Inline comment classifier extracting mid-function comments into top docblocks |
| **21** | `algo_21_import_dependency_grapher` | Import & Dependency Grapher Agent | `structural_ast` | Module import resolver detecting cyclic dependencies and computing DAG orders |
| **22** | `algo_22_code_outline_generator` | Code Outline Generator Agent | `structural_ast` | Hierarchical symbol and class outline generator for high-level codebase maps |

---

## 🚀 Prioritized Upcoming Feature Roadmap

### 🔴 Priority P0: Critical / Immediate Value (Next Sprint)
*Features delivering direct 1000% speedup, automated refactoring, and real-time developer productivity.*

1. **AST-Safe Automated Zero-Inline-Comment Migrator**
   - **Impact:** High | **Category:** Automation / Compliance
   - Uses `libcst` (Python) and `tree-sitter` (Go, TypeScript) to extract inline comments from function bodies and generate standardized top-side docblock blueprints automatically.
2. **Real-Time Streaming Telemetry & SSE (`/api/v1/agent/stream`)**
   - **Impact:** High | **Category:** UX & Observability
   - Server-Sent Events (SSE) endpoint emitting token-by-token generation, ReAct thoughts, tool execution progress, and latency counters in real time.
3. **Multi-Project Workspace Batch Synchronizer**
   - **Impact:** High | **Category:** Multi-Repo Consistency
   - Single command (`policy-orchestrator sync --workspace-root ...`) to simultaneously audit and enforce uniform API envelopes, error codes, and lint boundaries across all submodules.
4. **GraphRAG Hybrid Fusion (Neo4j Community Walk + Qdrant Embeddings)**
   - **Impact:** High | **Category:** Advanced RAG
   - Traverses Neo4j subgraphs (`(:Rule)-[:ENFORCES]->(:Pattern)`) to collect topological neighbor context, combining it with Qdrant cosine similarity for multi-hop reasoning.

---

### 🟠 Priority P1: High Priority (Quality, Recall & Safety)
*Features enhancing search precision, automated tool creation, and observability telemetry.*

5. **Hypothetical Document Embeddings (HyDE) & Cross-Encoder Reranker**
   - **Impact:** High | **Category:** Advanced RAG
   - Generates zero-shot hypothetical answer candidates before embedding, followed by a local cross-encoder scoring stage to eliminate irrelevant context chunks.
6. **Auto-Generated Scraper & AST Tool Self-Registration**
   - **Impact:** Medium-High | **Category:** Meta-Agent Tooling
   - When the agent encounters an unknown library or documentation source, it generates a scraper, validates its parameters schema, and registers it to `ToolRegistryPort` for permanent workspace reuse.
7. **Self-Updating Policy Proposal Engine (Automated PR Generator)**
   - **Impact:** Medium-High | **Category:** Policy Evolution
   - Analyzes newly discovered production traps or anti-patterns and generates formatted markdown rule proposals directly into `policies/rules/edgeCases/`.
8. **OpenTelemetry Span Exporter to OTLP / Grafana Tempo**
   - **Impact:** Medium-High | **Category:** Observability
   - Native export of internal agent spans (Thought duration, Tool execution time, LLM inference latency) directly to OTLP collector endpoints.

---

### 🟡 Priority P2: Medium Priority (Scale & Distributed Workflows)
*Features for distributed coordination, sub-agent swarms, and CI/CD bot integrations.*

9. **Multi-Agent Swarm Delegation Pipeline**
   - **Impact:** Medium | **Category:** Agent Orchestration
   - Meta-Agent delegates tasks to specialized sub-agents (`agent_scout`, `agent_planner`, `agent_editor`, `agent_verifier`, `agent_reporter`).
10. **Temporal / Durable Workflow Orchestration Worker**
    - **Impact:** Medium | **Category:** Resilience
    - Enables durable, checkpointed execution of large-scale repository refactoring sagas that survive process restarts.
11. **CloudEvents Git PR Webhook Consumer**
    - **Impact:** Medium | **Category:** CI/CD Integration
    - Listens to GitHub/GitLab webhook events and runs automated policy compliance checks on open Pull Requests.

---

### 🟢 Priority P3: Future Optimizations & Multi-Modal
*Long-term performance and multi-modal intelligence capabilities.*

12. **Local Model Distillation & Fine-Tuning Pipeline**
    - **Impact:** Low-Medium | **Category:** AI Optimization
    - Fine-tunes small local quantized models (e.g. Qwen2.5-Coder-7B / Llama-3.2-3B) specifically on company policy invariants for sub-second offline checks.
13. **Multi-Modal Architecture Diagram Extractor**
    - **Impact:** Low-Medium | **Category:** Multi-Modal
    - Parses PNG/SVG/Mermaid architecture diagrams and validates them against the active knowledge graph and OpenAPI specs.

---

## 🔧 Environment Configuration Reference

| Environment Variable | Default Value | Description |
| :--- | :--- | :--- |
| `POLICY_RULES_DIR` | `../rules` | Path to markdown rules directory |
| `LLM_BACKEND` | `mock` | LLM backend: `mock`, `openai`, `ollama` |
| `VECTOR_BACKEND` | `inmemory` | Vector database: `inmemory`, `qdrant` |
| `GRAPH_BACKEND` | `inmemory` | Graph database: `inmemory`, `neo4j` |
| `SEARCH_BACKEND` | `mock` | Search provider: `mock`, `duckduckgo` |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant HTTP REST endpoint |
| `QDRANT_COLLECTION`| `policy_rules` | Qdrant collection name |
| `NEO4J_URI` | `http://localhost:7474` | Neo4j HTTP API endpoint |
| `NEO4J_USER` | `neo4j` | Neo4j basic auth username |
| `NEO4J_PASSWORD` | `policysecret` | Neo4j basic auth password |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | OpenAI-compatible endpoint URL |
| `OPENAI_API_KEY` | `EMPTY` | API Key for model authentication |
| `OPENAI_MODEL` | `gpt-4o` | Model name for chat completions |
| `OLLAMA_BASE_URL` | `http://localhost:11434/v1` | Ollama local inference endpoint |
| `OLLAMA_MODEL` | `llama3.2` | Ollama local model tag |

---

## 🧪 Daily Commands & Testing Cheat Sheet

```bash
# 1. Run all unit and integration test suites
python3 -m unittest discover -s tests -p "test_*.py"

# 2. Search Grounded Policy Rules via Advanced Hybrid RAG
python3 src/api/cli/main.py rag search --query "transactional outbox dual write prevention"

# 3. Execute Autonomous AI Meta-Agent for multi-step reasoning
python3 src/api/cli/main.py agent "Audit the repository, search live RFC standards, and verify zero inline comments"

# 4. Invariant Contract Compliance Check
python3 src/api/cli/main.py policy-check

# 5. Launch REST API Server
python3 src/api/cli/main.py serve --host 0.0.0.0 --port 8000

# 6. Run Complete Stack via Docker Compose (Orchestrator + Qdrant + Neo4j)
docker compose up --build -d
```
