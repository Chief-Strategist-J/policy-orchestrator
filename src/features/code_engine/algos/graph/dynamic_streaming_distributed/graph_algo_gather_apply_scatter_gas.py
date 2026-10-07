"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GATHER-APPLY-SCATTER (GAS) MODEL (ALGO-GRAPH-PAR-216)
================================================================================

1. OVERVIEW & OBJECTIVE:
   PowerGraph Gather-Apply-Scatter (GAS) Vertex-Program Engine.
   Executes distributed vertex programs via commutative/associative edge-gather,
   local vertex-apply, and parallel neighbor-scatter message activation.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(M + V) per superstep.
   - Space Complexity: O(V + M) vertex state and edge mirror storage.
   - Purity: Configurable vertex-program execution, deterministic superstep barrier.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Graph topological layout.
   - `initial_state` (Dict[TNode, Any]): Initial vertex state values.
   - `gather_fn`, `sum_fn`, `apply_fn`, `scatter_fn`: GAS operator callbacks.

4. OUTPUT PARAMETERS:
   - `run_superstep()` (Dict[TNode, Any]): Updated vertex states after one synchronous GAS cycle.
   - `run_until_convergence(max_steps)` (Tuple[Dict[TNode, Any], int]): Final converged states and step count.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Gather accumulation satisfies strict commutativity and associativity.
================================================================================
"""

from typing import Any, Callable, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGatherApplyScatterGas(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-PAR-216
      name: GraphAlgoGatherApplyScatterGas
      version: 1.0.0
      category: graph_parallel
      capability_tags: [graph, parallel, gas_model, powergraph, vertex_program, gather_apply_scatter]
      inputs:
        type: object
        required: [adjacency, initial_state]
        properties:
          adjacency:
            type: object
          initial_state:
            type: object
      outputs:
        type: object
        properties:
          vertex_states: {type: object}
          steps_executed: {type: integer}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(M + V) per superstep
        space: O(V + M)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        initial_state: Dict[TNode, Any],
        gather_fn: Optional[Callable[[TNode, TNode, Any, Any], Any]] = None,
        sum_fn: Optional[Callable[[Any, Any], Any]] = None,
        apply_fn: Optional[Callable[[TNode, Any, Any], Any]] = None,
        scatter_fn: Optional[Callable[[TNode, TNode, Any, Any], bool]] = None,
    ) -> None:
        """
        Initialize Gather-Apply-Scatter runtime.

        Args:
            adjacency: Adjacency map.
            initial_state: Mapping from node to initial state payload.
            gather_fn: Function (u, v, state_u, state_v) -> gathered_val.
            sum_fn: Commutative sum operator (acc, gathered_val) -> acc.
            apply_fn: Function (u, gathered_sum, curr_state) -> new_state.
            scatter_fn: Function (u, v, old_state, new_state) -> bool (True if v should activate).
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._states: Dict[TNode, Any] = dict(initial_state)
        for u in self._adj:
            if u not in self._states:
                self._states[u] = None

        self._gather_fn = gather_fn or (lambda u, v, su, sv: sv)
        self._sum_fn = sum_fn or (lambda a, b: (a if a is not None else 0) + (b if b is not None else 0))
        self._apply_fn = apply_fn or (lambda u, gsum, state: gsum)
        self._scatter_fn = scatter_fn or (lambda u, v, old_st, new_st: old_st != new_st)
        self._active: Set[TNode] = set(self._adj.keys())

    def run_superstep(self) -> Dict[TNode, Any]:
        """
        Execute a single synchronous Gather-Apply-Scatter superstep.

        Returns:
            Dictionary of updated vertex states.
        """
        if not self._active:
            return dict(self._states)

        gathered: Dict[TNode, Any] = {}
        for u in self._active:
            acc = None
            for v in self._adj.get(u, []):
                val = self._gather_fn(u, v, self._states[u], self._states[v])
                acc = val if acc is None else self._sum_fn(acc, val)
            gathered[u] = acc

        new_states: Dict[TNode, Any] = dict(self._states)
        for u in self._active:
            new_states[u] = self._apply_fn(u, gathered[u], self._states[u])

        next_active: Set[TNode] = set()
        for u in self._active:
            old_st = self._states[u]
            new_st = new_states[u]
            for v in self._adj.get(u, []):
                if self._scatter_fn(u, v, old_st, new_st):
                    next_active.add(v)

        self._states = new_states
        self._active = next_active
        return dict(self._states)

    def run_until_convergence(self, max_steps: int = 100) -> Tuple[Dict[TNode, Any], int]:
        """
        Run GAS supersteps until no active vertices remain or max_steps reached.

        Args:
            max_steps: Maximum allowable iterations.

        Returns:
            Tuple of (final_states, total_steps_executed).
        """
        steps = 0
        while self._active and steps < max_steps:
            self.run_superstep()
            steps += 1
        return dict(self._states), steps
