# Policy Orchestrator (`policy-orchestrator`)

A high-performance Python package conforming to the **Contract-First & Pure Data-Driven Architecture** specified in [`api-structure.md`](file:///home/btpl-lap-22/live/llm-obs-infra/policies/rules/folderStructure/api-structure.md).

---

## 🎯 Purpose & Capabilities

- **56 Production Algorithm Engines:** Complete suite of Graph, Vector (Preprocessing + Search & Indexing), Search, Observability, and Update algorithms with unified interfaces, strict schema validation, and deterministic execution.
- **3-Tier Command Architecture:** Seamless interaction via **Normal Commands** (human-friendly aliases for beginners), **Developer Commands** (CLI power tools & catalog IDs for CI/CD), and **Code Commands** (REST API & Python SDK for services).
- **Repository Invariant Auditing (`audit`):** Multi-vector static analysis detecting naked sleeps, race conditions, SQL injection risks, unsafe deserializers, deep `OFFSET` pagination, and Redis blocking commands.
- **Safe Batch Refactoring (`refactor` / `patch`):** Deterministic, dry-run-verified search-and-replace across multi-language codebases (Go, TypeScript, JavaScript, Python, SQL, Prisma) using Concrete Syntax Tree (CST) analysis.
- **RAG & Knowledge Graph Engine (`rag` / `graph`):** Grounded semantic retrieval across policy rules and Cypher-compatible knowledge graph extraction.

---

## ⚡ 3-Tier Command System

Every one of the 56 algorithms supports three access tiers designed for different audiences and workflows:

| Tier | Target Audience | Syntax Style | Primary Use Case | Output Format |
|---|---|---|---|---|
| **Tier 1: Normal Command** | Beginners, End-Users, Quick CLI usage | `policy-orchestrator run <alias> [payload]` | Interactive terminal work, intuitive recall, auto-complete | Plain text header + full formatted JSON |
| **Tier 2: Developer Command** | Engineers, CI/CD, Scripting | `policy-orchestrator exec <ALGO-ID> [payload]`<br>or dedicated tool: `search`, `scan`, `outline`, etc. | DevOps pipelines, precise catalog verification, shell tooling | Raw JSON or specialized terminal tables |
| **Tier 3: Code Command** | Microservices, Python SDK, Agents | `POST /api/v1/algos/...`<br>`CodeEngineService.execute_algorithm()` | Application backend integration, automated workflows | Enterprise envelope (`{success, statusCode, data, errors, meta}`) |

### Discovering & Running Commands

```bash
# 1. List all 42 algorithms with plain-English descriptions
policy-orchestrator list

# 2. Filter list by category (graph, vector, search, observability, update)
policy-orchestrator list --category graph

# 3. Run any algorithm using its human-friendly alias (shows schema hint if payload omitted)
policy-orchestrator run dijkstra

# 4. Run with an inline JSON payload
policy-orchestrator run bfs '{"graph": {"A":["B","C"],"B":["D"],"C":[],"D":[]}, "start_node": "A"}'

# 5. Enable Shell Tab-Autocomplete (Bash, Zsh, Fish)
eval "$(policy-orchestrator completion bash)"
```

---

## 📚 Complete 42-Algorithm Reference

### 1. Graph Algorithms (9 Algorithms)

| # | Algo ID | Normal Command (Beginner) | Developer Command (CLI Power User) | Code Command (REST API & Python SDK) | What It Does (Plain English) |
|---|---|---|---|---|---|
| 1 | `ALGO-GRAPH-01` | `policy-orchestrator run bfs` | `policy-orchestrator exec ALGO-GRAPH-01` | `POST /api/v1/algos/graph/bfs` | Breadth-first graph walk (layer by layer like ripples in water) |
| 2 | `ALGO-GRAPH-02` | `policy-orchestrator run dfs` | `policy-orchestrator exec ALGO-GRAPH-02` | `POST /api/v1/algos/graph/dfs` | Depth-first graph walk (deepest path first before backtracking) |
| 3 | `ALGO-GRAPH-03` | `policy-orchestrator run dijkstra`<br>*(or `shortest-path`)* | `policy-orchestrator exec ALGO-GRAPH-03` | `POST /api/v1/algos/graph/dijkstra` | Finds lowest-cost path between two points (GPS routing) |
| 4 | `ALGO-GRAPH-04` | `policy-orchestrator run astar` | `policy-orchestrator exec ALGO-GRAPH-04` | `POST /api/v1/algos/graph/astar` | Smart heuristic-guided route finder to reach targets faster |
| 5 | `ALGO-GRAPH-05` | `policy-orchestrator run pagerank` | `policy-orchestrator exec ALGO-GRAPH-05` | `POST /api/v1/algos/graph/pagerank` | Scores nodes by incoming links from other important nodes |
| 6 | `ALGO-GRAPH-06` | `policy-orchestrator run centrality` | `policy-orchestrator exec ALGO-GRAPH-06` | `POST /api/v1/algos/graph/degree-centrality` | Identifies the most connected hub node in a network |
| 7 | `ALGO-GRAPH-07` | `policy-orchestrator run components` | `policy-orchestrator exec ALGO-GRAPH-07` | `POST /api/v1/algos/graph/connected-components` | Finds disconnected groups or sub-clusters in a graph |
| 8 | `ALGO-GRAPH-08` | `policy-orchestrator run tarjan` | `policy-orchestrator exec ALGO-GRAPH-08` | `POST /api/v1/algos/graph/tarjan-scc` | Detects circular dependency loops and potential deadlocks |
| 9 | `ALGO-GRAPH-09` | `policy-orchestrator run pattern-match` | `policy-orchestrator exec ALGO-GRAPH-09` | `POST /api/v1/algos/graph/subgraph-match` | Checks if a target sub-graph pattern exists in a larger network |

---

### 2. Vector Algorithms (38 Algorithms)

#### A. Preprocessing & Normalization (9 Algorithms)
| # | Algo ID | Normal Command (Beginner) | Developer Command (CLI Power User) | Code Command (REST API & Python SDK) | What It Does (Plain English) |
|---|---|---|---|---|---|
| 10 | `ALGO-VEC-01` | `policy-orchestrator run normalize` | `policy-orchestrator exec ALGO-VEC-01` | `POST /api/v1/algos/vector/normalize` | Scales vectors to standard length 1.0 (L2 unit norm) |
| 11 | `ALGO-VEC-02` | `policy-orchestrator run mean-center` | `policy-orchestrator exec ALGO-VEC-02` | `POST /api/v1/algos/vector/center` | Shifts numbers so dataset average is 0 (removes global bias) |
| 12 | `ALGO-VEC-03` | `policy-orchestrator run scale` | `policy-orchestrator exec ALGO-VEC-03` | `POST /api/v1/algos/vector/scale` | Fits numbers into standard 0–1 or standard-deviation units |
| 13 | `ALGO-VEC-04` | `policy-orchestrator run token-pool` | `policy-orchestrator exec ALGO-VEC-04` | `POST /api/v1/algos/vector/pool` | Condenses token embeddings into one sentence vector (mean/max) |
| 14 | `ALGO-VEC-05` | `policy-orchestrator run chunk` | `policy-orchestrator exec ALGO-VEC-05` | `POST /api/v1/algos/vector/chunk` | Splits long documents at topic transitions, not just line counts |
| 15 | `ALGO-VEC-06` | `policy-orchestrator run quantize` | `policy-orchestrator exec ALGO-VEC-06` | `POST /api/v1/algos/vector/quantize/scalar` | Compresses FP32 vectors to INT8/INT4 to save memory |
| 16 | `ALGO-VEC-07` | `policy-orchestrator run binary-quantize` | `policy-orchestrator exec ALGO-VEC-07` | `POST /api/v1/algos/vector/quantize/binary` | Shrinks vector values into 1s and 0s for fast bitwise search |
| 17 | `ALGO-VEC-08` | `policy-orchestrator run slice` | `policy-orchestrator exec ALGO-VEC-08` | `POST /api/v1/algos/vector/slice` | Trims big vectors to smaller dimensions (Matryoshka learning) |
| 18 | `ALGO-VEC-09` | `policy-orchestrator run layer-norm` | `policy-orchestrator exec ALGO-VEC-09` | `POST /api/v1/algos/vector/layer-norm` | Stabilizes vector distributions across AI model layers |

#### B. Vector Search & Indexing (29 Algorithms — #51 to #79)
| # | Algo ID | Normal Command (Beginner) | Developer Command (CLI Power User) | Code Command (REST API & Python SDK) | What It Does (Plain English) |
|---|---|---|---|---|---|
| 19 | `ALGO-VEC-SRCH-51` | `policy-orchestrator run vec-gemm` | `policy-orchestrator exec ALGO-VEC-SRCH-51` | `POST /api/v1/algos/vector-search/gemm` | Exact nearest neighbor search using matrix multiplication |
| 20 | `ALGO-VEC-SRCH-52` | `policy-orchestrator run vec-simd` | `policy-orchestrator exec ALGO-VEC-SRCH-52` | `POST /api/v1/algos/vector-search/simd-dist` | Hardware-vectorized SIMD chunked distance kernels |
| 21 | `ALGO-VEC-SRCH-53` | `policy-orchestrator run vec-topk` | `policy-orchestrator exec ALGO-VEC-SRCH-53` | `POST /api/v1/algos/vector-search/topk` | Heap-based bounded top-k candidate maintainer |
| 22 | `ALGO-VEC-SRCH-54` | `policy-orchestrator run vec-radix` | `policy-orchestrator exec ALGO-VEC-SRCH-54` | `POST /api/v1/algos/vector-search/radix-topk` | Linear-time bucket radix top-k selection |
| 23 | `ALGO-VEC-SRCH-55` | `policy-orchestrator run vec-early-abandon` | `policy-orchestrator exec ALGO-VEC-SRCH-55` | `POST /api/v1/algos/vector-search/early-abandon` | Early distance calculation cutoff on threshold breach |
| 24 | `ALGO-VEC-SRCH-56` | `policy-orchestrator run vec-pivot` | `policy-orchestrator exec ALGO-VEC-SRCH-56` | `POST /api/v1/algos/vector-search/pivot-prune` | Triangle-inequality pruning using reference pivots |
| 25 | `ALGO-VEC-SRCH-57` | `policy-orchestrator run vec-kdtree` | `policy-orchestrator exec ALGO-VEC-SRCH-57` | `POST /api/v1/algos/vector-search/kdtree` | Orthogonal axis KD-tree spatial partitioning index |
| 26 | `ALGO-VEC-SRCH-58` | `policy-orchestrator run vec-balltree` | `policy-orchestrator exec ALGO-VEC-SRCH-58` | `POST /api/v1/algos/vector-search/ball-tree` | Hyperspherical metric Ball-tree index |
| 27 | `ALGO-VEC-SRCH-59` | `policy-orchestrator run vec-vptree` | `policy-orchestrator exec ALGO-VEC-SRCH-59` | `POST /api/v1/algos/vector-search/vptree` | Concentric vantage-point shell metric tree |
| 28 | `ALGO-VEC-SRCH-60` | `policy-orchestrator run vec-rpforest` | `policy-orchestrator exec ALGO-VEC-SRCH-60` | `POST /api/v1/algos/vector-search/rp-forest` | Annoy-style random projection hyperplane forest |
| 29 | `ALGO-VEC-SRCH-61` | `policy-orchestrator run vec-ivf` | `policy-orchestrator exec ALGO-VEC-SRCH-61` | `POST /api/v1/algos/vector-search/ivf` | Voronoi inverted file index with cluster routing |
| 30 | `ALGO-VEC-SRCH-62` | `policy-orchestrator run vec-ivfpq` | `policy-orchestrator exec ALGO-VEC-SRCH-62` | `POST /api/v1/algos/vector-search/ivf-pq` | Inverted file index with Product Quantization (ADC) |
| 31 | `ALGO-VEC-SRCH-63` | `policy-orchestrator run vec-nprobe` | `policy-orchestrator exec ALGO-VEC-SRCH-63` | `POST /api/v1/algos/vector-search/nprobe-tune` | Automated Pareto frontier nprobe parameter tuner |
| 32 | `ALGO-VEC-SRCH-64` | `policy-orchestrator run vec-imi` | `policy-orchestrator exec ALGO-VEC-SRCH-64` | `POST /api/v1/algos/vector-search/imi` | Fine dual-codebook Inverted Multi-Index |
| 33 | `ALGO-VEC-SRCH-65` | `policy-orchestrator run vec-nsw` | `policy-orchestrator exec ALGO-VEC-SRCH-65` | `POST /api/v1/algos/vector-search/nsw` | Navigable Small World (NSW) proximity graph index & search |
| 34 | `ALGO-VEC-SRCH-66` | `policy-orchestrator run vec-hnsw-search` | `policy-orchestrator exec ALGO-VEC-SRCH-66` | `POST /api/v1/algos/vector-search/hnsw-search` | Hierarchical NSW multilayer beam search |
| 35 | `ALGO-VEC-SRCH-67` | `policy-orchestrator run vec-hnsw-insert` | `policy-orchestrator exec ALGO-VEC-SRCH-67` | `POST /api/v1/algos/vector-search/hnsw-insert` | HNSW scale-free layer insertion with neighbor heuristic |
| 36 | `ALGO-VEC-SRCH-68` | `policy-orchestrator run vec-beam` | `policy-orchestrator exec ALGO-VEC-SRCH-68` | `POST /api/v1/algos/vector-search/beam-search` | Bounded beam search on proximity graphs |
| 37 | `ALGO-VEC-SRCH-69` | `policy-orchestrator run vec-vamana` | `policy-orchestrator exec ALGO-VEC-SRCH-69` | `POST /api/v1/algos/vector-search/vamana` | Vamana/DiskANN two-pass proximity graph index |
| 38 | `ALGO-VEC-SRCH-70` | `policy-orchestrator run vec-robust-prune` | `policy-orchestrator exec ALGO-VEC-SRCH-70` | `POST /api/v1/algos/vector-search/robust-prune` | RobustPrune alpha diversity filter for neighbor graphs |
| 39 | `ALGO-VEC-SRCH-71` | `policy-orchestrator run vec-nsg` | `policy-orchestrator exec ALGO-VEC-SRCH-71` | `POST /api/v1/algos/vector-search/nsg` | Navigating Spreading-out Graph with MRNG pruning |
| 40 | `ALGO-VEC-SRCH-72` | `policy-orchestrator run vec-cagra` | `policy-orchestrator exec ALGO-VEC-SRCH-72` | `POST /api/v1/algos/vector-search/cagra` | GPU-optimized fixed-degree regular graph |
| 41 | `ALGO-VEC-SRCH-73` | `policy-orchestrator run vec-entry` | `policy-orchestrator exec ALGO-VEC-SRCH-73` | `POST /api/v1/algos/vector-search/entry-point` | Medoid & multi-seed entry-point selection |
| 42 | `ALGO-VEC-SRCH-74` | `policy-orchestrator run vec-repair` | `policy-orchestrator exec ALGO-VEC-SRCH-74` | `POST /api/v1/algos/vector-search/connectivity-repair` | Graph reachability audit & island repair |
| 43 | `ALGO-VEC-SRCH-75` | `policy-orchestrator run vec-filtered-diskann` | `policy-orchestrator exec ALGO-VEC-SRCH-75` | `POST /api/v1/algos/vector-search/filtered-diskann` | Label-constrained in-index graph traversal |
| 44 | `ALGO-VEC-SRCH-76` | `policy-orchestrator run vec-spann` | `policy-orchestrator exec ALGO-VEC-SRCH-76` | `POST /api/v1/algos/vector-search/spann` | SPANN memory-disk hybrid with boundary duplication |
| 45 | `ALGO-VEC-SRCH-77` | `policy-orchestrator run vec-lsh-hyperplane` | `policy-orchestrator exec ALGO-VEC-SRCH-77` | `POST /api/v1/algos/vector-search/lsh-hyperplane` | Random-hyperplane cosine Locality-Sensitive Hashing |
| 46 | `ALGO-VEC-SRCH-78` | `policy-orchestrator run vec-lsh-multiprobe` | `policy-orchestrator exec ALGO-VEC-SRCH-78` | `POST /api/v1/algos/vector-search/lsh-multiprobe` | Multi-probe perturbation sequence LSH |
| 47 | `ALGO-VEC-SRCH-79` | `policy-orchestrator run vec-e2lsh` | `policy-orchestrator exec ALGO-VEC-SRCH-79` | `POST /api/v1/algos/vector-search/e2lsh` | Exact 2-stable Gaussian L2 Locality-Sensitive Hashing |

---

### 3. Search Algorithms (15 Algorithms)

| # | Algo ID | Normal Command (Beginner) | Developer Command (CLI Power User) | Code Command (REST API & Python SDK) | What It Does (Plain English) |
|---|---|---|---|---|---|
| 48 | `ALGO-SRCH-01` | `policy-orchestrator run file-walk` | `policy-orchestrator scan [dir]`<br>`policy-orchestrator exec ALGO-SRCH-01` | `POST /api/v1/algos/search/walk` | Lists every file in folder tree recursively |
| 49 | `ALGO-SRCH-02` | `policy-orchestrator run git-walk` | `policy-orchestrator exec ALGO-SRCH-02` | `POST /api/v1/algos/search/work-stealing-walk` | Parallel file search across CPU cores with work-stealing |
| 50 | `ALGO-SRCH-03` | `policy-orchestrator run git-ignore-walk` | `policy-orchestrator exec ALGO-SRCH-03` | `POST /api/v1/algos/search/git-aware-walk` | Lists files while automatically skipping `.gitignore` patterns |
| 51 | `ALGO-SRCH-04` | `policy-orchestrator run glob` | `policy-orchestrator exec ALGO-SRCH-04` | `POST /api/v1/algos/search/glob-match` | Matches paths with wildcard patterns (e.g. `**/*.py`) |
| 52 | `ALGO-SRCH-05` | `policy-orchestrator run trigram` | `policy-orchestrator exec ALGO-SRCH-05` | `POST /api/v1/algos/search/trigram-index` | 3-letter inverted index for ultra-fast fuzzy substring search |
| 53 | `ALGO-SRCH-06` | `policy-orchestrator run mmap-scan` | `policy-orchestrator exec ALGO-SRCH-06` | `POST /api/v1/algos/search/mmap-scan` | Memory-mapped zero-copy scan of gigabyte-sized files |
| 54 | `ALGO-SRCH-07` | `policy-orchestrator run stream-scan` | `policy-orchestrator exec ALGO-SRCH-07` | `POST /api/v1/algos/search/streaming-chunk-scan` | Low-RAM stream scanner for large files |
| 55 | `ALGO-SRCH-08` | `policy-orchestrator run size-filter` | `policy-orchestrator exec ALGO-SRCH-08` | `POST /api/v1/algos/search/size-line-check` | Skips files that exceed byte size or line count limits |
| 56 | `ALGO-SRCH-09` | `policy-orchestrator run regex-scan` | `policy-orchestrator exec ALGO-SRCH-09` | `POST /api/v1/algos/search/lazy-dfa` | Fast regex matching without backtracking catastrophic delays |
| 57 | `ALGO-SRCH-10` | `policy-orchestrator run snippet` | `policy-orchestrator exec ALGO-SRCH-10` | `POST /api/v1/algos/search/context-snippet` | Fetches lines before & after match for rich display |
| 58 | `ALGO-SRCH-11` | `policy-orchestrator run byte-search` | `policy-orchestrator exec ALGO-SRCH-11` | `POST /api/v1/algos/search/simd-memchr` | SIMD hardware-accelerated single-byte scanning |
| 59 | `ALGO-SRCH-12` | `policy-orchestrator run is-binary` | `policy-orchestrator exec ALGO-SRCH-12` | `POST /api/v1/algos/search/binary-check` | Checks if a file is binary or human-readable text |
| 60 | `ALGO-SRCH-13` | `policy-orchestrator run content-type` | `policy-orchestrator exec ALGO-SRCH-13` | `POST /api/v1/algos/search/content-type` | Probes file header bytes for MIME type and language |
| 61 | `ALGO-SRCH-14` | `policy-orchestrator run is-generated` | `policy-orchestrator exec ALGO-SRCH-14` | `POST /api/v1/algos/search/generated-code-check` | Flags auto-generated files (protobuf, swagger, etc.) |
| 62 | `ALGO-SRCH-15` | `policy-orchestrator run parallel-walk` | `policy-orchestrator search <patterns> [dir]`<br>`policy-orchestrator exec ALGO-SRCH-15` | `POST /api/v1/algos/search/aho-corasick`<br>`POST /api/v1/algos/search/scan` | Scans text for multiple search terms simultaneously |

---

### 4. Observability Algorithms (6 Algorithms)

| # | Algo ID | Normal Command (Beginner) | Developer Command (CLI Power User) | Code Command (REST API & Python SDK) | What It Does (Plain English) |
|---|---|---|---|---|---|
| 63 | `ALGO-OBS-16` | `policy-orchestrator run ast-parse` | `policy-orchestrator exec ALGO-OBS-16` | `POST /api/v1/algos/observability/ast` | Parses code into syntax tree representation |
| 64 | `ALGO-OBS-17` | `policy-orchestrator run outline` | `policy-orchestrator outline <file>`<br>`policy-orchestrator exec ALGO-OBS-17` | `POST /api/v1/algos/observability/outline` | Summarizes all classes, methods, and functions in a file |
| 65 | `ALGO-OBS-18` | `policy-orchestrator run extract-comments` | `policy-orchestrator exec ALGO-OBS-18` | `POST /api/v1/algos/observability/span-track` | Pulls out all comments, notes, and byte spans from code |
| 66 | `ALGO-OBS-19` | `policy-orchestrator run no-inline` | `policy-orchestrator lint <file>`<br>`policy-orchestrator exec ALGO-OBS-19` | `POST /api/v1/algos/observability/lint-comments` | Enforces Zero-Inline-Comment doctrine across codebases |
| 67 | `ALGO-OBS-20` | `policy-orchestrator run dep-graph` | `policy-orchestrator deps [dir]`<br>`policy-orchestrator exec ALGO-OBS-20` | `POST /api/v1/algos/observability/dependencies` | Maps module imports and flags circular cycles |
| 68 | `ALGO-OBS-21` | `policy-orchestrator run symbols` | `policy-orchestrator exec ALGO-OBS-21` | `POST /api/v1/algos/observability/symbols` | Resolves symbol scopes and variable definitions |

---

### 5. Update Algorithms (3 Algorithms)

| # | Algo ID | Normal Command (Beginner) | Developer Command (CLI Power User) | Code Command (REST API & Python SDK) | What It Does (Plain English) |
|---|---|---|---|---|---|
| 69 | `ALGO-UPD-22` | `policy-orchestrator run smart-patch` | `policy-orchestrator patch <file> <find> <replace>`<br>`policy-orchestrator exec ALGO-UPD-22` | `POST /api/v1/algos/update/cst-match` | Concrete Syntax Tree (CST) code patcher without syntax errors |
| 70 | `ALGO-UPD-23` | `policy-orchestrator run batch-patch` | `policy-orchestrator exec ALGO-UPD-23` | `POST /api/v1/algos/update/patch` | Multi-file atomic patch with rollback on any failure |
| 71 | `ALGO-UPD-24` | `policy-orchestrator run show-diff` | `policy-orchestrator diff <file> <find> <replace>`<br>`policy-orchestrator exec ALGO-UPD-24` | `POST /api/v1/algos/update/diff` | Generates standard unified GNU context diff (+/-) |

---

## 🏗️ Architecture & Module Structure

```
packages/policy-orchestrator/
├── contracts/
│   └── openapi/
│       └── v1.yaml               # REST API Contract Specification
├── config/
│   ├── default.yaml              # Default configuration values
│   └── env.schema                # Environment variable schema
├── src/
│   ├── api/
│   │   ├── cli/
│   │   │   └── main.py           # Single-entrypoint CLI with 3-tier dispatch
│   │   └── rest/v1/
│   │       ├── router.py         # FastAPI REST Router with standard envelope
│   │       └── envelope.py       # Strict API envelope format
│   ├── domain/
│   │   └── ports/                # Abstract domain interfaces
│   ├── features/
│   │   ├── code_engine/
│   │   │   ├── algos/            # 42 Pure Algorithm Implementations
│   │   │   │   ├── graph/        # 9 Graph algorithms (BFS, DFS, Dijkstra, A*, etc.)
│   │   │   │   ├── vector/       # 9 Vector algorithms (L2 Norm, Scaling, Quantize, etc.)
│   │   │   │   ├── search/       # 15 Search algorithms (Walkers, Trigram, DFA, etc.)
│   │   │   │   ├── observability/# 6 Observability algorithms (AST, Outline, Linter, etc.)
│   │   │   │   └── update/       # 3 Update algorithms (CST Matcher, Patch, Diff)
│   │   │   └── service/          # Algorithm execution & pipeline composer
│   │   ├── audit/                # Invariant scanning domain
│   │   ├── refactor/             # Safe batch refactoring domain
│   │   ├── rag/                  # Semantic policy retrieval domain
│   │   └── agent/                # Autonomous AI agent orchestration
│   └── infra/
│       ├── adapters/             # Database, Vector DB, LLM adapters
│       └── filesystem/           # Safe directory walker
└── tests/
    └── unit/                     # Unit test suites (83+ tests passing)
```

---

## 📜 Architectural Invariants Enforced

- **Zero-Inline-Comment Doctrine:** 100% comment-free function bodies; comprehensive top-level algorithm blueprints.
- **Pure Data-Driven Rules:** Business and security checks declared as data (`AuditRule` records), not procedural code.
- **Envelope Consistency:** All REST API responses conform strictly to `{success, statusCode, data, errors, meta}`.
- **Deterministic Rollback:** All update algorithms support dry-run preview and atomic commit/rollback.
