"""ALGORITHM & ARCHITECTURE BLUEPRINT: CHAITIN-BRIGGS REGISTER ALLOCATION (ALGO-GRAPH-SYS-301)

1. OVERVIEW & OBJECTIVE
Assigns variables/virtual registers to a limited pool of K physical hardware registers via interference
graph coloring. Implements the Chaitin-Briggs Kempe-heuristic simplification loop: (1) Simplify: iteratively
push vertices with degree < K onto an elimination stack; (2) Optimistic Spill: when all degrees >= K, push candidate
spill nodes optimistically; (3) Select: pop vertices and assign available non-conflicting colors, spilling to memory only if truly blocked.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V| + |E|) interference graph and elimination stack.
- Time Complexity: O(|V|^2 + |E|) per simplification-selection allocation round.
- Invariants:
  - If u and v interfere (connected by an edge), color(u) != color(v).
  - Number of assigned distinct colors is strictly bounded by parameter k_registers.

3. INPUT PARAMETERS:
- interference_adjacency: Mapping[TNode, Collection[TNode]] variable interference graph topology.
- k_registers: int number of physical registers / colors available.
- spill_costs: Optional[Mapping[TNode, float]] loop-nesting weighted spill penalty heuristic.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'register_allocation': Dict[TNode, int] assigned physical register ID (0 to K-1) for allocated variables.
  - 'spilled_variables': Set[TNode] variables that must be spilled to memory / stack slots.
  - 'num_spills': int total spill count.
  - 'is_successful': bool True if zero variables were spilled.

5. AGENT CONTRACT:
- Strict zero-inline-comment doctrine.
- Generic node typing via `TNode`.
"""

from __future__ import annotations

from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoChaitinBriggsRegisterAllocation(Generic[TNode]):
    """Chaitin-Briggs optimistic graph coloring register allocation engine.

    ```yaml
    contract:
      id: ALGO-GRAPH-SYS-301
      name: GraphAlgoChaitinBriggsRegisterAllocation
      inputs:
        - name: interference_adjacency
          type: Mapping[TNode, Collection[TNode]]
          description: Interference graph where edges represent overlapping live ranges.
        - name: k_registers
          type: int
          description: Available physical register count K.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Physical register assignments, spilled variables, and success status.
      parameters:
        spill_costs: Optional[Mapping[TNode, float]] (default None)
      capability_tags:
        - COMPILER_OPT
        - REGISTER_ALLOCATION
        - GRAPH_COLORING
        - CHAITIN_BRIGGS
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(|V|^2 + |E|)
        space: O(|V| + |E|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        interference_adjacency: Mapping[TNode, Collection[TNode]],
        k_registers: int,
        spill_costs: Optional[Mapping[TNode, float]] = None,
    ) -> Dict[str, Any]:
        """Executes Chaitin-Briggs simplification, optimistic spilling, and selection."""
        all_nodes = list(interference_adjacency.keys())
        if not all_nodes or k_registers <= 0:
            return {
                "register_allocation": {},
                "spilled_variables": set(all_nodes),
                "num_spills": len(all_nodes),
                "is_successful": len(all_nodes) == 0,
            }

        costs = spill_costs if spill_costs is not None else {u: 1.0 for u in all_nodes}

        adj: Dict[TNode, Set[TNode]] = {
            u: set(interference_adjacency.get(u, [])) for u in all_nodes
        }
        degrees: Dict[TNode, int] = {u: len(adj[u]) for u in all_nodes}
        removed: Set[TNode] = set()
        stack: List[TNode] = []

        remaining_count = len(all_nodes)

        while remaining_count > 0:
            low_degree_nodes = [
                u for u in all_nodes if u not in removed and degrees[u] < k_registers
            ]

            if low_degree_nodes:
                low_degree_nodes.sort(key=lambda u: degrees[u])
                v = low_degree_nodes[0]
                removed.add(v)
                stack.append(v)
                remaining_count -= 1
                for nbr in adj[v]:
                    if nbr not in removed:
                        degrees[nbr] -= 1
            else:
                high_degree_nodes = [u for u in all_nodes if u not in removed]
                high_degree_nodes.sort(
                    key=lambda u: costs.get(u, 1.0) / max(1, degrees[u])
                )
                v = high_degree_nodes[0]
                removed.add(v)
                stack.append(v)
                remaining_count -= 1
                for nbr in adj[v]:
                    if nbr not in removed:
                        degrees[nbr] -= 1

        color_assignment: Dict[TNode, int] = {}
        spilled: Set[TNode] = set()

        while stack:
            u = stack.pop()
            neighbor_colors = {
                color_assignment[nbr]
                for nbr in adj[u]
                if nbr in color_assignment
            }

            available_color = None
            for c in range(k_registers):
                if c not in neighbor_colors:
                    available_color = c
                    break

            if available_color is not None:
                color_assignment[u] = available_color
            else:
                spilled.add(u)

        return {
            "register_allocation": color_assignment,
            "spilled_variables": spilled,
            "num_spills": len(spilled),
            "is_successful": len(spilled) == 0,
        }
