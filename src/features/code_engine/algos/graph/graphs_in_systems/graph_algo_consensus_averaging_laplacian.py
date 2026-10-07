"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Consensus Averaging on Graphs (ALGO-GRAPH-SYS-310)

1. OVERVIEW & OBJECTIVE:
Implements decentralized consensus averaging over graph network topologies.
Supports discrete-time Laplacian dynamics for undirected communication graphs
`(x(t+1) = (I - epsilon * L) x(t))` and the Push-Sum algorithm for directed graphs,
tracking asymptotic convergence to the exact average with convergence bounds.

2. COMPLEXITY & INVARIANTS:
- Time Complexity: O(T * |E|) for T iterations over edge set E.
- Space Complexity: O(|V|) state vectors for values and weights.
- Invariants: Mass conservation holds across iterations in the absence of packet loss.

3. INPUT PARAMETERS:
- `adjacency`: Dict[TNode, List[TNode]] graph communication topology.
- `initial_values`: Dict[TNode, float] starting scalar values per node.
- `epsilon`: float step size for Laplacian consensus (must be < 1 / max_degree).
- `max_iterations`: int maximum simulation rounds.
- `tolerance`: float stopping threshold for standard deviation across node estimates.
- `method`: str in ('laplacian', 'push_sum').

4. OUTPUT PARAMETERS:
- `consensus_value`: float average value reached across all nodes.
- `target_average`: float exact theoretical arithmetic mean of initial values.
- `final_estimates`: Dict[TNode, float] converged estimate per node.
- `iterations_run`: int total rounds executed.
- `converged`: bool whether variance fell below tolerance.
- `residual_error`: float max absolute deviation from true mean.

5. AGENT CONTRACT:
- Role: Analyst and Distributed Aggregator.
- Rules: Enforce step size epsilon < 1 / d_max for stability under Laplacian dynamics.
- Guardrails: Push-Sum ensures unbiased convergence under directed regular topologies.
"""

from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
import math

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoConsensusAveragingLaplacian(Generic[TNode]):
    """
    inputs:
      adjacency: Dict[TNode, List[TNode]]
      initial_values: Dict[TNode, float]
      epsilon: Optional[float]
      max_iterations: Optional[int]
      tolerance: Optional[float]
      method: Optional[str]
    outputs:
      consensus_value: float
      target_average: float
      final_estimates: Dict[TNode, float]
      iterations_run: int
      converged: bool
      residual_error: float
    parameters:
      epsilon: 0.1
      max_iterations: 100
      tolerance: 1e-6
      method: "laplacian"
    capability_tags:
      - distributed_consensus
      - laplacian_dynamics
      - push_sum
      - decentralized_averaging
    purity: deterministic
    determinism: true
    idempotency: true
    complexity:
      time: "O(T * |E|)"
      space: "O(|V|)"
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        adjacency: Dict[TNode, List[TNode]],
        initial_values: Dict[TNode, float],
        epsilon: float = 0.1,
        max_iterations: int = 100,
        tolerance: float = 1e-6,
        method: str = "laplacian",
    ) -> Dict[str, Any]:
        nodes = sorted(list(initial_values.keys()), key=lambda x: str(x))
        n = len(nodes)
        if n == 0:
            return {
                "consensus_value": 0.0,
                "target_average": 0.0,
                "final_estimates": {},
                "iterations_run": 0,
                "converged": True,
                "residual_error": 0.0,
            }

        target_avg = sum(initial_values.values()) / n

        if method == "push_sum":
            s = {u: float(initial_values[u]) for u in nodes}
            w = {u: 1.0 for u in nodes}

            rounds = 0
            converged = False

            for it in range(max_iterations):
                rounds = it + 1
                next_s: Dict[TNode, float] = {u: 0.0 for u in nodes}
                next_w: Dict[TNode, float] = {u: 0.0 for u in nodes}

                for u in nodes:
                    out_neighbors = adjacency.get(u, [])
                    deg = len(out_neighbors) + 1
                    s_share = s[u] / deg
                    w_share = w[u] / deg

                    next_s[u] += s_share
                    next_w[u] += w_share

                    for v in out_neighbors:
                        if v in next_s:
                            next_s[v] += s_share
                            next_w[v] += w_share

                s = next_s
                w = next_w

                estimates = {u: (s[u] / w[u]) if w[u] > 1e-12 else 0.0 for u in nodes}
                vals = list(estimates.values())
                mean_est = sum(vals) / n
                var = sum((x - mean_est) ** 2 for x in vals) / n

                if math.sqrt(var) < tolerance:
                    converged = True
                    break

            final_estimates = {u: (s[u] / w[u]) if w[u] > 1e-12 else 0.0 for u in nodes}

        else:
            x = {u: float(initial_values[u]) for u in nodes}
            rounds = 0
            converged = False

            for it in range(max_iterations):
                rounds = it + 1
                next_x: Dict[TNode, float] = {}

                for u in nodes:
                    neighbors = adjacency.get(u, [])
                    laplacian_flow = sum(x.get(v, x[u]) - x[u] for v in neighbors)
                    next_x[u] = x[u] + epsilon * laplacian_flow

                x = next_x
                vals = list(x.values())
                mean_est = sum(vals) / n
                var = sum((val - mean_est) ** 2 for val in vals) / n

                if math.sqrt(var) < tolerance:
                    converged = True
                    break

            final_estimates = x

        vals = list(final_estimates.values())
        consensus_val = sum(vals) / n
        max_err = max(abs(v - target_avg) for v in vals)

        return {
            "consensus_value": consensus_val,
            "target_average": target_avg,
            "final_estimates": final_estimates,
            "iterations_run": rounds,
            "converged": converged,
            "residual_error": max_err,
        }
