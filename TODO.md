# Policy Orchestrator & AI Agent: Master Roadmap & TODO

This document tracks the technical roadmap, architectural invariants, completed capabilities, and planned features for the **Policy Orchestrator & AI Agent Engine** (`policies/policy-orchestrator`).

---

## 🏛️ Architectural Doctrine & Invariants

1. **Hexagonal Architecture (Ports & Adapters)**:
   - Zero direct coupling between core domain logic and external SDKs/databases.
   - All external dependencies (LLMs, Vector Stores, Graph Stores, Knowledge Sources) must implement abstract domain ports.
2. **Zero-Inline-Comment Doctrine**:
   - No inline comments inside function bodies, loops, or control-flow blocks.
   - All documentation, algorithmic blueprints, and design contracts live in top-side standardized module headers.
3. **Open Standards**:
   - W3C Distributed Trace Context (`traceparent` header propagation).
   - CloudEvents 1.0 event model alignment.
   - OpenAPI v3 contract conformance with uniform `{meta, data, errors}` response envelopes.

---

## 📊 Current Status & Feature Matrix

| Subsystem | Component | Status | Port / Contract | Adapters |
| :--- | :--- | :---: | :--- | :--- |
| **Domain** | LLM Engine | ✅ Completed | `LLMProviderPort` | `OpenAICompatibleAdapter` (vLLM/Ollama/DeepSeek/OpenAI), `MockLLMAdapter` |
| **Domain** | Vector Database | ✅ Completed | `VectorStorePort` | `InMemoryCosineVectorAdapter`, `QdrantVectorAdapter` |
| **Domain** | Graph Database | ✅ Completed | `GraphStorePort` | `InMemoryGraphAdapter`, `Neo4jGraphAdapter` (openCypher/Memgraph) |
| **Domain** | Knowledge Source | ✅ Completed | `KnowledgeSourcePort`| `PolicyRulesMarkdownLoader` (Parses `policies/rules/`) |
| **Feature** | Invariant Audit | ✅ Completed | `AuditService` | Multi-vector pattern rules, severity triage |
| **Feature** | Hybrid RAG | ✅ Completed | `RAGService` | BM25 lexical search + dense vector + Reciprocal Rank Fusion (RRF) |
| **Feature** | AI Policy Agent | ✅ Completed | `AgentService` | ReAct reasoning loop, tool execution, safety guardrails |
| **Feature** | Knowledge Graph | ✅ Completed | `KnowledgeGraphService`| Automatic entity & dependency extraction, BFS shortest path |
| **Delivery**| REST API | ✅ Completed | FastAPI v1 Router | Envelope `{meta, data, errors}`, trace context middleware |
| **Delivery**| CLI Utility | ✅ Completed | `python -m src.api.cli` | `audit`, `rag`, `agent`, `refactor`, `policy-check`, `serve` |
| **DevOps**  | Dockerization | ✅ Completed | Dockerfile + Compose | Multi-stage non-root runtime, Qdrant & Neo4j integration |

---

## 📋 Comprehensive TODO & Milestone Tracker

### Phase 1: Core Foundation & Hexagonal Scaffolding (✅ Completed)
- [x] Establish Hexagonal folder structure conforming to `api-structure.md`.
- [x] Create `LLMProviderPort` with streaming, function calling, and dense vector embeddings.
- [x] Create `VectorStorePort` with batch upsert, metadata filtering, and cosine distance queries.
- [x] Create `GraphStorePort` with node/edge upsert, Cypher queries, and topological path search.
- [x] Create `KnowledgeSourcePort` with Markdown heading-aware chunking and taxonomy classification.
- [x] Implement `MockLLMAdapter` with deterministic feature hashing for offline CI execution.
- [x] Implement `OpenAICompatibleAdapter` for Ollama, vLLM, DeepSeek, and OpenAI endpoints.
- [x] Implement `InMemoryCosineVectorAdapter` for zero-dependency local runs.
- [x] Implement `QdrantVectorAdapter` for open-source scalable vector search.
- [x] Implement `InMemoryGraphAdapter` with BFS shortest-path and pattern queries.
- [x] Implement `Neo4jGraphAdapter` for open-standard Cypher graph querying.

### Phase 2: RAG, Knowledge Graph & Agent Loop (✅ Completed)
- [x] Implement `RAGService` with BM25 inverted index tokenization and Reciprocal Rank Fusion (RRF).
- [x] Ground RAG directly against `policies/rules/` markdown contracts.
- [x] Implement `KnowledgeGraphService` extracting `(:Rule)-[:BELONGS_TO]->(:Category)` and `(:Rule)-[:ENFORCES]->(:ArchitecturePattern)` relationships.
- [x] Implement `AgentService` autonomous ReAct reasoning loop with dynamic tool dispatching (`search_policy_rules`, `run_repo_audit`, `generate_refactoring_plan`).
- [x] Enforce system prompt guardrails for zero inline comments, anti-corruption layers, and envelope compliance.

### Phase 3: Delivery Interfaces & Open Standards (✅ Completed)
- [x] Implement standardized API envelope (`{meta, data, errors}`) per `api-request-response-structure.md`.
- [x] Implement FastAPI REST API v1 endpoints (`/health`, `/rag/search`, `/rag/index`, `/agent/run`, `/audit/scan`, `/graph/build`, `/graph/query`, `/graph/impact/{rule_id}`).
- [x] Implement CLI entrypoint (`src/api/cli/main.py`) with all subcommands.
- [x] Build production multi-stage `Dockerfile` with non-root security (`appuser:appgroup` UID 10001).
- [x] Create `docker-compose.yml` orchestrating `policy-orchestrator`, `qdrant`, and `neo4j`.
- [x] Ensure all unit and integration test suites pass.

---

### Phase 4: Advanced Capabilities & Production Hardening (⏳ Planned / Upcoming)

#### 4.1 Real-Time Streaming & SSE Agent Telemetry
- [ ] Implement Server-Sent Events (SSE) `/api/v1/agent/stream` endpoint for live streaming token & thought output to web UIs.
- [ ] Add OpenTelemetry distributed span instrumentation directly into `AgentStep` telemetry.

#### 4.2 AST-Safe Code Modification Engine
- [ ] Deepen `RefactorService` with `libcst` (Concrete Syntax Tree) for Python and `tree-sitter` for Go/TypeScript.
- [ ] Automate zero-inline-comment extraction (moving inline comments to top-side blueprint docblocks with AST precision).
- [ ] Implement dry-run unified diff generator with syntax validation before disk write.

#### 4.3 Policy Self-Evolution & Live Web Research
- [ ] Add `internet_search_tool` to Agent using SearXNG / DuckDuckGo for live CVE and RFC cross-checking.
- [ ] Implement self-updating policy proposal engine: Agent evaluates codebase anomalies and proposes updates to `policies/rules/`.

#### 4.4 Distributed Workflows & Event Bus Integration
- [ ] Integrate Temporal / Durable execution worker for long-running repository-wide refactoring sagas.
- [ ] CloudEvents 1.0 Kafka/NATS consumer to trigger audits automatically on Git PR webhooks.

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

## 🧪 Testing & Verification Commands

```bash
# Run all unit and integration test suites
python3 -m unittest discover -s tests -p "test_*.py"

# Run semantic RAG query via CLI
python3 src/api/cli/main.py rag search --query "outbox pattern dual write"

# Run AI policy agent reasoning loop via CLI
python3 src/api/cli/main.py agent "Audit the codebase and identify concurrency risks"

# Launch REST API server
python3 src/api/cli/main.py serve --host 0.0.0.0 --port 8000

# Run via Docker Compose (includes Qdrant & Neo4j)
docker compose up --build -d
```
