"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: EPIDEMIC SIR & SIS SPREADING (ALGO-GRAPH-MODEL-146)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Stochastic epidemic spreading simulator on complex graphs (SIR and SIS models).
   Simulates infection along contact edges with rate beta and recovery with rate gamma.
   Tracks continuous or discrete-time infection trajectories, epidemic threshold,
   peak infected fraction, and final epidemic outbreak size.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(events * (deg_avg + log V)) stochastic simulation.
   - Space Complexity: O(V) node compartment states.
   - Purity: Pure functional transformation, deterministic with fixed RNG seed.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Contact network adjacency list.
   - initial_infected: List[TNode] - Seed patient-zero infected vertices.
   - beta_infection: float - Infection rate along contact edges in [0.0, 1.0] (default: 0.3).
   - gamma_recovery: float - Recovery rate in [0.0, 1.0] (default: 0.1).
   - model_type: str - 'SIR' or 'SIS' (default: 'SIR').
   - max_steps: int - Maximum simulation time steps (default: 50).
   - rng_seed: int - Deterministic random seed (default: 42).

4. OUTPUT PARAMETERS:
   - final_infected_count: int - Total individuals infected over course of epidemic.
   - peak_infected_count: int - Maximum simultaneously infected individuals.
   - final_states: Dict[TNode, str] - Final state per node ('S', 'I', or 'R').
   - trajectory: List[Dict[str, int]] - State count history at each step [{'S': ..., 'I': ..., 'R': ...}].

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: beta and gamma rates in [0.0, 1.0].
   - Guardrails: Recovered individuals in SIR remain permanently immune.
================================================================================
"""

import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoEpidemicSirSis(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-MODEL-146
      name: GraphAlgoEpidemicSirSis
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, random_models, epidemics, sir_model, sis_model, infection_spreading, gillespie]
      inputs:
        type: object
        required: [adjacency, initial_infected]
        properties:
          adjacency: {type: object}
          initial_infected: {type: array, items: {type: string}}
          beta_infection: {type: number, default: 0.3}
          gamma_recovery: {type: number, default: 0.1}
          model_type: {type: string, default: SIR}
          max_steps: {type: integer, default: 50}
          rng_seed: {type: integer, default: 42}
      outputs:
        type: object
        required: [final_infected_count, peak_infected_count, final_states, trajectory]
        properties:
          final_infected_count: {type: integer}
          peak_infected_count: {type: integer}
          final_states: {type: object}
          trajectory: {type: array, items: {type: object}}
      parameters:
        beta_infection: {type: number, default: 0.3}
        gamma_recovery: {type: number, default: 0.1}
        model_type: {type: string, default: SIR}
        max_steps: {type: integer, default: 50}
        rng_seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(T * (V + E))
        space: O(V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        initial_infected: List[TNode],
        beta_infection: float = 0.3,
        gamma_recovery: float = 0.1,
        model_type: str = "SIR",
        max_steps: int = 50,
        rng_seed: int = 42,
    ) -> None:
        """
        Initialize the Epidemic Spreading simulator.

        Args:
            adjacency: Graph adjacency dictionary.
            initial_infected: Initial seeds in compartment 'I'.
            beta_infection: Edge transmission probability.
            gamma_recovery: Node recovery probability.
            model_type: 'SIR' or 'SIS'.
            max_steps: Maximum step limit.
            rng_seed: Deterministic random seed.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._init_i: Set[TNode] = set(initial_infected)
        self._beta: float = beta_infection
        self._gamma: float = gamma_recovery
        self._model: str = model_type.upper()
        self._max_steps: int = max_steps
        self._rng_seed: int = rng_seed
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def simulate_epidemic(self) -> Tuple[int, int, Dict[TNode, str], List[Dict[str, int]]]:
        """
        Simulate discrete-time Markovian epidemic spreading.

        Returns:
            Tuple of (total_ever_infected, peak_simultaneous_infected, final_states_dict, trajectory_history).
        """
        rng = random.Random(self._rng_seed)
        states: Dict[TNode, str] = {u: "I" if u in self._init_i else "S" for u in self._nodes}
        ever_infected: Set[TNode] = set(self._init_i)

        peak_i: int = len(self._init_i)
        trajectory: List[Dict[str, int]] = []

        for _ in range(self._max_steps):
            s_count = sum(1 for s in states.values() if s == "S")
            i_count = sum(1 for s in states.values() if s == "I")
            r_count = sum(1 for s in states.values() if s == "R")
            trajectory.append({"S": s_count, "I": i_count, "R": r_count})

            if i_count > peak_i:
                peak_i = i_count

            if i_count == 0:
                break

            next_states = dict(states)

            for u in self._nodes:
                if states[u] == "I":
                    for v in self._adj.get(u, set()):
                        if states[v] == "S" and next_states[v] == "S":
                            if rng.random() <= self._beta:
                                next_states[v] = "I"
                                ever_infected.add(v)

                    if rng.random() <= self._gamma:
                        next_states[u] = "R" if self._model == "SIR" else "S"

            states = next_states

        return len(ever_infected), peak_i, states, trajectory
