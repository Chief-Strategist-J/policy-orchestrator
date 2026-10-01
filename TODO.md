# Policy Orchestrator & AI Meta-Agent: Master Roadmap & TODO

This document tracks the comprehensive architecture, completed capabilities, and prioritized roadmap for the **Policy Orchestrator, Advanced GraphRAG, and AI Meta-Agent Engine** (`policies/policy-orchestrator`).

---

## 🏛️ Architectural Doctrine & Invariants

1. **Hexagonal Architecture (Ports & Adapters)**:
   - Domain business logic is 100% decoupled from concrete external SDKs, vector engines, and databases.
   - External dependencies (LLMs, Vector Stores, Graph Stores, Web Search, Tool Registries) implement abstract domain ports.
2. **Zero-Inline-Comment Doctrine**:
   - Zero comments permitted inside function bodies, loop blocks, or conditional handlers.
   - All documentation, algorithmic blueprints, complexity metrics, and safety contracts live in top-side standardized module headers.
3. **Open Standards**:
   - W3C Distributed Trace Context (`traceparent` header propagation).
   - CloudEvents 1.0 event model alignment.
   - OpenAPI v3 contract conformance with uniform `{meta, data, errors}` response envelopes.
4. **Agent of Agents (Meta-Agent Orchestrator)**:
   - Designed to maintain consistency across large multi-project workspaces and accelerate feature delivery by 1000%.
   - Reusable tool and scraper registry prevents repeating tool creation work.

---

## 📊 Current Status & Feature Matrix

| Subsystem | Component | Status | Port / Contract | Adapters |
| :--- | :--- | :---: | :--- | :--- |
| **Domain** | LLM Engine | ✅ Completed | `LLMProviderPort` | `OpenAICompatibleAdapter` (vLLM/Ollama/DeepSeek/OpenAI), `MockLLMAdapter` |
| **Domain** | Vector Database | ✅ Completed | `VectorStorePort` | `InMemoryCosineVectorAdapter`, `QdrantVectorAdapter` |
| **Domain** | Graph Database | ✅ Completed | `GraphStorePort` | `InMemoryGraphAdapter`, `Neo4jGraphAdapter` (openCypher/Memgraph) |
| **Domain** | Live Search & Scraper | ✅ Completed | `WebSearchPort` | `DuckDuckGoSearchAdapter`, `MockWebSearchAdapter` |
| **Domain** | Tool Registry & Cache| ✅ Completed | `ToolRegistryPort` | `InMemoryToolRegistryAdapter` (Dynamic AST & Scraper Store) |
| **Domain** | Knowledge Source | ✅ Completed | `KnowledgeSourcePort`| `PolicyRulesMarkdownLoader` (Parses `policies/rules/`) |
| **Feature** | Invariant Audit | ✅ Completed | `AuditService` | Multi-vector pattern rules, severity triage |
| **Feature** | Hybrid RAG | ✅ Completed | `RAGService` | BM25 lexical search + dense vector + Reciprocal Rank Fusion (RRF) |
| **Feature** | Knowledge Graph | ✅ Completed | `KnowledgeGraphService`| Automatic entity & dependency extraction, BFS shortest path |
| **Feature** | AI Policy Meta-Agent | ✅ Completed | `AgentService` | ReAct reasoning loop, dynamic tool execution, safety guardrails |
| **Delivery**| REST API | ✅ Completed | FastAPI v1 Router | Envelope `{meta, data, errors}`, trace context middleware |
| **Delivery**| CLI Utility | ✅ Completed | `python -m src.api.cli` | `audit`, `rag`, `agent`, `refactor`, `policy-check`, `serve` |
| **DevOps**  | Dockerization | ✅ Completed | Dockerfile + Compose | Multi-stage non-root runtime, Qdrant & Neo4j integration |

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
   - Meta-Agent delegates tasks to specialized sub-agents:
     - `LinterAgent`: Verifies comment doctrines and naming conventions.
     - `SecurityAgent`: Scans for tenant leaks and authorization gaps.
     - `RefactorAgent`: Executes safe AST transformations.
     - `DocsAgent`: Keeps OpenAPI, AsyncAPI, and markdown synced.
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

## 📋 Historical & Completed Milestones

### Phase 1: Core Foundation & Hexagonal Scaffolding (✅ Completed)
- [x] Establish Hexagonal folder structure conforming to `api-structure.md`.
- [x] Create `LLMProviderPort` with streaming, function calling, and dense vector embeddings.
- [x] Create `VectorStorePort` with batch upsert, metadata filtering, and cosine distance queries.
- [x] Create `GraphStorePort` with node/edge upsert, Cypher queries, and topological path search.
- [x] Create `WebSearchPort` for live internet RFC/CVE lookups and clean page scraping.
- [x] Create `ToolRegistryPort` for caching and reusing dynamically generated AST searchers.
- [x] Create `KnowledgeSourcePort` with Markdown heading-aware chunking and taxonomy classification.
- [x] Implement `MockLLMAdapter` with deterministic feature hashing for offline CI execution.
- [x] Implement `OpenAICompatibleAdapter` for Ollama, vLLM, DeepSeek, and OpenAI endpoints.
- [x] Implement `InMemoryCosineVectorAdapter` for zero-dependency local runs.
- [x] Implement `QdrantVectorAdapter` for open-source scalable vector search.
- [x] Implement `InMemoryGraphAdapter` with BFS shortest-path and pattern queries.
- [x] Implement `Neo4jGraphAdapter` for open-standard Cypher graph querying.

### Phase 2: Core RAG & Meta-Agent Delivery (✅ Completed)
- [x] Implement `RAGService` with BM25 inverted index tokenization and Reciprocal Rank Fusion (RRF).
- [x] Ground RAG directly against `policies/rules/` markdown contracts.
- [x] Implement `KnowledgeGraphService` extracting `(:Rule)-[:BELONGS_TO]->(:Category)` and `(:Rule)-[:ENFORCES]->(:ArchitecturePattern)` relationships.
- [x] Implement `AgentService` autonomous ReAct reasoning loop with dynamic tool dispatching (`search_policy_rules`, `search_internet_knowledge`, `search_codebase_ast`, `register_reusable_tool`, `run_repo_audit`, `generate_refactoring_plan`).
- [x] Create `AGENTS.md` defining strict operating contracts for self-improvement and consistency enforcement.
- [x] Standardized response envelope (`{meta, data, errors}`) per `api-request-response-structure.md`.
- [x] FastAPI REST API v1 endpoints (`/health`, `/rag/search`, `/rag/index`, `/agent/run`, `/audit/scan`, `/graph/build`, `/graph/query`, `/graph/impact/{rule_id}`).
- [x] Unified CLI entrypoint (`src/api/cli/main.py`) with all subcommands.
- [x] Multi-stage `Dockerfile` and `docker-compose.yml` with `policy-orchestrator`, `qdrant`, and `neo4j`.

---

## 🔧 Environment Configuration Reference

| Environment Variable | Default Value | Description |
| :--- | :--- | :--- |
| `POLICY_RULES_DIR` | `../rules` | Path to markdown rules directory |
| `LLM_BACKEND` | `mock` | LLM backend: `mock`, `openai`, `ollama` |
| `VECTOR_BACKEND` | `inmemory` | Vector database: `inmemory`, `qdrant` |
| `GRAPH_BACKEND` | `inmemory` | Graph database: `inmemory`, `neo4j` |
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
