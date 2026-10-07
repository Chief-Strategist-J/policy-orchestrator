"""ALGORITHM & ARCHITECTURE BLUEPRINT: HARMONIC LABEL PROPAGATION (ZHU-GHAHRAMANI) (ALGO-GRAPH-RANK-286)

1. OVERVIEW & OBJECTIVE
Semi-supervised graph classification via Harmonic Energy Minimization (Zhu, Ghahramani, Lafferty).
Fixes labeled node probabilities (Dirichlet boundary conditions) and computes harmonic functions on
unlabeled nodes such that each unlabeled node's distribution is the weighted average of its neighbors' distributions:
Delta f(u) = 0 for all u in U, minimizing graph Dirichlet energy E(f) = (1/2) * sum_{ij} W_{ij} (f(i) - f(j))^2.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V| * |K| + |E|) where K is class label count.
- Time Complexity: O(T_iter * |E| * |K|) iterative Jacobi/Gauss-Seidel relaxation.
- Invariants:
  - Labeled nodes strictly retain their clamp values: f_L(u) = y_u at every iteration.
  - Predicted label distributions are harmonic on unlabeled nodes and sum to 1.0.

3. INPUT PARAMETERS:
- weighted_adjacency: Mapping[TNode, Mapping[TNode, float]] weighted graph edges W_{ij} >= 0.
- labeled_nodes: Mapping[TNode, int] observed discrete class assignments for subset L subset of V.
- num_classes: int number of discrete classification categories.
- max_iterations: int relaxation iteration cutoff.
- tolerance: float convergence threshold max_u ||f^{(t)}(u) - f^{(t-1)}(u)||_1.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'predictions': Dict[TNode, int] predicted argmax class label for all nodes.
  - 'probabilities': Dict[TNode, List[float]] class posterior distribution per node.
  - 'converged': bool convergence indicator.
  - 'iterations': int completed relaxation iterations.

5. AGENT CONTRACT:
- Zero inline comments.
- Generic node typing `TNode`.
"""

from __future__ import annotations

from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoHarmonicLabelPropagation(Generic[TNode]):
    """Harmonic function semi-supervised label propagation with Dirichlet boundary clamping.

    ```yaml
    contract:
      id: ALGO-GRAPH-RANK-286
      name: GraphAlgoHarmonicLabelPropagation
      inputs:
        - name: weighted_adjacency
          type: Mapping[TNode, Mapping[TNode, float]]
          description: Weighted graph affinity dictionary.
        - name: labeled_nodes
          type: Mapping[TNode, int]
          description: Known class labels for seed vertices.
        - name: num_classes
          type: int
          description: Total number of classification labels.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Predicted discrete classes, posterior vectors, and convergence metrics.
      parameters:
        max_iterations: int (default 200)
        tolerance: float (default 1e-5)
      capability_tags:
        - SEMI_SUPERVISED
        - LABEL_PROPAGATION
        - HARMONIC_FUNCTION
        - DIRICHLET_ENERGY
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(T * |E| * K)
        space: O(|V| * K + |E|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        weighted_adjacency: Mapping[TNode, Mapping[TNode, float]],
        labeled_nodes: Mapping[TNode, int],
        num_classes: int,
        max_iterations: int = 200,
        tolerance: float = 1e-5,
    ) -> Dict[str, Any]:
        """Solves harmonic label distribution on unlabeled vertices."""
        all_nodes: Set[TNode] = set(weighted_adjacency.keys())
        for nbrs in weighted_adjacency.values():
            all_nodes.update(nbrs.keys())
        all_nodes.update(labeled_nodes.keys())

        node_list = list(all_nodes)
        if not node_list or num_classes <= 0:
            return {
                "predictions": {},
                "probabilities": {},
                "converged": True,
                "iterations": 0,
            }

        probs: Dict[TNode, List[float]] = {}
        for u in node_list:
            if u in labeled_nodes:
                lbl = labeled_nodes[u]
                v = [0.0] * num_classes
                if 0 <= lbl < num_classes:
                    v[lbl] = 1.0
                probs[u] = v
            else:
                probs[u] = [1.0 / float(num_classes)] * num_classes

        degrees: Dict[TNode, float] = {}
        for u in node_list:
            deg = sum(weighted_adjacency.get(u, {}).values())
            degrees[u] = max(1e-12, deg)

        unlabeled = [u for u in node_list if u not in labeled_nodes]
        converged = False
        iteration = 0

        for it in range(max_iterations):
            iteration = it + 1
            max_delta = 0.0
            new_probs: Dict[TNode, List[float]] = {}

            for u in node_list:
                if u in labeled_nodes:
                    new_probs[u] = list(probs[u])
                    continue

                accum = [0.0] * num_classes
                deg_u = degrees[u]

                for v, w in weighted_adjacency.get(u, {}).items():
                    p_v = probs.get(v, [1.0 / float(num_classes)] * num_classes)
                    for k in range(num_classes):
                        accum[k] += (w / deg_u) * p_v[k]

                s = sum(accum)
                if s > 0.0:
                    normalized = [val / s for val in accum]
                else:
                    normalized = [1.0 / float(num_classes)] * num_classes

                delta = sum(abs(normalized[k] - probs[u][k]) for k in range(num_classes))
                if delta > max_delta:
                    max_delta = delta

                new_probs[u] = normalized

            probs = new_probs
            if max_delta < tolerance:
                converged = True
                break

        predictions: Dict[TNode, int] = {}
        for u in node_list:
            p_vec = probs[u]
            best_cls = max(range(num_classes), key=lambda k: p_vec[k])
            predictions[u] = best_cls

        return {
            "predictions": predictions,
            "probabilities": probs,
            "converged": converged,
            "iterations": iteration,
        }
