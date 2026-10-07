"""ALGORITHM & ARCHITECTURE BLUEPRINT: LOOPY BELIEF PROPAGATION (LBP WITH DAMPING) (ALGO-GRAPH-PGM-270)

1. OVERVIEW & OBJECTIVE
Approximate marginal inference on general cyclic/loopy undirected graphical models and factor graphs via
iterative message passing with momentum damping. Messages are updated synchronously or asynchronously
until convergence or maximum iteration limits, providing variational approximations (Bethe free energy stationary points).

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|E| * |K| + |V| * |K|) storing messages and local beliefs.
- Time Complexity: O(T_iter * |E| * |K|^2) where K is the maximum cardinality of variable domains.
- Invariants:
  - Damping parameter alpha in [0.0, 1.0) guarantees stabilized message updates: m_new = (1-a)*m_calc + a*m_old.
  - Belief vectors are normalized probability distributions summing to 1.0.

3. INPUT PARAMETERS:
- adjacency: Mapping[TNode, Collection[TNode]] cyclic or general graph topology.
- node_potentials: Mapping[TNode, Sequence[float]] unary node evidence/potentials.
- edge_potentials: Mapping[tuple[TNode, TNode], Sequence[Sequence[float]]] pairwise compatibility tables.
- max_iterations: int maximum iteration cutoff.
- damping: float momentum damping coefficient in [0.0, 1.0).
- tolerance: float message delta convergence threshold.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'marginals': Dict[TNode, List[float]] estimated posterior marginal probabilities.
  - 'converged': bool indicating whether message deltas fell below tolerance.
  - 'iterations': int count of executed message passing steps.
  - 'messages': Dict[tuple[TNode, TNode], List[float]] final converged messages.

5. AGENT CONTRACT:
- Adherence to zero-inline-comment rule.
- Full generic compatibility over `TNode`.
"""

from __future__ import annotations

import math
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Sequence, Set, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoLoopyBeliefPropagation(Generic[TNode]):
    """Iterative Loopy Belief Propagation (LBP) with damping for cyclic graphs.

    ```yaml
    contract:
      id: ALGO-GRAPH-PGM-270
      name: GraphAlgoLoopyBeliefPropagation
      inputs:
        - name: adjacency
          type: Mapping[TNode, Collection[TNode]]
          description: General graph adjacency map.
        - name: node_potentials
          type: Mapping[TNode, Sequence[float]]
          description: Local node potential vectors.
        - name: edge_potentials
          type: Mapping[tuple[TNode, TNode], Sequence[Sequence[float]]]
          description: Symmetric or directed pairwise potential matrices.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Approximate marginals, convergence status, and message tables.
      parameters:
        max_iterations: int (default 100)
        damping: float (default 0.2)
        tolerance: float (default 1e-6)
      capability_tags:
        - PGM
        - LOOPY_BP
        - APPROXIMATE_INFERENCE
        - BETHE_APPROXIMATION
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(T_iter * |E| * |K|^2)
        space: O(|E| * |K| + |V| * |K|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        adjacency: Mapping[TNode, Collection[TNode]],
        node_potentials: Mapping[TNode, Sequence[float]],
        edge_potentials: Mapping[tuple[TNode, TNode], Sequence[Sequence[float]]],
        max_iterations: int = 100,
        damping: float = 0.2,
        tolerance: float = 1e-6,
    ) -> Dict[str, Any]:
        """Runs damped synchronous Loopy Belief Propagation until convergence."""
        nodes: List[TNode] = list(node_potentials.keys())
        if not nodes:
            return {"marginals": {}, "converged": True, "iterations": 0, "messages": {}}

        directed_edges: Set[tuple[TNode, TNode]] = set()
        for u in nodes:
            for v in adjacency.get(u, []):
                if v in node_potentials:
                    directed_edges.add((u, v))
                    directed_edges.add((v, u))

        messages: Dict[tuple[TNode, TNode], List[float]] = {}
        for u, v in directed_edges:
            v_dim = len(node_potentials[v])
            messages[(u, v)] = [1.0 / float(v_dim)] * v_dim

        converged = False
        iteration = 0

        for it in range(max_iterations):
            iteration = it + 1
            max_delta = 0.0
            new_messages: Dict[tuple[TNode, TNode], List[float]] = {}

            for u, v in directed_edges:
                psi_u = list(node_potentials[u])
                u_dim = len(psi_u)
                prod_incoming = list(psi_u)

                for w in adjacency.get(u, []):
                    if w != v and (w, u) in messages:
                        inc = messages[(w, u)]
                        for s in range(u_dim):
                            prod_incoming[s] *= inc[s]

                factor = edge_potentials.get((u, v))
                is_trans = False
                if factor is None:
                    factor = edge_potentials.get((v, u))
                    is_trans = True

                v_dim = len(node_potentials[v])
                raw_msg = [0.0] * v_dim

                if factor is not None:
                    for j in range(v_dim):
                        s = 0.0
                        for i in range(u_dim):
                            val = factor[j][i] if is_trans else factor[i][j]
                            s += prod_incoming[i] * val
                        raw_msg[j] = s
                else:
                    tot = sum(prod_incoming)
                    raw_msg = [tot] * v_dim

                sum_m = sum(raw_msg)
                norm_msg = [val / sum_m if sum_m > 0.0 else 1.0 / v_dim for val in raw_msg]

                old_msg = messages[(u, v)]
                damped_msg = [
                    (1.0 - damping) * norm_msg[j] + damping * old_msg[j]
                    for j in range(v_dim)
                ]
                damped_sum = sum(damped_msg)
                final_msg = [val / damped_sum if damped_sum > 0.0 else 1.0 / v_dim for val in damped_msg]

                delta = sum(abs(final_msg[j] - old_msg[j]) for j in range(v_dim))
                if delta > max_delta:
                    max_delta = delta

                new_messages[(u, v)] = final_msg

            messages = new_messages
            if max_delta < tolerance:
                converged = True
                break

        marginals: Dict[TNode, List[float]] = {}
        for u in nodes:
            psi_u = list(node_potentials[u])
            u_dim = len(psi_u)
            prod = list(psi_u)
            for w in adjacency.get(u, []):
                if (w, u) in messages:
                    inc = messages[(w, u)]
                    for s in range(u_dim):
                        prod[s] *= inc[s]
            total = sum(prod)
            if total > 0.0:
                marginals[u] = [val / total for val in prod]
            else:
                marginals[u] = [1.0 / u_dim] * u_dim

        return {
            "marginals": marginals,
            "converged": converged,
            "iterations": iteration,
            "messages": messages,
        }
