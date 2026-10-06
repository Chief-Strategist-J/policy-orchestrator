"""
================================================================================
ALGORITHM BLUEPRINT: STACK GRAPH INCREMENTAL NAME RESOLUTION
================================================================================

1. OVERVIEW:
   Stack Graphs are modular, zero-build name resolution graph fragments (GitHub code
   navigation model). Each source file produces an isolated graph fragment with
   'push' symbol and 'pop' symbol edges. At query time, paths are stitched together
   across file boundaries, evaluating push and pop labels like a stack automaton
   to resolve qualified symbol paths (`pkg.module.Class.method`) incrementally.

2. STACK AUTOMATON RULES:
   - Push Edge: Pushes symbol token S onto resolution symbol stack.
   - Pop Edge: Pops matching symbol token S from top of stack.
   - Valid Path: A path from reference to definition is valid iff the symbol stack
     is empty (or matches initial prefix) upon reaching the target declaration.

3. COMPLEXITY ANALYSIS:
   - Incremental Cost: O(1) file rebuild on edit.
   - Query: O(Path_Length) push/pop path evaluation.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, List, Any, Optional, Tuple, Set


class StackGraphEdge:
    def __init__(self, source: str, target: str, action: str = "pass", symbol: str = "") -> None:
        self.source: str = source
        self.target: str = target
        self.action: str = action
        self.symbol: str = symbol


class SearchEngineStackGraphAlgo:
    """
    --- contract:
      id: ALGO-SRCH-86
      name: SearchEngineStackGraphAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(Paths)
        space: O(Nodes + Edges)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - stack.graph
      - name_resolution.interprocedural
      - scope.stack
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def __init__(self) -> None:
        self._edges: List[StackGraphEdge] = []

    def add_edge(self, source: str, target: str, action: str = "pass", symbol: str = "") -> None:
        self._edges.append(StackGraphEdge(source, target, action, symbol))

    def resolve_path(self, start_node: str, target_node: str, max_depth: int = 20) -> Optional[List[str]]:
        queue: List[Tuple[str, List[str], List[str]]] = [(start_node, [], [start_node])]
        visited_states: Set[Tuple[str, Tuple[str, ...]]] = set()

        while queue:
            curr_node, symbol_stack, path = queue.pop(0)
            state_key = (curr_node, tuple(symbol_stack))
            if state_key in visited_states:
                continue
            visited_states.add(state_key)

            if curr_node == target_node and len(symbol_stack) == 0:
                return path

            if len(path) > max_depth:
                continue

            for edge in self._edges:
                if edge.source == curr_node:
                    new_stack = list(symbol_stack)
                    valid_transition = True

                    if edge.action == "push":
                        new_stack.append(edge.symbol)
                    elif edge.action == "pop":
                        if new_stack and new_stack[-1] == edge.symbol:
                            new_stack.pop()
                        elif not new_stack:
                            valid_transition = False
                        else:
                            valid_transition = False

                    if valid_transition:
                        queue.append((edge.target, new_stack, path + [edge.target]))

        return None

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        edges_raw = payload.get("edges", [])
        start = str(payload.get("start_node", "ref"))
        target = str(payload.get("target_node", "def"))

        self._edges = []
        for e in edges_raw:
            self.add_edge(
                source=str(e.get("source")),
                target=str(e.get("target")),
                action=str(e.get("action", "pass")),
                symbol=str(e.get("symbol", ""))
            )

        resolved_path = self.resolve_path(start, target)

        return {
            "algorithm": "ALGO-SRCH-89",
            "start_node": start,
            "target_node": target,
            "is_resolved": resolved_path is not None,
            "resolution_path": resolved_path,
            "total_edges": len(self._edges)
        }
