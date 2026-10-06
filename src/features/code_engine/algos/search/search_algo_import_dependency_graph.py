"""
================================================================================
ALGORITHM BLUEPRINT: MODULE IMPORT DEPENDENCY GRAPH & TOPOLOGICAL ORDERING
================================================================================

1. OVERVIEW:
   Constructs a directed dependency graph of module imports (`import A`, `from B import C`).
   Detects circular dependency cycles (SCCs), calculates reverse downstream dependencies
   (who depends on module X), and computes safe topological ordering for staged
   refactoring and build executions.

2. GRAPH TOPOLOGY & RESOLUTION:
   - Forward Dependency: Module A -> Module B (A depends on B).
   - Reverse Dependency: Module B <- Module A (Affecting B impacts A).
   - Cycle Detection: Tarjan / DFS recursion stack cycle detection.
   - Topological Order: Kahn's in-degree algorithm for build scheduling.

3. COMPLEXITY ANALYSIS:
   - Graph Extraction: O(Files * Imports).
   - Topological Sort: O(V + E) linear time.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import ast
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional, Set, Tuple


class SearchEngineImportDependencyGraphAlgo:
    """
    --- contract:
      id: ALGO-SRCH-90
      name: SearchEngineImportDependencyGraphAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(Files + Imports)
        space: O(Graph)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - graph.dependency
      - imports.dag
      - cycle.detection
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def __init__(self) -> None:
        self._adj: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_adj: Dict[str, Set[str]] = defaultdict(set)
        self._modules: Set[str] = set()

    def add_dependency(self, importer: str, imported: str) -> None:
        self._modules.add(importer)
        self._modules.add(imported)
        self._adj[importer].add(imported)
        self._reverse_adj[imported].add(importer)

    def extract_from_file_code(self, module_name: str, code: str) -> None:
        self._modules.add(module_name)
        try:
            tree = ast.parse(code)
        except Exception:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.add_dependency(module_name, alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.add_dependency(module_name, node.module)

    def detect_cycles(self) -> List[List[str]]:
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycles: List[List[str]] = []
        path: List[str] = []

        def _dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self._adj.get(node, set()):
                if neighbor not in visited:
                    _dfs(neighbor)
                elif neighbor in rec_stack:
                    idx = path.index(neighbor)
                    cycles.append(path[idx:] + [neighbor])

            rec_stack.remove(node)
            path.pop()

        for m in sorted(list(self._modules)):
            if m not in visited:
                _dfs(m)

        return cycles

    def topological_sort(self) -> List[str]:
        in_degree: Dict[str, int] = {m: 0 for m in self._modules}
        for src, targets in self._adj.items():
            for tgt in targets:
                in_degree[tgt] = in_degree.get(tgt, 0) + 1

        queue: deque = deque([m for m, deg in in_degree.items() if deg == 0])
        order: List[str] = []

        while queue:
            curr = queue.popleft()
            order.append(curr)
            for neighbor in self._adj.get(curr, set()):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return order

    def find_affected_downstream(self, module_name: str) -> List[str]:
        visited: Set[str] = set()
        queue = [module_name]
        while queue:
            curr = queue.pop(0)
            for parent in self._reverse_adj.get(curr, set()):
                if parent not in visited:
                    visited.add(parent)
                    queue.append(parent)
        return sorted(list(visited))

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        files_data = payload.get("files", {})
        raw_deps = payload.get("dependencies", [])
        target_mod = payload.get("target_module")

        self._adj = defaultdict(set)
        self._reverse_adj = defaultdict(set)
        self._modules = set()

        for mod_name, code in files_data.items():
            self.extract_from_file_code(str(mod_name), str(code))

        for dep in raw_deps:
            if isinstance(dep, dict):
                self.add_dependency(str(dep.get("importer")), str(dep.get("imported")))
            elif isinstance(dep, (list, tuple)) and len(dep) >= 2:
                self.add_dependency(str(dep[0]), str(dep[1]))

        cycles = self.detect_cycles()
        topo_order = self.topological_sort() if not cycles else []
        downstream = self.find_affected_downstream(str(target_mod)) if target_mod else []

        return {
            "algorithm": "ALGO-SRCH-93",
            "total_modules": len(self._modules),
            "has_cycles": len(cycles) > 0,
            "cycles": cycles,
            "topological_order": topo_order,
            "target_module": target_mod,
            "affected_downstream_modules": downstream,
            "affected_count": len(downstream)
        }
