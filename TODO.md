# Policy Orchestrator & Master Algorithm Engine Roadmap

This document tracks the comprehensive architecture, completed capabilities, the **1000+ Declarative Agent Catalog**, and the exhaustive roadmap for incorporating all algorithmic knowledge bases from `policies/rules/algos/` into the **Policy Orchestrator and Master Algorithm Engine** (`policies/policy-orchestrator`).

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
4. **Three-Tier Wiring Invariant (Per Algorithm)**:
   - **Tier 1 (In-Code Contract & Pure Logic)**: Strongly-typed Pydantic contract registered in `BUILTIN_ALGORITHM_CONTRACTS` in [`algorithm_catalog.py`](file:///home/btpl-lap-22/live/llm-obs-infra/policies/policy-orchestrator/src/features/code_engine/registry/algorithm_catalog.py), accompanied by pure deterministic Python implementation with zero inline comments in `src/features/code_engine/algos/<category>/`.
   - **Tier 2 (Service Dispatch & CLI Access)**: Dynamic execution wiring in [`code_engine_service.py`](file:///home/btpl-lap-22/live/llm-obs-infra/policies/policy-orchestrator/src/features/code_engine/service/code_engine_service.py) and shorthand command alias in [`src/api/cli/main.py`](file:///home/btpl-lap-22/live/llm-obs-infra/policies/policy-orchestrator/src/api/cli/main.py).
   - **Tier 3 (Delivery & Contracts)**: Role-scoped REST route in dedicated router under `src/api/rest/v1/routers/`, mounted into [`router.py`](file:///home/btpl-lap-22/live/llm-obs-infra/policies/policy-orchestrator/src/api/rest/v1/router.py), documented in [`contracts/openapi/v1.yaml`](file:///home/btpl-lap-22/live/llm-obs-infra/policies/policy-orchestrator/contracts/openapi/v1.yaml), and backed by complete unit tests.
5. **Declarative Agent Scaling (Template for 1000+ Specialized Agents)**:
   - Agents are declared as frozen `AgentManifest` data structures (specifying `agent_id`, `role`, `system_prompt`, `allowed_tools`, and `algorithms`).
   - Zero boilerplate duplication: 1000+ agents can be loaded from YAML manifests or dynamic registries instantly.

---

## 📊 High-Level Algorithm Implementation Status

| Category Source Directory | Total Algos Described | Implemented & Verified | Pending | Status |
| :--- | :---: | :---: | :---: | :---: |
| **`vectorAlgo/`** (Vector Math, Search, Lifecycle, Obs) | 200 | **200** | 0 | 🟢 100% Complete (All 4 Parts Done) |
| **`fileIndexingAndSearching/`** (Search, AST, Diff, CST) | 200 | **50** | 150 | 🟡 25% Complete (Part 1 Done) |
| **`graphs/`** (Traversal, Flow, Temporal, Distributed) | 300+ | **9** | 291+ | 🔴 3% Complete |
| **`knowlageGraph/`** (KG Modeling, Reasoning, GNNs) | 100+ | **0** | 100+ | ⚪ Pending |
| **`glue/`** (Composition Models, L1–L8 Pipeline Contracts) | 8 Specs | **L1 Contracts** | L2–L8 Engines | 🟡 In Progress |
| **TOTALS** | **800+** | **268 Live** | **541+** | **Active Pipeline** |

*Current System Metrics: 268 Algorithms, 288 FastAPI Routes, 262 Documented OpenAPI Paths, 269 CLI Aliases, 348 Automated Passing Tests.*

---

## 🎯 Completed: Vector Algorithms Part 4 (#156–200)

**Vector Algorithm Suite: 100% Complete (200/200)**.

### Sub-Category D1: Retrieval Quality Metrics (#156–167)
- [x] **156. Recall@k (against exact ground truth)** (`ALGO-VEC-OBS-156`) — Fraction of true k-nearest neighbors returned vs brute force top-k.
- [x] **157. Ground-truth sampling (shadow brute force)** (`ALGO-VEC-OBS-157`) — Continuous exact recall sampling on background shadow snapshots.
- [x] **158. Precision@k** (`ALGO-VEC-OBS-158`) — Fraction of top-k results verified relevant to user query.
- [x] **159. Mean Reciprocal Rank (MRR)** (`ALGO-VEC-OBS-159`) — Mean reciprocal rank $1/\text{rank}$ of first relevant result across queries.
- [x] **160. nDCG (normalized discounted cumulative gain)** (`ALGO-VEC-OBS-160`) — Graded relevance ranking metric with logarithmic position discounts.
- [x] **161. Hit rate (success@k)** (`ALGO-VEC-OBS-161`) — Proportion of queries with at least one relevant passage in top-k.
- [x] **162. Relative distance error** (`ALGO-VEC-OBS-162`) — Distance difference ratio between approximate and exact nearest neighbors.
- [x] **163. LLM-as-judge relevance evaluation** (`ALGO-VEC-OBS-163`) — Prompted LLM evaluator scoring query-passage relevance and explanation.
- [x] **164. Golden query set regression testing** (`ALGO-VEC-OBS-164`) — Synthetic/curated benchmark regression gate before index or model promotions.
- [x] **165. Online implicit feedback** (`ALGO-VEC-OBS-165`) — Click-through rate, dwell time, and copy action monitoring for result quality.
- [x] **166. Interleaving experiments** (`ALGO-VEC-OBS-166`) — Team-draft interleaving of two retrieval rankers in single live streams.
- [x] **167. Faithfulness and groundedness (RAG evaluation)** (`ALGO-VEC-OBS-167`) — Entailment and hallucination checking against retrieved context.

### Sub-Category D2: Embedding Space and Distribution Drift (#168–177)
- [x] **168. Centroid shift** (`ALGO-VEC-OBS-168`) — Tracking global and per-cluster center displacement over time.
- [x] **169. Maximum Mean Discrepancy (MMD)** (`ALGO-VEC-OBS-169`) — Kernel two-sample test measuring distribution drift between vector sets.
- [x] **170. PSI and KS tests on projections** (`ALGO-VEC-OBS-170`) — Population Stability Index and Kolmogorov-Smirnov statistical drift tests.
- [x] **171. Similarity score distribution monitoring** (`ALGO-VEC-OBS-171`) — Histogram and percentile tracking of top-1/top-k cosine scores.
- [x] **172. Vector norm distribution** (`ALGO-VEC-OBS-172`) — Norm anomalies detection signaling unnormalized vectors or token corruption.
- [x] **173. Partition and cluster balance** (`ALGO-VEC-OBS-173`) — Tracking entropy and Gini coefficient of partition cluster sizes.
- [x] **174. Hubness measurement (k-occurrence skew)** (`ALGO-VEC-OBS-174`) — Identifying bad hub vectors that appear inordinately often in top-k results.
- [x] **175. Intrinsic dimensionality estimation** (`ALGO-VEC-OBS-175`) — Two-NN and MLE dimension estimation measuring embedding space collapse.
- [x] **176. Outlier detection on embeddings** (`ALGO-VEC-OBS-176`) — Isolation forests and k-NN distance thresholding for poisoned vectors.
- [x] **177. Query out-of-distribution (OOD) detection** (`ALGO-VEC-OBS-177`) — Mahalanobis and cosine distance gating against training/index domain.

### Sub-Category D3: Performance, Resources, and Health (#178–190)
- [x] **178. Latency histograms and percentiles** (`ALGO-VEC-OBS-178`) — p50, p95, p99, p99.9 latency telemetry per pipeline phase.
- [x] **179. RED and USE methods** (`ALGO-VEC-OBS-179`) — Rate, Errors, Duration + Utilization, Saturation, Errors monitoring.
- [x] **180. SLOs and error-budget burn rate** (`ALGO-VEC-OBS-180`) — Error budget consumption alerts with multi-window multi-burn rates.
- [x] **181. Distributed tracing (OpenTelemetry)** (`ALGO-VEC-OBS-181`) — End-to-end W3C trace context spans across embed, search, rerank, and LLM.
- [x] **182. Freshness lag (ingest-to-searchable)** (`ALGO-VEC-OBS-182`) — End-to-end duration from source mutation to searchable index state.
- [x] **183. Graph index health** (`ALGO-VEC-OBS-183`) — HNSW/DiskANN disconnected component detection, out-degree distribution, diameter.
- [x] **184. Tombstone ratio** (`ALGO-VEC-OBS-184`) — Soft-deleted record proportion alerting compaction and rebuild triggers.
- [x] **185. Cache hit ratio and memory pressure** (`ALGO-VEC-OBS-185`) — Vector cache eviction rates, hit/miss ratios, working set fit.
- [x] **186. Capacity planning with Little's Law** (`ALGO-VEC-OBS-186`) — Concurrency = Arrival Rate $\times$ Latency capacity provisioning.
- [x] **187. Consumer lag (stream backlog)** (`ALGO-VEC-OBS-187`) — Kafka/WAL offset distance between producer write and index consumer.
- [x] **188. Cardinality-safe metric labels** (`ALGO-VEC-OBS-188`) — Prometheus label sanitization preventing time-series explosions.
- [x] **189. Anomaly detection on metrics** (`ALGO-VEC-OBS-189`) — Z-score, Holt-Winters, and rolling standard deviation metric tripwires.
- [x] **190. Quantile sketches (t-digest, DDSketch)** (`ALGO-VEC-OBS-190`) — Mergeable bounded-memory streaming quantile estimators.

### Sub-Category D4: Debugging, Lineage, and Economics (#191–200)
- [x] **191. Query explain (per-stage breakdown)** (`ALGO-VEC-OBS-191`) — Execution timeline detailing filter pruning, candidate counts, distance ops.
- [x] **192. Retrieval trace logging with sampling** (`ALGO-VEC-OBS-192`) — Structured query/result payload capture with privacy scrubbing and rate limits.
- [x] **193. Embedding-space visualization** (`ALGO-VEC-OBS-193`) — UMAP and t-SNE 2D/3D projection maps for semantic inspections.
- [x] **194. Failure clustering** (`ALGO-VEC-OBS-194`) — HDBSCAN clustering on low-score/failed queries to isolate blind spots.
- [x] **195. Canary queries and synthetic probes** (`ALGO-VEC-OBS-195`) — Continuous synthetic probe injections verifying alive serving state.
- [x] **196. Shadow traffic comparison** (`ALGO-VEC-OBS-196`) — Live mirroring of production requests to candidate index versions.
- [x] **197. Data lineage** (`ALGO-VEC-OBS-197`) — Full provenance tracking: raw document $\to$ chunker $\to$ embedding model $\to$ segment.
- [x] **198. Reconciliation checks** (`ALGO-VEC-OBS-198`) — Periodic cross-system audits verifying database record count matches vector index.
- [x] **199. Cost per query and per item** (`ALGO-VEC-OBS-199`) — Token consumption, GPU hours, and infrastructure cost accounting per tenant.
- [x] **200. Feedback loop into improvement** (`ALGO-VEC-OBS-200`) — Closed-loop pipeline routing observability findings to re-embedding and tuning.

---

## 🗺️ Master Category Inventory & Roadmap (All Folders)

### 1. `policies/rules/algos/vectorAlgo/` (200 Total Algorithms)
- ✅ **Part 1: Transformation & Normalization (#1–50)**:
  - 50 algorithms live: `ALGO-VEC-TRFM-01` to `ALGO-VEC-TRFM-50`.
  - Byte-pair tokenization, embeddings pooling, Matryoshka slicing, whitening, PCA, UMAP, scalar & product quantization (PQ, SQ, RVQ, IVFPQ), sparse lexical projection.
- ✅ **Part 2: Search & Indexing (#51–110)**:
  - 60 algorithms live: `ALGO-VEC-SRCH-51` to `ALGO-VEC-SRCH-110` (including `ALGO-VEC-FLTR-80` to `84`).
  - Brute force, k-d trees, Ball trees, Annoy random projection, IVF, HNSW, DiskANN, Vamana, LSH, pre/post/iterative filtering, hybrid lexical-dense RRF, ColBERT MaxSim, HyDE, two-stage cascades, hedged routing.
- ✅ **Part 3: Update and Lifecycle Management (#111–155)**:
  - 45 algorithms live: `ALGO-VEC-UPD-111` to `ALGO-VEC-UPD-155`.
  - Stable IDs, WAL mutations, Fresh buffer, LSM segment compaction, tombstone deletions, HNSW edge repair, blue-green index swaps, CDC, outbox pattern, idempotent versions, Raft consensus, quorum R/W, version vectors.
- ✅ **Part 4: Observability, Drift, and Metrics (#156–200)**:
  - 45 algorithms live: `ALGO-VEC-OBS-156` to `ALGO-VEC-OBS-200`.
  - Quality metrics (Recall, Precision, MRR, nDCG, HitRate, RAG faithfulness), drift detection (Centroid shift, MMD, PSI, KS tests, Hubness, Intrinsic dim, OOD), health/performance (RED, USE, SLO burn, HNSW graph health, tombstone ratio, Kafka consumer lag, t-digest), and debugging (Query explain, trace logging, failure clustering, shadow traffic, data lineage, cost accounting, closed-loop feedback).

---

### 2. `policies/rules/algos/fileIndexingAndSearching/` (200 Total Algorithms)
Focuses on codebase indexing, syntax-tree transformation, fuzzy search, and verified diff application.

- 🟢 **Part 1: Bulk Search, String Matching, Regex (#1–50)**:
  - **100% Complete (50/50 Live)**: `ALGO-SRCH-01` to `ALGO-SRCH-15`, `ALGO-OBS-16` to `ALGO-OBS-21`, `ALGO-UPD-22` to `ALGO-UPD-24`, and `ALGO-SRCH-25` to `ALGO-SRCH-50`.
  - Recursive walk, work-stealing, git-aware, glob matcher, binary classifier, MIME prober, size bouncer, codegen detector, SIMD memchr, Aho-Corasick, lazy DFA, chunk scanner, context collector, mmap scanner, Wu-Manber, Z-algorithm, Levenshtein DP distance, Myers bit-parallel, Levenshtein automaton, BK-tree, MinHash/Jaccard, fzf fuzzy scorer, regex parser, Thompson NFA, Pike VM, safe backtracking regex, subset DFA, lazy hybrid DFA, literal extraction, reverse inner optimizer, Hyperscan regex set, ReDoS protection, inverted index, trigram inverted index, positional trigram offset index, sparse n-grams, suffix array (SA-IS), Kasai LCP array, suffix automaton (DAWG), Burrows-Wheeler Transform (BWT) & LF-mapping.
- ⏳ **Part 2: Index Structures & Structural Symbol Search (#51–100)**:
  - FM-index, Patricia Radix Tree, FST (Finite State Transducers), B+ trees, Roaring Bitmaps, Galloping intersection, Block-Max WAND, SCIP/LSIF code intelligence, Call Graph, CFG, Static Single Assignment (SSA), Dataflow worklist, Taint analysis, CodeQL Datalog rules.
- ⏳ **Part 3: Vector Retrieval, Syntax Trees, Text Buffers, Diff (#101–150)**:
  - AST-aware chunking, code embeddings, piece-table text buffers, rope data structures, Myers diff, patience diff, GumTree AST diff, tree edit distance (Zhang-Shasha), syntax-directed refactoring.
- ⏳ **Part 4: Diff Refinement, Safe Application & LLM Edits (#151–200)**:
  - Precondition hash gating, semantic AST patch reconciliation, Zero-Inline-Comment extractors, multi-file atomic transactions, rollback recovery, lint boundary enforcement.

---

### 3. `policies/rules/algos/graphs/` (300+ Total Algorithms)
Focuses on deep graph analytics, topological traversal, dynamic graphs, and distributed GNN processing.

- 🟡 **Basic Implemented**:
  - 9 algorithms live: `ALGO-GRAPH-01` to `ALGO-GRAPH-09` (BFS, DFS, Dijkstra, A*, Tarjan SCC, Cycle Detection, Bipartite Matching, PageRank, Subgraph Isomorphism).
- ⏳ **Advanced Traversal & Connectivity (#10–50)**:
  - Bellman-Ford, Floyd-Warshall, Johnson's all-pairs shortest paths, Suurballe's disjoint paths, Edmonds-Karp, Dinic's blocking flow, Push-Relabel, Hopcroft-Karp maximum bipartite matching, Blossom general matching.
- ⏳ **Centrality, Communities, & Spectral Methods (#51–150)**:
  - Betweenness centrality (Brandes), Closeness, Eigenvector, Katz centrality, Louvain community detection, Leiden algorithm, Infomap, Girvan-Newman, Spectral clustering via Graph Laplacian, Normalized cuts.
- ⏳ **Dynamic, Streaming, & Temporal Graphs (#151–245)**:
  - Ramalingam-Reps dynamic shortest paths, Pearce-Kelly incremental topological sort, semi-streaming spanners, AGM linear graph sketches, Count-Min sketches for graphs, temporal reachability journeys, delta-temporal motifs, Gather-Apply-Scatter (GAS), Gunrock GPU frontier processing, GraphBLAS linear algebraic formulations.
- ⏳ **Distributed & Subgraph Processing (#246–300+)**:
  - 2D partitioning distributed BFS, Shiloach-Vishkin fast connected components, GHS distributed MST, worst-case optimal joins (Leapfrog Triejoin), AutoMine/GraphPi pattern enumeration, SWeG graph summarization, Benczúr-Karger cut sparsifiers.

---

### 4. `policies/rules/algos/knowlageGraph/` (100+ Total Algorithms)
Focuses on enterprise Knowledge Graph construction, semantic querying, ontology alignment, and GraphRAG.

- ⏳ **Section 1: Modeling, Storage, and Construction**:
  - RDF/OWL triple stores, Property Graphs, Entity Extraction (NER), Relation Extraction (RE), Coreference resolution, Entity linking, Knowledge fusion, Canonicalization.
- ⏳ **Section 2: Querying, Graph Algorithms, and Reasoning**:
  - openCypher parsing, SPARQL graph pattern matching, Datalog rule engines, OWL Description Logic reasoners, Transitive closure engines, Multi-hop path reasoning.
- ⏳ **Section 3: Embeddings & Graph Machine Learning**:
  - TransE, RotatE, ComplEx, DistMult knowledge graph embeddings, Node2Vec, DeepWalk, Graph Convolutional Networks (GCN), Graph Attention Networks (GAT), Inductive representation learning (GraphSAGE).
- ⏳ **Section 4: Knowledge Graphs + LLM Operations & Observability**:
  - Subgraph extraction for LLM prompt augmentation, GraphRAG community walk summarization, Cypher/SPARQL generation verification, hallucination detection via factual graph checks.

---

### 5. `policies/rules/algos/glue/` (Execution & Composition Layer)
Focuses on the declarative execution engine that wires any arbitrary chain of algorithms together automatically.

- ✅ **Contracts-L1**: Master metadata, purity, determinism, idempotency, and complexity schema definitions (implemented in `AlgorithmContract`).
- ⏳ **Composition-Models-L2**: Sequential, branching, parallel, and speculative algorithm composition DAGs.
- ⏳ **Automatic-Composition-L3**: Type-driven automatic algorithm pipeline synthesizers based on input/output schemas.
- ⏳ **Execution-Control-L4**: Cancellation tokens, timeouts, resource limits, and circuit breakers.
- ⏳ **Scope-and-Data-Flow-L5**: Dynamic memory arenas, zero-copy buffer passing between algorithms.
- ⏳ **Safety-and-Verification-L6**: Invariant formal checking, taint tracking, and precondition guards.
- ⏳ **Matching-Data-Binding-L7**: Metavariable capture, structural pattern binding across algorithm inputs.
- ⏳ **Lang-Ref-L8**: Declarative pipeline DSL for algorithm workflows.

---

## 🛠️ Implementation Protocol & Daily Checklist

When starting a new batch of algorithms:

1. **Strict Zero-Inline-Comment Doctrine**: Code files must contain zero inline comments inside function bodies or methods. Blueprints, complexity analysis, and pre/postconditions must reside in top-level module docstrings.
2. **Deterministic Naming Conventions**:
   - Files: `src/features/code_engine/algos/<category>/<category>_algo_<name>.py`
   - Contract IDs: `ALGO-<CATEGORY>-<NUMBER>`
   - CLI Aliases: `<cat>-<name>` in `src/api/cli/main.py`
3. **Cascading Git Submodule Push**:
   - Push commit in `policies/policy-orchestrator` (`origin main`).
   - Push submodule update in `policies` (`origin main`).
   - Push submodule update in root `llm-obs-infra` (`origin main`).
