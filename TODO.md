# Policy Orchestrator & AI Meta-Agent: Master Roadmap & TODO

This document tracks the comprehensive architecture, completed capabilities, and high-impact daily features for the **Policy Orchestrator, Advanced GraphRAG, and AI Meta-Agent Engine** (`policies/policy-orchestrator`).

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

## 📋 Comprehensive Daily Features & Roadmap Tracker

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

### Phase 2: Advanced RAG & GraphRAG Retrieval (✅ Core Built / ⏳ Daily Enhancements)
- [x] Implement `RAGService` with BM25 inverted index tokenization and Reciprocal Rank Fusion (RRF).
- [x] Ground RAG directly against `policies/rules/` markdown contracts.
- [x] Implement `KnowledgeGraphService` extracting `(:Rule)-[:BELONGS_TO]->(:Category)` and `(:Rule)-[:ENFORCES]->(:ArchitecturePattern)` relationships.
- [ ] **GraphRAG Hybrid Fusion**: Combine graph community traversal with dense vector context for multi-hop reasoning.
- [ ] **Hypothetical Document Embeddings (HyDE)**: Generate zero-shot hypothetical policy responses to boost dense similarity recall on complex queries.
- [ ] **Self-Correction & Cross-Encoder Reranker**: Add light cross-encoder scoring stage to filter out low-confidence chunks.
- [ ] **Hierarchical Context Summarizer**: Automatic multi-level summary generation for large policy catalogs.

### Phase 3: Meta-Agent ("Agent of Agents") & Tool Reuse Engine (✅ Core Built / ⏳ Advanced Extensions)
- [x] Implement `AgentService` autonomous ReAct reasoning loop with dynamic tool dispatching (`search_policy_rules`, `search_internet_knowledge`, `search_codebase_ast`, `register_reusable_tool`, `run_repo_audit`, `generate_refactoring_plan`).
- [x] Create `AGENTS.md` defining strict operating contracts for self-improvement and consistency enforcement.
- [x] Integrate `ToolRegistryPort` to store and discover custom scrapers and AST code searchers without code duplication.
- [ ] **Multi-Agent Swarm Orchestration**: Sub-agent delegation for specialized tasks (Linter Agent, Security Agent, Refactor Agent, Docs Agent).
- [ ] **Auto-Generated Scraper Catalog**: Automatic creation and persistence of website/API documentation scrapers for upstream libraries.
- [ ] **Self-Updating Policy Engine**: Meta-Agent evaluates codebase anomalies and proposes automated pull requests to update `policies/rules/`.

### Phase 4: Project-Wide Bulk Consistency & Safe Refactoring (⏳ In Progress)
- [x] Implement batch search-and-replace in `RefactorService` with regex and file extension filtering.
- [ ] **AST-Safe Automated Code Refactoring**: Deepen refactoring using `libcst` (Python) and `tree-sitter` (Go, TypeScript).
- [ ] **Zero-Inline-Comment Auto-Migrator**: AST tool to extract inline comments from function bodies and format them into top-side blueprint docblocks automatically.
- [ ] **Multi-Project Workspace Synchronizer**: Single CLI command to synchronize architecture invariants, envelopes, and lint rules across all submodules simultaneously.
- [ ] **Atomic Rollback & Dry-Run Diff Engine**: Generates visual side-by-side patch previews before executing mutations.

### Phase 5: Delivery Interfaces, Streaming & Open Standards (✅ Core Built / ⏳ Telemetry)
- [x] Implement standardized API envelope (`{meta, data, errors}`) per `api-request-response-structure.md`.
- [x] Implement FastAPI REST API v1 endpoints (`/health`, `/rag/search`, `/rag/index`, `/agent/run`, `/audit/scan`, `/graph/build`, `/graph/query`, `/graph/impact/{rule_id}`).
- [x] Implement unified CLI entrypoint (`src/api/cli/main.py`) with `audit`, `rag`, `agent`, `refactor`, `policy-check`, `serve` commands.
- [x] Multi-stage `Dockerfile` with non-root security (`appuser:appgroup` UID 10001).
- [x] `docker-compose.yml` stack with `policy-orchestrator`, `qdrant`, and `neo4j`.
- [ ] **Server-Sent Events (SSE) Stream Endpoint**: `/api/v1/agent/stream` for real-time agent token and reasoning telemetry.
- [ ] **OpenTelemetry Span Export**: Export trace spans directly to OTLP collector / Jaeger.

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
