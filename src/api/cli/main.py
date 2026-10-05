#!/usr/bin/env python3
"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ERGONOMIC POLICY ORCHESTRATOR CLI
================================================================================

1. OVERVIEW & OBJECTIVE:
   Provides a clean, intuitive, Single Responsibility Principle (SRP) compliant CLI
   with consistent argument conventions, beginner-friendly shortcuts, JSON outputs,
   and shell auto-completion generation (bash/zsh/fish).

2. SINGLE RESPONSIBILITY SUBCOMMANDS:
   - `search <patterns> [dir]`: Fast multi-pattern search (ALGO-SRCH-03 + 11 + 14).
   - `scan [dir]`: Recursive repository file tree discovery (ALGO-SRCH-01/02).
   - `outline <file>`: Hierarchical AST symbol tree generator (ALGO-OBS-17 + 21).
   - `lint <file>`: Zero-Inline-Comment doctrine compliance linter (ALGO-OBS-19).
   - `deps [dir]`: Module import dependency graph & cycle detector (ALGO-OBS-20).
   - `diff <file> <find> <replace>`: Unified context diff generator (ALGO-UPD-24).
   - `patch <file> <find> <replace> [--apply]`: AST/CST atomic patcher (ALGO-UPD-22/23).
   - `exec <algo_id> [input_json]`: Direct universal algorithm execution (All 42 algos).
   - `contracts [--category]`: Layer 1 algorithm contract discovery.
   - `compose <algo_ids...>`: Dynamic pipeline execution DAG composer.
   - `completion <bash|zsh|fish>`: Generates shell tab-completion scripts.
   - `algo <action>`: Legacy backwards-compatible unified dispatcher.
   - `audit`: Multi-vector invariant and architecture scanner.
   - `rag`: Grounded semantic policy retrieval.
   - `agent`: Autonomous AI agent execution.
   - `migrate`: Database migrations and catalog seeding.
   - `serve`: FastAPI Uvicorn REST server.

3. ARCHITECTURAL INVARIANTS:
   - Zero-Inline-Comment Doctrine: 100% pure method/function bodies.
   - Standardized Posix Exit Codes: 0 on success, 1 on error/violation.
================================================================================
"""

import sys

ALGO_ALIASES: dict = {
    "bfs": {
        "id": "ALGO-GRAPH-01",
        "algo_name": "BFS Traversal",
        "plain_name": "Level-by-level graph walk",
        "what_it_does": "Visits every node starting from a point, layer by layer — like ripples spreading in water.",
        "example": '{"graph": {"A":["B","C"],"B":["D"],"C":[],"D":[]}, "start_node": "A"}',
        "category": "graph",
    },
    "dfs": {
        "id": "ALGO-GRAPH-02",
        "algo_name": "DFS Traversal",
        "plain_name": "Deep-dive graph walk",
        "what_it_does": "Goes as deep as possible down one path before backtracking — like exploring a maze by hugging one wall.",
        "example": '{"graph": {"A":["B","C"],"B":["D"],"C":[],"D":[]}, "start_node": "A"}',
        "category": "graph",
    },
    "dijkstra": {
        "id": "ALGO-GRAPH-03",
        "algo_name": "Dijkstra Shortest Path",
        "plain_name": "Find cheapest route between two points",
        "what_it_does": "Finds the least-cost path between two nodes in a network — like a GPS choosing the fastest road.",
        "example": '{"graph": {"A":{"B":1,"C":4},"B":{"C":2,"D":5},"C":{"D":1},"D":{}}, "source": "A", "target": "D"}',
        "category": "graph",
    },
    "shortest-path": {
        "id": "ALGO-GRAPH-03",
        "algo_name": "Dijkstra Shortest Path",
        "plain_name": "Find cheapest route between two points",
        "what_it_does": "Finds the least-cost path between two nodes in a network — like a GPS choosing the fastest road.",
        "example": '{"graph": {"A":{"B":1,"C":4},"B":{"C":2,"D":5},"C":{"D":1},"D":{}}, "source": "A", "target": "D"}',
        "category": "graph",
    },
    "astar": {
        "id": "ALGO-GRAPH-04",
        "algo_name": "A* Search",
        "plain_name": "Smart guided route finder",
        "what_it_does": "Finds the fastest path using a hint about the direction of the goal — smarter than plain shortest-path.",
        "example": '{"graph": {"A":{"B":1},"B":{"C":1},"C":{}}, "start": "A", "goal": "C", "heuristic": {"A":2,"B":1,"C":0}}',
        "category": "graph",
    },
    "pagerank": {
        "id": "ALGO-GRAPH-05",
        "algo_name": "PageRank Centrality",
        "plain_name": "Rank nodes by importance",
        "what_it_does": "Scores nodes by how many important nodes point to them — the same idea Google uses to rank web pages.",
        "example": '{"graph": {"A":["B","C"],"B":["C"],"C":["A"]}, "damping": 0.85, "iterations": 100}',
        "category": "graph",
    },
    "centrality": {
        "id": "ALGO-GRAPH-06",
        "algo_name": "Degree Centrality",
        "plain_name": "Who is the most connected node?",
        "what_it_does": "Ranks each node by how many direct connections it has — the more connections, the more central.",
        "example": '{"graph": {"A":["B","C"],"B":["A","C"],"C":["A","B"]}}',
        "category": "graph",
    },
    "components": {
        "id": "ALGO-GRAPH-07",
        "algo_name": "Connected Components",
        "plain_name": "Find isolated groups in a graph",
        "what_it_does": "Finds all groups of nodes that are connected to each other but completely separate from other groups.",
        "example": '{"graph": {"A":["B"],"B":["A"],"C":["D"],"D":["C"],"E":[]}}',
        "category": "graph",
    },
    "tarjan": {
        "id": "ALGO-GRAPH-08",
        "algo_name": "Tarjan SCC",
        "plain_name": "Find circular dependency groups",
        "what_it_does": "Finds groups where every node can reach every other — catches circular imports, deadlock candidates.",
        "example": '{"graph": {"A":["B"],"B":["C"],"C":["A"],"D":["B"]}}',
        "category": "graph",
    },
    "pattern-match": {
        "id": "ALGO-GRAPH-09",
        "algo_name": "Subgraph Isomorphism",
        "plain_name": "Does this pattern exist in the graph?",
        "what_it_does": "Checks whether a small graph pattern exists inside a larger graph — like searching for a shape inside a diagram.",
        "example": '{"graph": {"A":["B","C"],"B":["C"],"C":[]}, "pattern": {"X":["Y"],"Y":[]}}',
        "category": "graph",
    },
    "normalize": {
        "id": "ALGO-VEC-01",
        "algo_name": "L2 Normalization",
        "plain_name": "Scale all vectors to the same size",
        "what_it_does": "Adjusts number lists so each has the same total size — like converting different speeds into directions.",
        "example": '{"vectors": [[1,2,3],[4,5,6]]}',
        "category": "vector",
    },
    "mean-center": {
        "id": "ALGO-VEC-02",
        "algo_name": "Mean Centering",
        "plain_name": "Remove average bias from data",
        "what_it_does": "Shifts all values so the average becomes zero — removes any dataset-wide offset before comparison.",
        "example": '{"vectors": [[1,2,3],[4,5,6]]}',
        "category": "vector",
    },
    "scale": {
        "id": "ALGO-VEC-03",
        "algo_name": "MinMax / ZScore Normalization",
        "plain_name": "Rescale numbers into a standard range",
        "what_it_does": "Squishes all values into 0–1 (minmax) or standard-deviation units (zscore) so they're comparable.",
        "example": '{"vectors": [[1,2,3]], "method": "minmax"}',
        "category": "vector",
    },
    "token-pool": {
        "id": "ALGO-VEC-04",
        "algo_name": "Token Pooling",
        "plain_name": "Collapse many token vectors into one summary",
        "what_it_does": "Combines many small vectors (one per word/token) into a single summary vector using mean, max, or first.",
        "example": '{"token_embeddings": [[0.1,0.2],[0.3,0.4]], "strategy": "mean"}',
        "category": "vector",
    },
    "chunk": {
        "id": "ALGO-VEC-05",
        "algo_name": "Semantic Chunker",
        "plain_name": "Split long text by topic",
        "what_it_does": "Breaks a long document into chunks where each chunk stays on the same topic — not just by word count.",
        "example": '{"sentences": ["Hello world.", "This is a test."], "threshold": 0.8}',
        "category": "vector",
    },
    "quantize": {
        "id": "ALGO-VEC-06",
        "algo_name": "Scalar Quantization",
        "plain_name": "Compress vectors to save memory",
        "what_it_does": "Reduces floating point precision in vectors — dramatically cuts memory use with minimal accuracy loss.",
        "example": '{"vectors": [[1.5,2.5,3.5]], "bits": 8}',
        "category": "vector",
    },
    "binary-quantize": {
        "id": "ALGO-VEC-07",
        "algo_name": "Binary Quantization",
        "plain_name": "Shrink vectors to just 0s and 1s",
        "what_it_does": "Converts each vector value to a single bit — extreme compression for very fast similarity search.",
        "example": '{"vectors": [[0.5,-0.3,1.2,-0.8]]}',
        "category": "vector",
    },
    "slice": {
        "id": "ALGO-VEC-08",
        "algo_name": "Matryoshka Slicing",
        "plain_name": "Trim big vectors to smaller useful sizes",
        "what_it_does": "Cuts a large embedding to smaller sizes (like 128 or 256 dims) that still work well for search.",
        "example": '{"vector": [0.1,0.2,0.3,0.4,0.5,0.6], "dimensions": [2,4]}',
        "category": "vector",
    },
    "layer-norm": {
        "id": "ALGO-VEC-09",
        "algo_name": "Layer Normalization",
        "plain_name": "Stabilize vector values for AI models",
        "what_it_does": "Normalizes values within each individual vector — keeps AI model inputs in a stable, consistent range.",
        "example": '{"vectors": [[1.0,2.0,3.0]]}',
        "category": "vector",
    },
    "file-walk": {
        "id": "ALGO-SRCH-01",
        "algo_name": "Recursive File Walker",
        "plain_name": "List all files in a folder",
        "what_it_does": "Walks through every folder and subfolder and returns a list of every file it finds.",
        "example": '{"root_dir": "."}',
        "category": "search",
    },
    "git-walk": {
        "id": "ALGO-SRCH-02",
        "algo_name": "Work-Stealing Parallel Walker",
        "plain_name": "List files using multiple CPU cores",
        "what_it_does": "Walks directory trees across multiple CPU threads simultaneously — much faster in large repos.",
        "example": '{"root_dir": ".", "num_workers": 4}',
        "category": "search",
    },
    "git-ignore-walk": {
        "id": "ALGO-SRCH-03",
        "algo_name": "Git-Aware Walker",
        "plain_name": "List files respecting .gitignore",
        "what_it_does": "Lists files but automatically skips everything your .gitignore file says to ignore.",
        "example": '{"root_dir": ".", "respect_gitignore": true}',
        "category": "search",
    },
    "glob": {
        "id": "ALGO-SRCH-04",
        "algo_name": "Glob Matcher",
        "plain_name": "Match files by wildcard pattern",
        "what_it_does": "Filters file paths using wildcards like *.py, src/**/*.ts — like a smart filename filter.",
        "example": '{"pattern": "**/*.py", "paths": ["src/main.py","src/test.go"]}',
        "category": "search",
    },
    "trigram": {
        "id": "ALGO-SRCH-05",
        "algo_name": "Trigram Index Search",
        "plain_name": "Fast fuzzy text search using 3-letter chunks",
        "what_it_does": "Builds a 3-letter (trigram) index for extremely fast substring and fuzzy text searches.",
        "example": '{"documents": ["hello world","foo bar"], "query": "hello"}',
        "category": "search",
    },
    "mmap-scan": {
        "id": "ALGO-SRCH-06",
        "algo_name": "Memory-Mapped File Scanner",
        "plain_name": "Scan huge files without loading them fully",
        "what_it_does": "Reads files directly from disk memory — searches gigabyte-sized files instantly without RAM issues.",
        "example": '{"file_path": "src/api/cli/main.py", "pattern": "def handle"}',
        "category": "search",
    },
    "stream-scan": {
        "id": "ALGO-SRCH-07",
        "algo_name": "Streaming Chunk Scanner",
        "plain_name": "Scan large files in small pieces",
        "what_it_does": "Reads files piece-by-piece so even enormous files can be searched without using too much memory.",
        "example": '{"file_path": "src/api/cli/main.py", "pattern": "policy"}',
        "category": "search",
    },
    "size-filter": {
        "id": "ALGO-SRCH-08",
        "algo_name": "Size/Line Bouncer",
        "plain_name": "Skip files that are too big or too long",
        "what_it_does": "Checks if a file exceeds a size or line-count limit before wasting time scanning it.",
        "example": '{"file_path": "src/api/cli/main.py", "max_size_bytes": 1000000, "max_lines": 50000}',
        "category": "search",
    },
    "regex-scan": {
        "id": "ALGO-SRCH-09",
        "algo_name": "Lazy DFA Regex Engine",
        "plain_name": "Search using a regex pattern (no backtracking)",
        "what_it_does": "Runs regular expressions efficiently using a deterministic finite automaton — never hangs on bad patterns.",
        "example": '{"pattern": "def \\\\w+", "text": "def foo(): pass"}',
        "category": "search",
    },
    "snippet": {
        "id": "ALGO-SRCH-10",
        "algo_name": "Context Snippet Collector",
        "plain_name": "Show lines around a match",
        "what_it_does": "Returns the lines before and after a match so you can read results in context, not just the hit line.",
        "example": '{"file_path": "src/api/cli/main.py", "pattern": "def main", "context_lines": 3}',
        "category": "search",
    },
    "byte-search": {
        "id": "ALGO-SRCH-11",
        "algo_name": "SIMD Memchr Byte Search",
        "plain_name": "Ultra-fast single-byte or character search",
        "what_it_does": "Finds a specific byte or character using CPU hardware acceleration — fastest possible byte scan.",
        "example": '{"text": "hello world", "byte_value": 32}',
        "category": "search",
    },
    "is-binary": {
        "id": "ALGO-SRCH-12",
        "algo_name": "Binary File Classifier",
        "plain_name": "Check if a file is binary or text",
        "what_it_does": "Quickly determines whether a file is binary (image, executable) or plain text — so you know if it's readable.",
        "example": '{"file_path": "src/api/cli/main.py"}',
        "category": "search",
    },
    "content-type": {
        "id": "ALGO-SRCH-13",
        "algo_name": "Content-Type Prober",
        "plain_name": "Detect what type of file this is",
        "what_it_does": "Sniffs a file's content to identify its type (Python, JSON, Markdown, etc.) — like a file-type detector.",
        "example": '{"file_path": "src/api/cli/main.py"}',
        "category": "search",
    },
    "is-generated": {
        "id": "ALGO-SRCH-14",
        "algo_name": "Generated Code Classifier",
        "plain_name": "Was this file auto-generated?",
        "what_it_does": "Detects files created by code generators (protobuf, swagger, etc.) that you should never edit by hand.",
        "example": '{"file_path": "src/api/cli/main.py"}',
        "category": "search",
    },
    "parallel-walk": {
        "id": "ALGO-SRCH-15",
        "algo_name": "Aho-Corasick Multi-Pattern Search",
        "plain_name": "Search for many words at once",
        "what_it_does": "Scans text for multiple words simultaneously — much faster than searching one pattern at a time.",
        "example": '{"patterns": ["TODO","FIXME"], "text": "TODO: fix this FIXME"}',
        "category": "search",
    },
    "ast-parse": {
        "id": "ALGO-OBS-16",
        "algo_name": "Tree-Sitter AST Parser",
        "plain_name": "Parse source code into a structured tree",
        "what_it_does": "Converts source code into a tree of functions, classes, and expressions — the foundation for all code analysis.",
        "example": '{"file_path": "src/api/cli/main.py", "language": "python"}',
        "category": "observability",
    },
    "outline": {
        "id": "ALGO-OBS-17",
        "algo_name": "Code Outline Generator",
        "plain_name": "Show a file's structure at a glance",
        "what_it_does": "Extracts all functions, classes, and methods from a file — like a table of contents for source code.",
        "example": '{"file_path": "src/api/cli/main.py"}',
        "category": "observability",
    },
    "extract-comments": {
        "id": "ALGO-OBS-18",
        "algo_name": "Comment Extractor",
        "plain_name": "Pull out every comment and docstring",
        "what_it_does": "Collects every comment, inline note, and docstring from a source file into one list.",
        "example": '{"file_path": "src/api/cli/main.py"}',
        "category": "observability",
    },
    "no-inline": {
        "id": "ALGO-OBS-19",
        "algo_name": "Zero-Inline-Comment Linter",
        "plain_name": "Check for banned inline comments in code",
        "what_it_does": "Flags code that has inline comments — enforces the rule that all docs must be in the file header, not inline.",
        "example": '{"file_path": "src/api/cli/main.py"}',
        "category": "observability",
    },
    "dep-graph": {
        "id": "ALGO-OBS-20",
        "algo_name": "Import Dependency Grapher",
        "plain_name": "Map what each module imports from what",
        "what_it_does": "Builds a graph of all module imports in a codebase and detects circular dependencies that can break builds.",
        "example": '{"directory": "src"}',
        "category": "observability",
    },
    "symbols": {
        "id": "ALGO-OBS-21",
        "algo_name": "Symbol Scope Resolver",
        "plain_name": "Find where variables and functions are defined",
        "what_it_does": "Traces every variable and function name back to where it was defined — for understanding code ownership.",
        "example": '{"file_path": "src/api/cli/main.py"}',
        "category": "observability",
    },
    "smart-patch": {
        "id": "ALGO-UPD-22",
        "algo_name": "CST Matcher / Patcher",
        "plain_name": "Edit code without breaking its structure",
        "what_it_does": "Edits code using the syntax tree so renames and replacements are structure-aware — no accidental breakage.",
        "example": '{"file_path": "src/api/cli/main.py", "find_pattern": "old_name", "replace_text": "new_name", "dry_run": true}',
        "category": "update",
    },
    "batch-patch": {
        "id": "ALGO-UPD-23",
        "algo_name": "Batch Patcher",
        "plain_name": "Edit many files at once safely",
        "what_it_does": "Applies find-and-replace across many files at once with a SHA-256 checksum and rollback on any failure.",
        "example": '{"operations": [{"file_path": "src/api/cli/main.py", "find_pattern": "TODO", "replace_text": "DONE", "is_regex": false}], "dry_run": true}',
        "category": "update",
    },
    "show-diff": {
        "id": "ALGO-UPD-24",
        "algo_name": "Unified Diff Engine",
        "plain_name": "Show exactly what changed between two versions",
        "what_it_does": "Generates a standard unified diff (+/-) showing every line added or removed between two texts.",
        "example": '{"original": "hello world", "modified": "hello earth", "file_path": "test.py"}',
        "category": "update",
    },
    "vec-gemm": {
        "id": "ALGO-VEC-SRCH-51",
        "algo_name": "Brute-Force kNN with GEMM",
        "plain_name": "Exact nearest neighbor search using matrix math",
        "what_it_does": "Scores query against all database vectors in one fast BLAS matrix multiply — the gold standard ground truth.",
        "example": '{"database_vectors": [[1,0],[0,1]], "query_vectors": [[1,0]], "k": 2}',
        "category": "vector",
    },
    "vec-simd": {
        "id": "ALGO-VEC-SRCH-52",
        "algo_name": "SIMD Distance Kernels",
        "plain_name": "Hardware-accelerated vector distance calculator",
        "what_it_does": "Computes L2, dot, cosine, or binary Hamming distance using CPU SIMD vector lanes.",
        "example": '{"vector_a": [1,2,3,4], "vector_b": [1,2,3,5], "metric": "l2"}',
        "category": "vector",
    },
    "vec-topk": {
        "id": "ALGO-VEC-SRCH-53",
        "algo_name": "Heap Top-K Selection",
        "plain_name": "Find the k best items without sorting everything",
        "what_it_does": "Maintains a bounded heap of size k to pick the highest or lowest scoring candidates with low memory.",
        "example": '{"candidates": [{"id": "doc1", "score": 10.5}, {"id": "doc2", "score": 20.0}], "k": 1}',
        "category": "vector",
    },
    "vec-radix": {
        "id": "ALGO-VEC-SRCH-54",
        "algo_name": "Radix / Quickselect Top-K",
        "plain_name": "Ultra-fast bucket partitioning for top scores",
        "what_it_does": "Selects top-k scores in linear time without sorting, inspired by GPU radix selection algorithms.",
        "example": '{"scores": [10.0, 50.0, 20.0, 40.0], "k": 2}',
        "category": "vector",
    },
    "vec-early-abandon": {
        "id": "ALGO-VEC-SRCH-55",
        "algo_name": "Early Abandoning Distance",
        "plain_name": "Stop distance calculation early if candidate is too far",
        "what_it_does": "Halts math as soon as partial distance exceeds current best threshold — saves up to 70% of calculations.",
        "example": '{"database_vectors": [[0,0],[5,5]], "query_vector": [0,0], "k": 1}',
        "category": "vector",
    },
    "vec-pivot": {
        "id": "ALGO-VEC-SRCH-56",
        "algo_name": "Pivot Triangle-Inequality Pruning",
        "plain_name": "Skip far vectors using reference landmark points",
        "what_it_does": "Uses precalculated distances to landmark pivots to rule out distant vectors without full calculations.",
        "example": '{"database_vectors": [[0,0],[1,1],[10,10]], "pivots": [[0,0]], "query_vector": [0.1,0.1], "k": 1}',
        "category": "vector",
    },
    "vec-kdtree": {
        "id": "ALGO-VEC-SRCH-57",
        "algo_name": "KD-Tree Spatial Index",
        "plain_name": "Fast spatial search tree across dimensions",
        "what_it_does": "Recursively splits coordinate axes to search points in logarithmic time instead of scanning everything.",
        "example": '{"vectors": [[2,3],[5,4],[9,6],[4,7]], "query": [9,5], "k": 2}',
        "category": "vector",
    },
    "vec-balltree": {
        "id": "ALGO-VEC-SRCH-58",
        "algo_name": "Ball Tree Metric Index",
        "plain_name": "Group vectors into nested bounding spheres",
        "what_it_does": "Encloses points into spherical clusters to beat the curse of dimensionality in higher dimensions.",
        "example": '{"vectors": [[0,0],[1,1],[5,5],[10,10]], "query": [0.9,0.9], "k": 1}',
        "category": "vector",
    },
    "vec-vptree": {
        "id": "ALGO-VEC-SRCH-59",
        "algo_name": "Vantage-Point Tree",
        "plain_name": "Split metric space using concentric shells",
        "what_it_does": "Partitions data into spherical shells around vantage points — works in any metric distance space.",
        "example": '{"vectors": [[0,0],[1,1],[5,5],[10,10]], "query": [5.1,5.1], "k": 1}',
        "category": "vector",
    },
    "vec-rpforest": {
        "id": "ALGO-VEC-SRCH-60",
        "algo_name": "Random Projection Tree Forest (Annoy-style)",
        "plain_name": "Fast approximate search using random planes",
        "what_it_does": "Splits space with random cutting planes across multiple trees for fast approximate nearest neighbor search.",
        "example": '{"vectors": [[0,0],[1,2],[2,4],[3,6]], "query": [1,2], "k": 2, "num_trees": 4}',
        "category": "vector",
    },
    "vec-ivf": {
        "id": "ALGO-VEC-SRCH-61",
        "algo_name": "Inverted File Index (IVF)",
        "plain_name": "Group vectors into Voronoi buckets and search top cells",
        "what_it_does": "Clusters vectors with k-means and only searches the closest cluster cells (nprobe) at query time.",
        "example": '{"vectors": [[0,0],[1,1],[5,5],[6,6]], "query": [0.5,0.5], "k": 2, "num_clusters": 2, "nprobe": 1}',
        "category": "vector",
    },
    "vec-ivfpq": {
        "id": "ALGO-VEC-SRCH-62",
        "algo_name": "IVF with Product Quantization (IVF-PQ)",
        "plain_name": "Search billions of compressed vectors in RAM",
        "what_it_does": "Combines cluster routing with sub-vector byte compression and fast distance lookup tables.",
        "example": '{"vectors": [[1,2,3,4],[5,6,7,8]], "query": [1,2,3,4], "k": 1, "num_clusters": 2, "nprobe": 1}',
        "category": "vector",
    },
    "vec-nprobe": {
        "id": "ALGO-VEC-SRCH-63",
        "algo_name": "nprobe Multi-Probe Tuner",
        "plain_name": "Automatically find the best balance of speed vs accuracy",
        "what_it_does": "Sweeps nprobe values against exact ground truth to find the fastest setting meeting your recall goal.",
        "example": '{"database_vectors": [[1,1],[2,2],[3,3],[4,4]], "sample_queries": [[1.1,1.1]], "target_recall": 0.9}',
        "category": "vector",
    },
    "vec-imi": {
        "id": "ALGO-VEC-SRCH-64",
        "algo_name": "Inverted Multi-Index (IMI)",
        "plain_name": "Ultra-fine dual-codebook Voronoi search",
        "what_it_does": "Splits vectors into halves and pairs centroids to create millions of fine cells with tiny memory.",
        "example": '{"vectors": [[1,2,3,4],[5,6,7,8]], "query": [1,2,3,4], "k": 1, "codebook_k1": 2, "codebook_k2": 2}',
        "category": "vector",
    },
    "vec-nsw": {
        "id": "ALGO-VEC-SRCH-65",
        "algo_name": "Navigable Small World (NSW) Graph",
        "plain_name": "Fast proximity graph routing with highway shortcuts",
        "what_it_does": "Navigates a small-world proximity network using greedy routing from long highway edges to local neighbors.",
        "example": '{"vectors": [[1,2],[3,4],[5,6]], "query": [1,2], "k": 2}',
        "category": "vector",
    },
    "vec-hnsw-search": {
        "id": "ALGO-VEC-SRCH-66",
        "algo_name": "Hierarchical NSW Search",
        "plain_name": "Logarithmic multi-layer vector graph search",
        "what_it_does": "Explores coarse sparse layers greedily down to layer 0 for bounded beam search with ef candidates.",
        "example": '{"vectors": [[1,2],[3,4]], "layers": [{"0": [1], "1": [0]}], "entry_point": 0, "top_layer": 0, "query": [1,2], "k": 1}',
        "category": "vector",
    },
    "vec-hnsw-insert": {
        "id": "ALGO-VEC-SRCH-67",
        "algo_name": "HNSW Layer Insertion & Diversity Pruning",
        "plain_name": "Scale-free graph insertion with directional link pruning",
        "what_it_does": "Builds multi-layer scale-free graphs, pruning links that point in redundant directions.",
        "example": '{"vectors": [[1,2],[3,4],[5,6]], "m": 2, "ef_construction": 8}',
        "category": "vector",
    },
    "vec-beam": {
        "id": "ALGO-VEC-SRCH-68",
        "algo_name": "Bounded Graph Beam Search",
        "plain_name": "Priority queue exploration with ef budget limit",
        "what_it_does": "Traverses graph edges using two bounded heaps, stopping when unexpanded nodes are farther than worst result.",
        "example": '{"vectors": [[1,2],[3,4]], "adjacency": {"0": [1], "1": [0]}, "start_nodes": [0], "query": [1,2], "k": 1}',
        "category": "vector",
    },
    "vec-vamana": {
        "id": "ALGO-VEC-SRCH-69",
        "algo_name": "Vamana / DiskANN Graph Index",
        "plain_name": "Single-layer graph index for billion-scale SSD search",
        "what_it_does": "Constructs two-pass graph index from medoid with RobustPrune for fast disk-resident retrieval.",
        "example": '{"vectors": [[1,2],[3,4],[5,6]], "query": [1,2], "k": 1, "r_max_degree": 4}',
        "category": "vector",
    },
    "vec-robust-prune": {
        "id": "ALGO-VEC-SRCH-70",
        "algo_name": "RobustPrune Alpha Diversity Filter",
        "plain_name": "Eliminate redundant neighbor paths while preserving long-range shortcuts",
        "what_it_does": "Prunes candidate neighbors using alpha triangle inequality to maintain high connectivity with bounded degree.",
        "example": '{"point": [0,0], "candidate_vectors": [[1,0],[0.5,0.1],[5,5]], "alpha": 1.2, "r_max_degree": 2}',
        "category": "vector",
    },
    "vec-nsg": {
        "id": "ALGO-VEC-SRCH-71",
        "algo_name": "Navigating Spreading-out Graph (NSG)",
        "plain_name": "Monotonic relative neighborhood graph with high recall",
        "what_it_does": "Prunes kNN graphs with MRNG rule and repairs connectivity from a central navigating node.",
        "example": '{"vectors": [[1,2],[3,4],[5,6]], "query": [1,2], "k": 1}',
        "category": "vector",
    },
    "vec-cagra": {
        "id": "ALGO-VEC-SRCH-72",
        "algo_name": "CAGRA Fixed-Degree Graph",
        "plain_name": "GPU-optimized regularized proximity graph",
        "what_it_does": "Transforms proximity graph into strict fixed-degree layout for parallel GPU batch search.",
        "example": '{"vectors": [[1,2],[3,4],[5,6],[7,8]], "query": [1,2], "k": 1, "fixed_degree": 2}',
        "category": "vector",
    },
    "vec-entry": {
        "id": "ALGO-VEC-SRCH-73",
        "algo_name": "Entry-Point Selection",
        "plain_name": "Pick geometric medoid or multi-seed starting points",
        "what_it_does": "Computes medoid or furthest-point sampling seeds to prevent graph trapping on multi-modal datasets.",
        "example": '{"vectors": [[1,2],[3,4],[5,6]], "strategy": "medoid"}',
        "category": "vector",
    },
    "vec-repair": {
        "id": "ALGO-VEC-SRCH-74",
        "algo_name": "Graph Connectivity Repair",
        "plain_name": "Detect unreachable islands and reconnect isolated nodes",
        "what_it_does": "Performs BFS reachability sweep and links unreachable nodes to their nearest reachable neighbors.",
        "example": '{"vectors": [[1,2],[3,4],[5,6]], "adjacency": {"0": [], "1": [], "2": []}, "entry_points": [0]}',
        "category": "vector",
    },
    "vec-filtered-diskann": {
        "id": "ALGO-VEC-SRCH-75",
        "algo_name": "Filtered-DiskANN",
        "plain_name": "Strict label-constrained in-index vector search",
        "what_it_does": "Traverses graph paths starting from label-specific medoid, ensuring only nodes matching target label are inspected.",
        "example": '{"vectors": [[1,2],[3,4]], "labels": ["tenantA", "tenantB"], "query": [1,2], "target_label": "tenantA", "k": 1}',
        "category": "vector",
    },
    "vec-spann": {
        "id": "ALGO-VEC-SRCH-76",
        "algo_name": "SPANN Memory-Disk Hybrid Index",
        "plain_name": "Centroids in RAM and boundary-duplicated postings on disk",
        "what_it_does": "Clusters vectors with boundary duplication into adjacent posting lists for fast sequential disk reads.",
        "example": '{"vectors": [[1,2],[3,4],[5,6],[7,8]], "query": [1,2], "k": 1, "num_centroids": 2, "nprobe": 1}',
        "category": "vector",
    },
    "vec-lsh-hyperplane": {
        "id": "ALGO-VEC-SRCH-77",
        "algo_name": "Random-Hyperplane LSH",
        "plain_name": "Locality-sensitive cosine hashing with random hyperplanes",
        "what_it_does": "Projects vectors onto random hyperplanes to generate bit signatures for fast sub-linear bucket lookup.",
        "example": '{"vectors": [[1,2],[3,4],[5,6]], "query": [1,2], "k": 1, "num_bits": 2, "num_tables": 2}',
        "category": "vector",
    },
    "vec-lsh-multiprobe": {
        "id": "ALGO-VEC-SRCH-78",
        "algo_name": "Multi-Probe LSH",
        "plain_name": "Check nearby perturbed hash buckets for high recall",
        "what_it_does": "Probes primary and perturbed bit buckets ranked by proximity to hyperplane boundary.",
        "example": '{"vectors": [[1,2],[3,4],[5,6]], "query": [1,2], "k": 1, "num_bits": 4, "probe_budget": 2}',
        "category": "vector",
    },
    "vec-e2lsh": {
        "id": "ALGO-VEC-SRCH-79",
        "algo_name": "Exact Euclidean L2 LSH (E2LSH)",
        "plain_name": "P-stable Gaussian random projection hashing for Euclidean space",
        "what_it_does": "Uses 2-stable Gaussian projections and uniform quantization slots for theoretical Euclidean collision guarantees.",
        "example": '{"vectors": [[1,2],[3,4],[5,6]], "query": [1,2], "k": 1, "slot_width_w": 4.0}',
        "category": "vector",
    },
    "vec-filter-pre": {
        "id": "ALGO-VEC-FLTR-80",
        "algo_name": "Vector Metadata Pre-Filtering",
        "plain_name": "Filter candidates before scoring vectors",
        "what_it_does": "Evaluates metadata predicates first to ensure zero security leaks before distance computation.",
        "example": '{"vectors": [[0,0],[1,1]], "metadata": [{"tenant":"A"},{"tenant":"B"}], "query": [0.1,0.1], "filters": {"tenant":"A"}, "k": 1}',
        "category": "filter",
    },
    "vec-filter-post": {
        "id": "ALGO-VEC-FLTR-81",
        "algo_name": "Vector Post-Filtering with Oversampling",
        "plain_name": "Search first with extra items then remove non-matching",
        "what_it_does": "Retrieves k * f candidates from index and rejects records that fail soft non-security filters.",
        "example": '{"vectors": [[0,0],[1,1]], "metadata": [{"lang":"en"},{"lang":"fr"}], "query": [0.1,0.1], "filters": {"lang":"en"}, "k": 1, "oversample_factor": 2.0}',
        "category": "filter",
    },
    "vec-filter-in-graph": {
        "id": "ALGO-VEC-FLTR-82",
        "algo_name": "ACORN In-Graph Filtering",
        "plain_name": "Hop across filtered graph nodes without breaking connectivity",
        "what_it_does": "Traverses graph routing paths while strictly admitting only allowed nodes into top-k candidates.",
        "example": '{"vectors": [[0,0],[1,0],[2,0]], "metadata": [{"status":"active"},{"status":"disabled"},{"status":"active"}], "adjacency": {"0":[1],"1":[2],"2":[]}, "entry_point": 0, "query": [1.9,0.0], "filters": {"status":"active"}, "k": 1}',
        "category": "filter",
    },
    "vec-filter-plan": {
        "id": "ALGO-VEC-FLTR-83",
        "algo_name": "Selectivity-Based Query Planner",
        "plain_name": "Choose best search strategy from filter selectivity",
        "what_it_does": "Estimates match ratio and picks pre-filtering, in-graph ACORN traversal, or post-filtering.",
        "example": '{"total_vectors": 10000, "metadata_sample": [{"tenant":"T1"},{"tenant":"T2"}], "filters": {"tenant":"T1"}, "is_security_filter": true}',
        "category": "filter",
    },
    "vec-filter-partition": {
        "id": "ALGO-VEC-FLTR-84",
        "algo_name": "Partitioned Multi-Tenant Index Search",
        "plain_name": "Route query strictly into tenant or collection slice",
        "what_it_does": "Directs search exclusively into the isolated physical partition with zero cross-tenant contamination.",
        "example": '{"partitions": {"tenant_A": [{"id":"d1","vector":[1,0],"metadata":{}}]}, "target_partition": "tenant_A", "query": [0.9,0.1], "k": 1}',
        "category": "filter",
    },
    "vec-bm25": {
        "id": "ALGO-VEC-SRCH-85",
        "algo_name": "Okapi BM25 Keyword Search",
        "plain_name": "Fast keyword search using term frequencies and document lengths",
        "what_it_does": "Scores documents with probabilistic TF-IDF and field length normalization.",
        "example": '{"corpus": ["hello world document", "another text"], "query": "hello", "k": 1}',
        "category": "vector",
    },
    "vec-hybrid": {
        "id": "ALGO-VEC-SRCH-86",
        "algo_name": "Sparse-Dense Hybrid Search",
        "plain_name": "Combine keyword search and semantic vector search",
        "what_it_does": "Blends lexical sparse keyword scores with dense vector similarities via linear interpolation.",
        "example": '{"dense_results": [{"id": "1", "score": 0.8}], "sparse_results": [{"id": "1", "score": 12.0}], "alpha": 0.5, "k": 1}',
        "category": "vector",
    },
    "vec-rrf": {
        "id": "ALGO-VEC-SRCH-87",
        "algo_name": "Reciprocal Rank Fusion",
        "plain_name": "Merge multiple ranking lists using reciprocal rank scores",
        "what_it_does": "Combines ranked lists without score calibration: score = sum(1 / (k + rank)).",
        "example": '{"rankings": [[{"id": "a"}, {"id": "b"}], [{"id": "b"}, {"id": "a"}]], "k_rrf": 60, "top_k": 2}',
        "category": "vector",
    },
    "vec-convex-fusion": {
        "id": "ALGO-VEC-SRCH-88",
        "algo_name": "Convex Score Fusion",
        "plain_name": "Weighted combination of normalized retrieval scores",
        "what_it_does": "Normalizes score scales (min-max or z-score) and fuses candidate channels with tuned weights.",
        "example": '{"score_lists": [[{"id": "1", "score": 0.9}], [{"id": "1", "score": 15.0}]], "norm_method": "minmax", "top_k": 1}',
        "category": "vector",
    },
    "vec-mmr": {
        "id": "ALGO-VEC-SRCH-89",
        "algo_name": "Maximal Marginal Relevance",
        "plain_name": "Balance relevance and diversity to prevent duplicate passages",
        "what_it_does": "Reranks candidates iteratively penalizing similarity to already chosen candidates.",
        "example": '{"candidate_vectors": [[1,0],[0.99,0.01],[0,1]], "candidate_ids": ["a","b","c"], "query_vector": [1,0], "lambda_mult": 0.7, "k": 2}',
        "category": "vector",
    },
    "vec-range": {
        "id": "ALGO-VEC-SRCH-90",
        "algo_name": "Range Radius Search",
        "plain_name": "Find all vectors within distance threshold rather than fixed top-k",
        "what_it_does": "Returns every neighbor within distance radius r, bounded by maximum allowed results.",
        "example": '{"vectors": [[0,0],[1,1],[5,5]], "query": [0,0], "radius": 1.5, "metric": "l2"}',
        "category": "vector",
    },
    "vec-maxsim": {
        "id": "ALGO-VEC-SRCH-91",
        "algo_name": "ColBERT Late-Interaction MaxSim",
        "plain_name": "Fine-grained token-level vector matching across query and document",
        "what_it_does": "Scores documents by summing maximum similarity of each query token across all document tokens.",
        "example": '{"document_token_vectors": [[[1,0],[0,1]]], "query_token_vectors": [[1,0]], "k": 1}',
        "category": "vector",
    },
    "vec-multi-query": {
        "id": "ALGO-VEC-SRCH-92",
        "algo_name": "Multi-Query Expansion",
        "plain_name": "Rewrite query into variants, search all, and fuse results",
        "what_it_does": "Runs multiple query variations in parallel and combines hits using rank fusion.",
        "example": '{"vectors": [[1,0],[0,1]], "expanded_queries": [[1,0],[0.9,0.1]], "k": 1}',
        "category": "vector",
    },
    "vec-rescore": {
        "id": "ALGO-VEC-SRCH-93",
        "algo_name": "Full Precision Rescoring",
        "plain_name": "Retrieve cheap candidates then re-score exact distances",
        "what_it_does": "Fetches uncompressed vectors for top compressed candidates to restore full recall.",
        "example": '{"candidate_ids": ["1"], "full_precision_vectors": {"1": [1.0, 0.0]}, "query_vector": [1.0, 0.0], "top_k": 1}',
        "category": "vector",
    },
    "vec-cross-encoder": {
        "id": "ALGO-VEC-SRCH-94",
        "algo_name": "Cross-Encoder Transformer Reranker",
        "plain_name": "Re-score top candidates by feeding query and passage jointly",
        "what_it_does": "Applies full cross-attention scoring across top candidate texts for maximum precision.",
        "example": '{"query": "machine learning", "candidates": [{"id": "1", "text": "ml intro"}], "top_k": 1}',
        "category": "vector",
    },
    "vec-funnel": {
        "id": "ALGO-VEC-SRCH-95",
        "algo_name": "Multi-Stage Retrieval Funnel",
        "plain_name": "Cascaded progressive ranking across candidate subsets",
        "what_it_does": "Applies cheap coarse search, intermediate rescoring, and precise final ranking stages.",
        "example": '{"stage1_candidates": [{"id": "1", "score": 0.9}], "stage2_top_m": 10, "stage3_top_k": 1}',
        "category": "vector",
    },
    "vec-llm-rerank": {
        "id": "ALGO-VEC-SRCH-96",
        "algo_name": "LLM Listwise Reranker",
        "plain_name": "Order small candidate list using language model reasoning",
        "what_it_does": "Prompts a language model with candidate summaries and strictly parses ranked order.",
        "example": '{"query": "best database", "candidates": [{"id": "1", "text": "Postgres is great"}], "top_k": 1}',
        "category": "vector",
    },
    "vec-hyde": {
        "id": "ALGO-VEC-SRCH-97",
        "algo_name": "Hypothetical Document Embeddings",
        "plain_name": "Generate hypothetical answer, embed it, and retrieve documents",
        "what_it_does": "Embeds generated hypothetical answers and fuses them with original query vector.",
        "example": '{"corpus_vectors": [[1,0],[0,1]], "query_vector": [1,0], "hypothetical_vectors": [[0.9,0.1]], "k": 1}',
        "category": "vector",
    },
    "vec-query-routing": {
        "id": "ALGO-VEC-SRCH-98",
        "algo_name": "Query Intent Routing",
        "plain_name": "Classify query and direct it to the best collection index",
        "what_it_does": "Routes incoming questions to appropriate indices (code, documentation, tickets).",
        "example": '{"query": "def parse_tokens", "available_routes": {"code": ["def", "class"], "docs": ["guide", "readme"]}}',
        "category": "vector",
    },
    "vec-scatter-gather": {
        "id": "ALGO-VEC-SRCH-99",
        "algo_name": "Sharded Scatter-Gather Search",
        "plain_name": "Query shards in parallel and merge results into global top-k",
        "what_it_does": "Broadcasts search query to shards and merges top-k candidates with min-heap.",
        "example": '{"shard_results": {"s1": [{"id": "1", "score": 0.9}], "s2": [{"id": "2", "score": 0.95}]}, "top_k": 2}',
        "category": "vector",
    },
    "vec-partition-routing": {
        "id": "ALGO-VEC-SRCH-100",
        "algo_name": "Partition-Aware Centroid Routing",
        "plain_name": "Route query to closest centroid shards saving search work",
        "what_it_does": "Compares query against cluster centroids to prune shards that cannot contain nearest neighbors.",
        "example": '{"centroids": [[1,0],[0,1]], "centroid_to_shard_map": {"0": "shard_1", "1": "shard_2"}, "query_vector": [0.9,0.1], "num_target_shards": 1}',
        "category": "vector",
    },
    "vec-load-balancer": {
        "id": "ALGO-VEC-SRCH-101",
        "algo_name": "Replication Load Balancer",
        "plain_name": "Select replica node by least loaded or lowest latency",
        "what_it_does": "Directs query requests among healthy replicas using round-robin, least-loaded, or latency heuristics.",
        "example": '{"replicas": [{"id": "r1", "healthy": true, "active_queries": 2}, {"id": "r2", "healthy": true, "active_queries": 0}], "strategy": "least_loaded"}',
        "category": "vector",
    },
    "vec-hedged-requests": {
        "id": "ALGO-VEC-SRCH-102",
        "algo_name": "Hedged Requests",
        "plain_name": "Send backup query if primary is slow cutting tail latency",
        "what_it_does": "Dispatches secondary request to backup replica when primary exceeds latency SLA threshold.",
        "example": '{"primary_latency_ms": 120.0, "backup_latency_ms": 25.0, "hedge_delay_threshold_ms": 50.0, "is_read_only": true}',
        "category": "vector",
    },
    "vec-kway-merge": {
        "id": "ALGO-VEC-SRCH-103",
        "algo_name": "K-Way Shard Merge",
        "plain_name": "Merge sorted candidate lists from multiple shards using heap",
        "what_it_does": "Produces single sorted top-k output from M pre-sorted shard streams in O(k log M).",
        "example": '{"shard_sorted_lists": [[{"id": "a", "score": 0.9}], [{"id": "b", "score": 0.8}]], "k": 2}',
        "category": "vector",
    },
    "vec-query-cache": {
        "id": "ALGO-VEC-SRCH-104",
        "algo_name": "Query & Result Cache",
        "plain_name": "Cache repeated queries and invalidate automatically on index updates",
        "what_it_does": "Stores query results keyed by query, tenant, filters, and index version with LRU eviction.",
        "example": '{"cache_store": {}, "query": "auth", "tenant_id": "t1", "filters": {}, "index_version": "v1", "results": [{"id": "1"}]}',
        "category": "vector",
    },
    "vec-semantic-cache": {
        "id": "ALGO-VEC-SRCH-105",
        "algo_name": "Semantic Similarity Cache",
        "plain_name": "Reuse cached responses when incoming query is semantically identical",
        "what_it_does": "Matches incoming query embedding against cached queries above similarity threshold.",
        "example": '{"cached_entries": [{"query_vector": [1,0], "result": "cached_answer"}], "query_vector": [0.99,0.01], "tenant_id": "t1", "similarity_threshold": 0.95}',
        "category": "vector",
    },
    "vec-batching": {
        "id": "ALGO-VEC-SRCH-106",
        "algo_name": "Query Batching",
        "plain_name": "Group concurrent queries into micro-batches for throughput",
        "what_it_does": "Packs concurrent queries into matrix batches to maximize GPU and SIMD utilization.",
        "example": '{"pending_queries": [{"id": "q1", "arrival_time": 0.1}], "max_batch_size": 16}',
        "category": "vector",
    },
    "vec-memory-tiering": {
        "id": "ALGO-VEC-SRCH-107",
        "algo_name": "RAM/SSD Memory Tiering",
        "plain_name": "Place hot index parts in RAM and large parts on SSD",
        "what_it_does": "Partitions vector index components into RAM residency or memory-mapped SSD storage.",
        "example": '{"components": [{"name": "centroids", "size_mb": 64, "priority": 10}, {"name": "vectors", "size_mb": 4096, "priority": 1}], "ram_budget_mb": 512}',
        "category": "vector",
    },
    "vec-disk-scheduler": {
        "id": "ALGO-VEC-SRCH-108",
        "algo_name": "Disk I/O Beam Scheduler",
        "plain_name": "Organize SSD reads in page-aligned batches for graph ANN",
        "what_it_does": "Batches proximity graph node lookups into page-aligned I/O requests to reduce SSD read latency.",
        "example": '{"requested_node_ids": [10, 20, 30], "cached_nodes": [10], "max_batch_size": 8}',
        "category": "vector",
    },
    "vec-admission-control": {
        "id": "ALGO-VEC-SRCH-109",
        "algo_name": "Token Bucket Admission Control",
        "plain_name": "Throttle and shed load to protect against runaway agent loops",
        "what_it_does": "Maintains token bucket and concurrency limit to reject or shed queries during overload.",
        "example": '{"current_tokens": 50.0, "max_tokens": 100.0, "refill_rate_per_sec": 10.0, "last_refill_timestamp": 0.0, "current_concurrency": 5, "max_concurrency": 20, "now": 1.0}',
        "category": "vector",
    },
    "vec-search-autotune": {
        "id": "ALGO-VEC-SRCH-110",
        "algo_name": "Pareto Search Parameter Autotuner",
        "plain_name": "Find optimal search parameters meeting recall target at minimum latency",
        "what_it_does": "Sweeps parameters against ground truth to construct Pareto curve and pick fastest setting.",
        "example": '{"ground_truth_topk": [1, 2, 3], "parameter_evaluations": [{"ef_search": 16, "topk": [1, 2, 4], "latency_ms": 1.2}, {"ef_search": 64, "topk": [1, 2, 3], "latency_ms": 2.5}], "target_recall": 0.95}',
        "category": "vector",
    },
}
import os
import re
from pathlib import Path

REPO_ROOT = str(Path(__file__).resolve().parent.parent.parent.parent)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import json
import argparse
from dataclasses import asdict
from typing import List, Dict, Any, Optional

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
from src.features.code_engine.service.code_engine_service import CodeEngineService
from src.features.code_engine.registry.algorithm_catalog import BUILTIN_ALGORITHM_CONTRACTS, BUILTIN_TYPE_ADAPTERS
from src.features.code_engine.service.algorithm_composer_service import AlgorithmComposerService
from src.infra.adapters.database.in_memory_algorithm_registry_adapter import InMemoryAlgorithmRegistryAdapter
from src.infra.adapters.database.migration_runner import DatabaseMigrationRunner


def _init_rag_and_agent(rules_dir: str, backend: str):
    knowledge_source = PolicyRulesMarkdownLoader(base_rules_dir=rules_dir)
    vector_store = InMemoryCosineVectorAdapter()

    if backend == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for openai backend")
        llm = OpenAICompatibleAdapter(
            api_key=api_key,
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            model_name=os.environ.get("OPENAI_MODEL", "gpt-4o"),
        )
    elif backend == "ollama":
        llm = OpenAICompatibleAdapter(
            api_key="ollama",
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            model_name=os.environ.get("OLLAMA_MODEL", "llama3"),
        )
    else:
        llm = MockLLMAdapter()

    rag_service = RAGService(knowledge_source, vector_store, llm)
    agent_service = AgentService(rag_service, llm)
    return rag_service, agent_service


def handle_search_command(args: argparse.Namespace) -> int:
    svc = CodeEngineService()
    raw_patterns = getattr(args, "patterns", None) or "TODO,FIXME,error,critical"
    patterns = [p.strip() for p in raw_patterns.split(",") if p.strip()]
    target_dir = getattr(args, "directory", None) or getattr(args, "root", ".")
    results = svc.scan_directory_multipattern(target_dir, patterns)

    if getattr(args, "json", False):
        print(json.dumps(results, indent=2))
        return 0

    print(f"\n{'='*75}")
    print(f"🔎 [SEARCH ENGINE] {len(results)} Files Matched in '{target_dir}'")
    print(f"{'='*75}\n")
    for res in results:
        print(f"📁 {res['file']} ({res['match_count']} matches)")
        for m in res["matches"][:3]:
            print(f"   Line {m['line']} [{m['pattern']}]: {m['context']}")
    return 0


def handle_scan_command(args: argparse.Namespace) -> int:
    target_dir = getattr(args, "root", None) or getattr(args, "directory", ".")
    svc = CodeEngineService()
    files = svc.execute_algorithm("ALGO-SRCH-01", {"root_dir": target_dir})

    if getattr(args, "json", False):
        print(json.dumps(files, indent=2))
        return 0

    file_list = files.get("files", [])
    print(f"\n{'='*75}")
    print(f"📂 [SCAN ENGINE] Discovered {len(file_list)} files under '{target_dir}'")
    print(f"{'='*75}\n")
    for f in file_list[:30]:
        print(f"  • {f}")
    if len(file_list) > 30:
        print(f"  ... and {len(file_list) - 30} more files.")
    return 0


def handle_outline_command(args: argparse.Namespace) -> int:
    file_path = getattr(args, "file", None)
    if not file_path:
        print("Error: file path is required")
        return 1

    svc = CodeEngineService()
    res = svc.inspect_file_outline(file_path)

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return 0

    print(res.get("markdown", "No outline available"))
    return 0


def handle_lint_command(args: argparse.Namespace) -> int:
    file_path = getattr(args, "file", None)
    if not file_path:
        print("Error: file path is required")
        return 1

    svc = CodeEngineService()
    res = svc.lint_zero_inline_comments(file_path)

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return 0 if res["is_compliant"] else 1

    status = "✅ COMPLIANT" if res["is_compliant"] else "❌ VIOLATION"
    print(f"\n{'='*75}")
    print(f"🛡️ [ZERO-INLINE-COMMENT DOCTRINE] {status}")
    print(f"   File: {res['file']}")
    print(f"   Banned Inline Comments: {res['banned_inline_count']}")
    print(f"   TODOs/FIXMEs: {res['todos_count']}")
    print(f"{'='*75}\n")
    for c in res["banned_comments"]:
        print(f"   Line {c['line']}: {c['text']}")
    return 0 if res["is_compliant"] else 1


def handle_deps_command(args: argparse.Namespace) -> int:
    target_dir = getattr(args, "directory", None) or getattr(args, "root", "src")
    svc = CodeEngineService()
    res = svc.analyze_module_dependencies(target_dir)

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return 0

    print(f"\n{'='*75}")
    print(f"🕸️ [IMPORT GRAPH] {res['total_modules']} Modules, {res['total_edges']} Edges")
    print(f"   Cycles: {'⚠️ DETECTED' if res['has_cycles'] else '✅ NONE'}")
    print(f"{'='*75}\n")
    if res["cycles"]:
        for cycle in res["cycles"]:
            print(f"  🔁 {' -> '.join(cycle)}")
    print(f"\nTopological Build Order ({len(res['topological_order'])} modules):")
    print(f"  {' -> '.join(res['topological_order'][:10])}{' ...' if len(res['topological_order']) > 10 else ''}")
    return 0


def handle_diff_command(args: argparse.Namespace) -> int:
    file_path = getattr(args, "file", None)
    find_str = getattr(args, "find", "")
    replace_str = getattr(args, "replace", "")
    is_regex = getattr(args, "regex", False)

    if not file_path or not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        return 1

    with open(file_path, "r", encoding="utf-8") as f:
        orig = f.read()

    mod = orig.replace(find_str, replace_str) if not is_regex else re.sub(find_str, replace_str, orig)
    svc = CodeEngineService()
    diff_res = svc.generate_diff(orig, mod, file_path=file_path)

    if getattr(args, "json", False):
        print(json.dumps(diff_res, indent=2))
        return 0

    print(f"\n{'='*75}")
    print(f"📝 [UNIFIED DIFF] (+{diff_res['added_lines']} / -{diff_res['deleted_lines']})")
    print(f"{'='*75}\n")
    print(diff_res["patch"] if diff_res["has_changes"] else "No differences found.")
    return 0


def handle_patch_command(args: argparse.Namespace) -> int:
    file_path = getattr(args, "file", None)
    find_str = getattr(args, "find", "")
    replace_str = getattr(args, "replace", "")
    is_regex = getattr(args, "regex", False)
    apply_mutations = getattr(args, "apply", False)

    if not file_path:
        print("Error: file path is required")
        return 1

    svc = CodeEngineService()
    ops = [{
        "file_path": file_path,
        "find_pattern": find_str,
        "replace_text": replace_str,
        "is_regex": is_regex,
    }]
    res = svc.apply_batch_patch(ops, dry_run=not apply_mutations)

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return 0 if res[0]["success"] else 1

    status = "[APPLIED]" if apply_mutations else "[DRY-RUN]"
    print(f"\n{'='*75}")
    print(f"⚡ [ATOMIC PATCH] {status}")
    print(f"   File: {res[0]['file_path']}")
    print(f"   Matches: {res[0]['occurrences']}")
    print(f"   Pre SHA-256 : {res[0]['before_sha256'][:12]}...")
    print(f"   Post SHA-256: {res[0]['after_sha256'][:12]}...")
    print(f"{'='*75}\n")
    return 0 if res[0]["success"] else 1


def handle_exec_command(args: argparse.Namespace) -> int:
    algo_id = getattr(args, "id", None)
    if not algo_id:
        print("Error: Algorithm ID is required (e.g. ALGO-VEC-01, ALGO-SRCH-11, ALGO-GRAPH-01)")
        return 1

    input_str = getattr(args, "input", "{}") or "{}"
    try:
        if input_str.startswith("@") or (os.path.isfile(input_str) and not input_str.startswith("{")):
            path = input_str.removeprefix("@")
            with open(path, "r", encoding="utf-8") as f:
                inputs = json.load(f)
        else:
            inputs = json.loads(input_str)
    except Exception as e:
        print(f"Error parsing input JSON: {e}")
        return 1

    svc = CodeEngineService()
    try:
        result = svc.execute_algorithm(algo_id=algo_id, inputs=inputs)
        if getattr(args, "json", False):
            print(json.dumps({"algo_id": algo_id, "result": result}, indent=2))
        else:
            print(f"\n{'='*75}")
            print(f"⚡ [ALGORITHM ENGINE] EXECUTED: {algo_id}")
            print(f"{'='*75}\n")
            print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        print(f"Execution failed: {e}")
        return 1


def handle_contracts_command(args: argparse.Namespace) -> int:
    category_filter = getattr(args, "category", None)
    tag_filter = getattr(args, "tag", None)
    contracts = [
        c for c in BUILTIN_ALGORITHM_CONTRACTS
        if (not category_filter or c.category.value == category_filter)
        and (not tag_filter or tag_filter in c.capability_tags)
    ]

    if getattr(args, "json", False):
        print(json.dumps([c.model_dump() for c in contracts], indent=2))
        return 0

    print(f"\n{'='*95}")
    print(f"📋 [ALGORITHM REGISTRY] {len(BUILTIN_ALGORITHM_CONTRACTS)} TOTAL CONTRACTS ({len(contracts)} matching)")
    print(f"{'='*95}")
    for c in contracts:
        print(f"  • [{c.id}] {c.name:<32} Category: {c.category.value:<14} Time: {c.complexity.time:<10} Target: {c.hardware_target.value}")
    return 0


def handle_compose_command(args: argparse.Namespace) -> int:
    raw_algos = getattr(args, "algos", "ALGO-SRCH-03,ALGO-OBS-17,ALGO-UPD-23") or "ALGO-SRCH-03,ALGO-OBS-17,ALGO-UPD-23"
    algo_ids = [a.strip() for a in raw_algos.split(",") if a.strip()]
    adapter = InMemoryAlgorithmRegistryAdapter(load_builtins=True)
    composer = AlgorithmComposerService(adapter)
    res = composer.compose_pipeline(algo_ids)

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
        return 0

    status = "✅ VALID" if res["is_valid"] else "❌ INVALID (Safety Warnings)"
    print(f"\n{'='*85}")
    print(f"🧩 [DYNAMIC PIPELINE COMPOSER] {status}")
    print(f"{'='*85}")
    print(f"Execution DAG Steps ({res['total_steps']}):")
    for step in res["pipeline_steps"]:
        print(f"  {step['step_index']}. ⚡ [{step['algo_id']}] {step['name']:<36} (Time: {step['complexity']['time']})")
    if res.get("inferred_adapters"):
        print("\nInjected G4 Type Adapters:")
        for ad in res["inferred_adapters"]:
            print(f"  🔧 Steps {ad['between_steps'][0]} -> {ad['between_steps'][1]}: {', '.join(ad['adapter_ids'])}")
    if res.get("safety_issues"):
        print("\nSafety Issues:")
        for w in res["safety_issues"]:
            print(f"  ⚠️  {w}")
    return 0 if res["is_valid"] else 1


def handle_run_command(args: argparse.Namespace) -> int:
    alias = getattr(args, "alias", None)
    if not alias:
        print("Error: alias name is required. Run `policy-orchestrator list` to see all available names.")
        return 1

    entry = ALGO_ALIASES.get(alias)
    if not entry:
        close = [k for k in ALGO_ALIASES if alias in k or k.startswith(alias[:3])]
        print(f"Unknown alias: '{alias}'")
        if close:
            print(f"Did you mean: {', '.join(close)}")
        print("Run `policy-orchestrator list` to see every available name.")
        return 1

    input_str = getattr(args, "input", "{}") or "{}"
    try:
        if input_str.startswith("@") or (os.path.isfile(input_str) and not input_str.startswith("{")):
            path = input_str.removeprefix("@")
            with open(path, "r", encoding="utf-8") as f:
                inputs = json.load(f)
        else:
            inputs = json.loads(input_str)
    except Exception as e:
        print(f"Bad input JSON: {e}")
        print(f"Example input for '{alias}': {entry['example']}")
        return 1

    svc = CodeEngineService()
    try:
        result = svc.execute_algorithm(algo_id=entry["id"], inputs=inputs)
    except Exception as e:
        print(f"Execution error: {e}")
        return 1

    print(f"\n{'='*75}")
    print(f"⚡  {entry['algo_name']}  ({entry['id']})")
    print(f"   {entry['plain_name']}")
    print(f"{'='*75}\n")
    print(json.dumps(result, indent=2))
    print(f"\n{'='*75}")
    print(f"📦 JSON output above. Add --json for machine-readable only output.")
    print(f"{'='*75}")
    return 0


def handle_list_command(args: argparse.Namespace) -> int:
    category_filter = getattr(args, "category", None)
    entries = {
        k: v for k, v in ALGO_ALIASES.items()
        if not category_filter or v["category"] == category_filter
    }

    if getattr(args, "json", False):
        print(json.dumps({
            k: {
                "id": v["id"],
                "algo_name": v["algo_name"],
                "plain_name": v["plain_name"],
                "what_it_does": v["what_it_does"],
                "example_input": v["example"],
                "category": v["category"],
            }
            for k, v in entries.items()
        }, indent=2))
        return 0

    categories_present = sorted({v["category"] for v in entries.values()})
    cat_labels = {"graph": "🕸️  Graph", "vector": "🔢 Vector", "search": "🔎 Search", "observability": "🔭 Observability", "update": "✏️  Update"}

    print(f"\n{'='*95}")
    print(f"  📋  ALGORITHM QUICK-REFERENCE  —  {len(entries)} commands  (filter: --category graph|vector|search|observability|update)")
    print(f"{'='*95}")
    print(f"  {'COMMAND NAME':<22} {'ALGO NAME':<32} {'PLAIN ENGLISH — WHAT IT DOES'}")
    print(f"  {'-'*22} {'-'*32} {'-'*35}")

    for cat in categories_present:
        print(f"\n  {cat_labels.get(cat, cat.upper())}")
        for alias, v in entries.items():
            if v["category"] != cat:
                continue
            print(f"  {alias:<22} {v['algo_name']:<32} {v['plain_name']}")
            print(f"  {'':22} {'':32} ↳ {v['what_it_does'][:72]}")

    print(f"\n{'='*95}")
    print(f"  HOW TO RUN:  policy-orchestrator run <COMMAND NAME> '<JSON-input>'")
    print(f"  EXAMPLE:     policy-orchestrator run bfs '{{\"graph\": {{\"A\":[\"B\"]}}, \"start_node\": \"A\"}}'")
    print(f"  EXAMPLE:     policy-orchestrator run normalize '{{\"vectors\": [[1,2,3]]}}'")
    print(f"  SEE EXAMPLE: policy-orchestrator list --json   (shows example input for each command)")
    print(f"{'='*95}\n")
    return 0


def handle_completion_command(args: argparse.Namespace) -> int:
    shell = getattr(args, "shell", "bash")
    algo_ids = [c.id for c in BUILTIN_ALGORITHM_CONTRACTS]
    alias_names = list(ALGO_ALIASES.keys())
    subcmds = ["search", "scan", "outline", "lint", "deps", "diff", "patch", "exec", "run", "list", "contracts", "compose", "audit", "rag", "agent", "refactor", "policy-check", "migrate", "serve", "completion", "algo"]
    categories = ["search", "observability", "update", "vector", "graph", "filter"]

    if shell == "bash":
        script = f"""# Bash completion for policy-orchestrator
_policy_orchestrator_completion() {{
    local cur prev subcmd
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    prev="${{COMP_WORDS[COMP_CWORD-1]}}"
    subcmd="${{COMP_WORDS[1]}}"

    local subcommands="{' '.join(subcmds)}"
    local algo_ids="{' '.join(algo_ids)}"
    local alias_names="{' '.join(alias_names)}"
    local categories="{' '.join(categories)}"

    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $(compgen -W "$subcommands" -- "$cur") )
        return 0
    fi

    case "$subcmd" in
        exec|execute)
            if [ $COMP_CWORD -eq 2 ] || [ "$prev" = "--id" ]; then
                COMPREPLY=( $(compgen -W "$algo_ids" -- "$cur") )
                return 0
            fi
            ;;
        run)
            if [ $COMP_CWORD -eq 2 ]; then
                COMPREPLY=( $(compgen -W "$alias_names" -- "$cur") )
                return 0
            fi
            ;;
        list)
            if [ "$prev" = "--category" ]; then
                COMPREPLY=( $(compgen -W "$categories" -- "$cur") )
                return 0
            fi
            ;;
        contracts)
            if [ "$prev" = "--category" ]; then
                COMPREPLY=( $(compgen -W "$categories" -- "$cur") )
                return 0
            fi
            ;;
        outline|lint|diff|patch)
            COMPREPLY=( $(compgen -f -- "$cur") )
            return 0
            ;;
        search|scan|deps)
            COMPREPLY=( $(compgen -d -- "$cur") )
            return 0
            ;;
    esac

    local opts="--json --help --root --directory --file --find --replace --regex --apply --patterns"
    COMPREPLY=( $(compgen -W "$opts" -- "$cur") )
}}
complete -F _policy_orchestrator_completion policy-orchestrator
"""
    elif shell == "zsh":
        script = f"""#compdef policy-orchestrator
_policy_orchestrator() {{
    local -a subcommands
    subcommands=({' '.join([f"'{s}:{s} command'" for s in subcmds])})
    _arguments '1: :->subcmd' '*: :->args'
    case $state in
        subcmd)
            _describe 'command' subcommands
            ;;
        args)
            case $words[2] in
                exec|execute)
                    _values 'algorithm_id' {' '.join(algo_ids)}
                    ;;
                contracts)
                    _values 'category' {' '.join(categories)}
                    ;;
                *)
                    _files
                    ;;
            esac
            ;;
    esac
}}
compdef _policy_orchestrator policy-orchestrator
"""
    else:
        script = f"""# Fish completion for policy-orchestrator
complete -c policy-orchestrator -f -n '__fish_use_subcommand' -a "{' '.join(subcmds)}"
"""
    print(script)
    return 0


def handle_algo_command(args: argparse.Namespace) -> int:
    action = getattr(args, "action", None)
    if action in {"search", "scan"} and hasattr(args, "patterns"):
        return handle_search_command(args)
    elif action == "scan":
        return handle_scan_command(args)
    elif action == "outline":
        return handle_outline_command(args)
    elif action == "lint-comments":
        return handle_lint_command(args)
    elif action == "dependencies":
        return handle_deps_command(args)
    elif action == "patch":
        return handle_patch_command(args)
    elif action == "diff":
        return handle_diff_command(args)
    elif action == "contracts":
        return handle_contracts_command(args)
    elif action == "compose":
        return handle_compose_command(args)
    elif action == "execute":
        return handle_exec_command(args)
    return 0


def handle_audit_command(args: argparse.Namespace) -> int:
    audit_service = AuditService()
    summary = audit_service.run_full_audit(args.root)

    if args.json:
        print(json.dumps(asdict(summary), indent=2))
    else:
        print("\n" + "=" * 80)
        print("REPOSITORY INVARIANT & ARCHITECTURE AUDIT SUMMARY")
        print("=" * 80)
        print(f"Total Rules Checked : {summary.total_rules_checked}")
        print(f"Passed Rules        : {summary.passed_rules}")
        print(f"Failed Rules        : {summary.failed_rules}")
        print(f"Total Violations    : {summary.total_violations}")
        print(f"Audit Status        : {summary.status.upper()}")
        print("=" * 80)
        if summary.failed_rules > 0:
            print("\nRule Breakdown:")
            for report in summary.rule_reports:
                if report.status == "fail":
                    print(f"\n❌ [{report.rule_id}] {report.rule_name}")
                    for finding in report.findings[:5]:
                        print(f"   • {finding.file_path}:{finding.line_number} - {finding.message}")
        print("=" * 80 + "\n")
    return 0 if summary.failed_rules == 0 else 1


def handle_rag_command(args: argparse.Namespace) -> int:
    rag_service, _ = _init_rag_and_agent(args.rules_dir, args.backend)
    if args.action == "index":
        indexed = rag_service.index_policies()
        print(f"✅ Successfully indexed {indexed} policy rule sections into vector memory.")
        return 0
    elif args.action == "search":
        if not args.query:
            print("Error: --query is required for rag search")
            return 1
        rag_service.index_policies()
        request = RAGQueryRequest(query=args.query, category=args.category, top_k=args.top_k)
        response = rag_service.query_policies(request)
        if args.json:
            print(json.dumps(asdict(response), indent=2))
        else:
            print(f"\n{'='*75}")
            print(f"🔍 RAG RETRIEVAL: {len(response.results)} matches for '{args.query}'")
            print(f"{'='*75}\n")
            for i, match in enumerate(response.results, 1):
                print(f"[{i}] {match.rule_title} (Similarity: {match.similarity_score:.3f})")
                print(f"    Source: {match.source_file}")
                print(f"    Content Preview: {match.content[:150]}...\n")
        return 0
    return 0


def handle_agent_command(args: argparse.Namespace) -> int:
    _, agent_service = _init_rag_and_agent(args.rules_dir, args.backend)
    req = AgentExecutionRequest(task_prompt=args.prompt, target_directory=args.target_dir, max_steps=args.max_steps)
    res = agent_service.execute_task(req)
    if args.json:
        print(json.dumps(asdict(res), indent=2))
    else:
        print(f"\n{'='*75}")
        print(f"🤖 AGENT WORKFLOW COMPLETED: Status = {res.status.upper()}")
        print(f"{'='*75}")
        print(f"Summary: {res.summary}\n")
        print("Reasoning Trajectory:")
        for step in res.trajectory:
            print(f"  Step {step.step_number}: {step.action_type} -> Tool: {step.tool_name}")
            print(f"    Thought: {step.thought}")
            if step.tool_output:
                preview = str(step.tool_output)[:120].replace('\n', ' ')
                print(f"    Result: {preview}...")
        print(f"{'='*75}\n")
    return 0 if res.status == "success" else 1


def handle_refactor_command(args: argparse.Namespace) -> int:
    service = RefactorService()
    extensions = [ext.strip() for ext in args.ext.split(",") if ext.strip()]
    res = service.execute_batch_refactor(
        root_dir=args.root,
        find_pattern=args.find,
        replace_text=args.replace,
        allowed_extensions=extensions,
        is_regex=args.regex,
        dry_run=not args.apply,
    )
    if args.json:
        print(json.dumps(asdict(res), indent=2))
    else:
        mode = "APPLIED" if args.apply else "DRY-RUN (Simulated)"
        print(f"\n{'='*75}")
        print(f"🔄 BATCH REFACTOR SUMMARY [{mode}]")
        print(f"{'='*75}")
        print(f"Files Scanned   : {res.total_files_scanned}")
        print(f"Files Modified  : {res.total_files_modified}")
        print(f"Total Matches   : {res.total_occurrences_replaced}")
        print(f"{'='*75}\n")
    return 0


def handle_policy_check_command(args: argparse.Namespace) -> int:
    sync_service = PolicySyncService()
    violations = sync_service.audit_contract_file(args.path)
    if args.json:
        print(json.dumps([asdict(v) for v in violations], indent=2))
    else:
        print(f"\n{'='*75}")
        print(f"📋 POLICY CONTRACT AUDIT: {len(violations)} Violations in {args.path}")
        print(f"{'='*75}")
        if not violations:
            print("✅ All algorithm entries strictly conform to the engineering contract standard.")
        else:
            for v in violations:
                print(f"  ❌ Line {v.line_number}: [{v.rule_id}] {v.message}")
        print(f"{'='*75}\n")
    return 0 if len(violations) == 0 else 1


def handle_migrate_command(args: argparse.Namespace) -> int:
    runner = DatabaseMigrationRunner()
    if getattr(args, "action", "run") == "run":
        db_target = getattr(args, "db", "sqlite")
        if db_target == "sqlite":
            res = runner.run_sqlite_migrations(getattr(args, "sqlite_path", "policy_registry.db"))
        else:
            res = runner.run_postgres_migrations(getattr(args, "postgres_url", "postgresql://postgres:postgres@localhost:5432/postgres"))
        print(f"✅ Migration successful: Applied {res.get('applied_migrations')} migrations, Seeded {res.get('seeded_algorithms')} algorithms.")
        return 0
    elif getattr(args, "action", "") == "status":
        status = runner.get_migration_status(getattr(args, "sqlite_path", None) if getattr(args, "db", "sqlite") == "sqlite" else None)
        print(json.dumps(status, indent=2))
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
        description="Repository Invariant Auditor, Layer 1 Algorithm Suite & Policy Orchestrator",
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # 1. Search Subcommand
    search_p = subparsers.add_parser("search", help="Fast multi-pattern code search (ALGO-SRCH-03 + 11 + 14)")
    search_p.add_argument("patterns", nargs="?", default="TODO,FIXME,error,critical", help="Comma-separated patterns to find")
    search_p.add_argument("directory", nargs="?", default=".", help="Target directory (default: current)")
    search_p.add_argument("--patterns", dest="patterns_flag", default=None, help="Explicit --patterns flag")
    search_p.add_argument("--directory", "--root", dest="dir_flag", default=None, help="Explicit directory flag")
    search_p.add_argument("--json", action="store_true", help="Output as JSON")

    # 2. Scan Subcommand
    scan_p = subparsers.add_parser("scan", help="Recursive repository file tree discovery (ALGO-SRCH-01/02)")
    scan_p.add_argument("directory", nargs="?", default=".", help="Root directory (default: .)")
    scan_p.add_argument("--root", dest="root_flag", default=None, help="Explicit --root flag")
    scan_p.add_argument("--json", action="store_true", help="Output as JSON")

    # 3. Outline Subcommand
    outline_p = subparsers.add_parser("outline", help="Hierarchical AST symbol outline (ALGO-OBS-17 + 21)")
    outline_p.add_argument("file", nargs="?", default=None, help="Source code file path")
    outline_p.add_argument("--file", dest="file_flag", default=None, help="Explicit --file flag")
    outline_p.add_argument("--json", action="store_true", help="Output as JSON")

    # 4. Lint Subcommand
    lint_p = subparsers.add_parser("lint", help="Zero-Inline-Comment doctrine compliance linter (ALGO-OBS-19)")
    lint_p.add_argument("file", nargs="?", default=None, help="Source code file path")
    lint_p.add_argument("--file", dest="file_flag", default=None, help="Explicit --file flag")
    lint_p.add_argument("--json", action="store_true", help="Output as JSON")

    # 5. Dependencies / Deps Subcommand
    deps_p = subparsers.add_parser("deps", aliases=["dependencies"], help="Module import dependency graph & cycle detector (ALGO-OBS-20)")
    deps_p.add_argument("directory", nargs="?", default="src", help="Target source directory")
    deps_p.add_argument("--directory", dest="dir_flag", default=None, help="Explicit directory flag")
    deps_p.add_argument("--json", action="store_true", help="Output as JSON")

    # 6. Diff Subcommand
    diff_p = subparsers.add_parser("diff", help="Unified context diff generator (ALGO-UPD-24)")
    diff_p.add_argument("file", nargs="?", default=None, help="File to inspect")
    diff_p.add_argument("find", nargs="?", default="", help="Pattern to match")
    diff_p.add_argument("replace", nargs="?", default="", help="Replacement string")
    diff_p.add_argument("--file", dest="file_flag", default=None, help="Explicit --file flag")
    diff_p.add_argument("--find", dest="find_flag", default=None, help="Explicit --find flag")
    diff_p.add_argument("--replace", dest="replace_flag", default=None, help="Explicit --replace flag")
    diff_p.add_argument("--regex", action="store_true", help="Treat pattern as regex")
    diff_p.add_argument("--json", action="store_true", help="Output as JSON")

    # 7. Patch Subcommand
    patch_p = subparsers.add_parser("patch", help="AST/CST atomic batch patcher (ALGO-UPD-22/23)")
    patch_p.add_argument("file", nargs="?", default=None, help="File to patch")
    patch_p.add_argument("find", nargs="?", default="", help="Pattern to match")
    patch_p.add_argument("replace", nargs="?", default="", help="Replacement string")
    patch_p.add_argument("--file", dest="file_flag", default=None, help="Explicit --file flag")
    patch_p.add_argument("--find", dest="find_flag", default=None, help="Explicit --find flag")
    patch_p.add_argument("--replace", dest="replace_flag", default=None, help="Explicit --replace flag")
    patch_p.add_argument("--apply", action="store_true", help="Apply mutations to disk (default is dry-run)")
    patch_p.add_argument("--regex", action="store_true", help="Treat pattern as regex")
    patch_p.add_argument("--json", action="store_true", help="Output as JSON")

    # 8. Exec Subcommand
    exec_p = subparsers.add_parser("exec", aliases=["execute"], help="Direct universal algorithm execution across all 42 algos")
    exec_p.add_argument("id", nargs="?", default=None, help="Algorithm ID (e.g. ALGO-VEC-01, ALGO-GRAPH-01, ALGO-SRCH-11)")
    exec_p.add_argument("input", nargs="?", default="{}", help="Input payload JSON string or @filepath")
    exec_p.add_argument("--id", dest="id_flag", default=None, help="Explicit --id flag")
    exec_p.add_argument("--input", dest="input_flag", default=None, help="Explicit --input flag")
    exec_p.add_argument("--json", action="store_true", help="Output as JSON")

    # 9. Contracts Subcommand
    contracts_p = subparsers.add_parser("contracts", help="List and filter Layer 1 Algorithm Contracts")
    contracts_p.add_argument("--category", choices=["search", "observability", "update", "vector", "graph"], default=None, help="Filter by category")
    contracts_p.add_argument("--tag", default=None, help="Filter by capability tag")
    contracts_p.add_argument("--json", action="store_true", help="Output as JSON")

    # 10. Compose Subcommand
    compose_p = subparsers.add_parser("compose", help="Compose dynamic DAG pipeline from algorithm IDs")
    compose_p.add_argument("algos", nargs="?", default="ALGO-SRCH-03,ALGO-OBS-17,ALGO-UPD-23", help="Comma-separated algorithm IDs")
    compose_p.add_argument("--algos", dest="algos_flag", default=None, help="Explicit --algos flag")
    compose_p.add_argument("--json", action="store_true", help="Output as JSON")

    # 11. Run Subcommand (human-friendly alias runner)
    run_p = subparsers.add_parser("run", help="Run any algorithm by its human-friendly name (e.g. bfs, dijkstra, normalize, chunk)")
    run_p.add_argument("alias", nargs="?", default=None, help="Human-friendly algorithm name (run `policy-orchestrator list` to see all)")
    run_p.add_argument("input", nargs="?", default="{}", help="Input as JSON string or @filepath")
    run_p.add_argument("--alias", dest="alias_flag", default=None, help="Explicit --alias flag")
    run_p.add_argument("--input", dest="input_flag", default=None, help="Explicit --input flag")
    run_p.add_argument("--json", action="store_true", help="Output as JSON")

    # 12. List Subcommand (human-friendly discovery)
    list_p = subparsers.add_parser("list", help="List every algorithm with plain-English names and descriptions")
    list_p.add_argument("--category", choices=["search", "observability", "update", "vector", "graph"], default=None, help="Filter by category")
    list_p.add_argument("--json", action="store_true", help="Output full detail as JSON")

    # 13. Completion Subcommand
    comp_p = subparsers.add_parser("completion", help="Generate shell auto-completion script (bash, zsh, fish)")
    comp_p.add_argument("shell", choices=["bash", "zsh", "fish"], default="bash", nargs="?", help="Target shell")

    # 12. Legacy Algo Subcommand (Backwards Compatibility)
    algo_parser = subparsers.add_parser("algo", help="Execute Categorized Search, Observability, Update & Vector Algorithms")
    algo_parser.add_argument("action", choices=["search", "scan", "outline", "lint-comments", "dependencies", "patch", "diff", "contracts", "compose", "execute"], help="Algorithm action")
    algo_parser.add_argument("--id", default=None, help="Algorithm ID to execute")
    algo_parser.add_argument("--input", default="{}", help="Input payload JSON string or @filepath")
    algo_parser.add_argument("--root", default=".", help="Root directory")
    algo_parser.add_argument("--patterns", default="TODO,FIXME,error,critical", help="Comma-separated patterns")
    algo_parser.add_argument("--file", default="src/api/cli/main.py", help="File to inspect or patch")
    algo_parser.add_argument("--directory", default="src", help="Directory to analyze")
    algo_parser.add_argument("--find", default="", help="Pattern to find for update/diff/patch")
    algo_parser.add_argument("--replace", default="", help="Replacement string for update/diff/patch")
    algo_parser.add_argument("--regex", action="store_true", help="Treat find pattern as regex")
    algo_parser.add_argument("--apply", action="store_true", help="Apply patch modifications to disk")
    algo_parser.add_argument("--category", default=None, help="Filter contracts by category")
    algo_parser.add_argument("--algos", default="ALGO-SRCH-03,ALGO-OBS-17,ALGO-UPD-23", help="Comma-separated algorithm IDs to compose")
    algo_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Standard existing commands
    audit_parser = subparsers.add_parser("audit", help="Run multi-vector invariant scan")
    audit_parser.add_argument("--root", default=".", help="Root directory")
    audit_parser.add_argument("--json", action="store_true", help="Output findings as JSON")

    migrate_parser = subparsers.add_parser("migrate", help="Run database migrations and seed algorithm contracts")
    migrate_parser.add_argument("action", choices=["run", "status"], default="run", nargs="?", help="Migration action")
    migrate_parser.add_argument("--db", choices=["sqlite", "alloydb", "postgres"], default="sqlite", help="Target database")
    migrate_parser.add_argument("--sqlite-path", default="policy_registry.db", help="SQLite database path")
    migrate_parser.add_argument("--postgres-url", default="postgresql://postgres:postgres@localhost:5432/postgres", help="PostgreSQL connection string")

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

    # Normalise flags vs positional shortcuts
    if hasattr(args, "patterns_flag") and args.patterns_flag:
        args.patterns = args.patterns_flag
    if hasattr(args, "dir_flag") and args.dir_flag:
        args.directory = args.dir_flag
    if hasattr(args, "root_flag") and args.root_flag:
        args.root = args.root_flag
    if hasattr(args, "file_flag") and args.file_flag:
        args.file = args.file_flag
    if hasattr(args, "find_flag") and args.find_flag:
        args.find = args.find_flag
    if hasattr(args, "replace_flag") and args.replace_flag:
        args.replace = args.replace_flag
    if hasattr(args, "id_flag") and args.id_flag:
        args.id = args.id_flag
    if hasattr(args, "input_flag") and args.input_flag:
        args.input = args.input_flag
    if hasattr(args, "algos_flag") and args.algos_flag:
        args.algos = args.algos_flag

    if hasattr(args, "alias_flag") and args.alias_flag:
        args.alias = args.alias_flag

    dispatch = {
        "search": handle_search_command,
        "scan": handle_scan_command,
        "outline": handle_outline_command,
        "lint": handle_lint_command,
        "deps": handle_deps_command,
        "dependencies": handle_deps_command,
        "diff": handle_diff_command,
        "patch": handle_patch_command,
        "exec": handle_exec_command,
        "execute": handle_exec_command,
        "run": handle_run_command,
        "list": handle_list_command,
        "contracts": handle_contracts_command,
        "compose": handle_compose_command,
        "completion": handle_completion_command,
        "algo": handle_algo_command,
        "audit": handle_audit_command,
        "migrate": handle_migrate_command,
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
