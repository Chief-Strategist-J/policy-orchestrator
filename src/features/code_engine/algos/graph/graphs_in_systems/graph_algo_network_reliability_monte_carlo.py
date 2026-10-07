"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Network Reliability Monte Carlo (ALGO-GRAPH-SYS-311)

1. OVERVIEW & OBJECTIVE:
Estimates the operational reliability of communication networks subject to independent
component failures. Implements Monte Carlo sampling and union-find connectivity testing
for two-terminal reliability (s-t connectivity) and all-terminal reliability (spanning connectivity),
computing empirical success rates, standard errors, and confidence intervals.

2. COMPLEXITY & INVARIANTS:
- Time Complexity: O(num_samples * (|E| * alpha(|V|))) for disjoint-set connectivity evaluation.
- Space Complexity: O(|V| + |E|) for union-find state representation.
- Invariants: Reliability estimate lies in [0, 1]; confidence intervals narrow with sqrt(N).

3. INPUT PARAMETERS:
- `edges`: List[Tuple[TNode, TNode, float]] list of edges `(u, v, failure_probability)`.
- `nodes`: List[TNode] or Set[TNode] of all vertices in the network.
- `source`: Optional[TNode] source node for two-terminal reliability.
- `target`: Optional[TNode] target node for two-terminal reliability.
- `num_samples`: int number of Monte Carlo realization trials (default 1000).
- `confidence_level`: float Z-score parameter (e.g. 0.95 for 95% CI).

4. OUTPUT PARAMETERS:
- `two_terminal_reliability`: Optional[float] estimated probability that source and target stay connected.
- `all_terminal_reliability`: float estimated probability that all nodes remain in a single connected component.
- `confidence_interval_95`: Tuple[float, float] lower and upper bounds of 95% confidence interval.
- `standard_error`: float empirical standard error of the Monte Carlo estimator.
- `sample_trials`: int total evaluated sample iterations.

5. AGENT CONTRACT:
- Role: Network Analyst and Risk Evaluator.
- Rules: Edge failure probabilities must lie strictly in [0.0, 1.0].
- Guardrails: Document independent failure assumptions; flag critical single points of failure.
"""

from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
import math
import random

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoNetworkReliabilityMonteCarlo(Generic[TNode]):
    """
    inputs:
      edges: List[Tuple[TNode, TNode, float]]
      nodes: List[TNode]
      source: Optional[TNode]
      target: Optional[TNode]
      num_samples: Optional[int]
      confidence_level: Optional[float]
    outputs:
      two_terminal_reliability: Optional[float]
      all_terminal_reliability: float
      confidence_interval_95: Tuple[float, float]
      standard_error: float
      sample_trials: int
    parameters:
      num_samples: 1000
      confidence_level: 0.95
    capability_tags:
      - network_reliability
      - monte_carlo
      - terminal_reliability
      - union_find
    purity: deterministic
    determinism: true
    idempotency: true
    complexity:
      time: "O(samples * |E| * alpha(|V|))"
      space: "O(|V| + |E|)"
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        edges: List[Tuple[TNode, TNode, float]],
        nodes: List[TNode],
        source: Optional[TNode] = None,
        target: Optional[TNode] = None,
        num_samples: int = 1000,
        confidence_level: float = 0.95,
    ) -> Dict[str, Any]:
        node_list = sorted(list(set(nodes)), key=lambda x: str(x))
        n = len(node_list)

        if n <= 1:
            return {
                "two_terminal_reliability": 1.0 if source and target else None,
                "all_terminal_reliability": 1.0,
                "confidence_interval_95": (1.0, 1.0),
                "standard_error": 0.0,
                "sample_trials": num_samples,
            }

        rng = random.Random(42)

        all_term_success = 0
        two_term_success = 0

        for _ in range(num_samples):
            parent: Dict[TNode, TNode] = {u: u for u in node_list}

            def find(u: TNode) -> TNode:
                root = u
                while parent[root] != root:
                    root = parent[root]
                curr = u
                while curr != root:
                    nxt = parent[curr]
                    parent[curr] = root
                    curr = nxt
                return root

            def union(u: TNode, v: TNode) -> None:
                ru, rv = find(u), find(v)
                if ru != rv:
                    parent[ru] = rv

            for u, v, q_fail in edges:
                if rng.random() >= q_fail:
                    if u in parent and v in parent:
                        union(u, v)

            distinct_roots = {find(u) for u in node_list}
            if len(distinct_roots) == 1:
                all_term_success += 1

            if source is not None and target is not None:
                if source in parent and target in parent:
                    if find(source) == find(target):
                        two_term_success += 1

        all_rel = all_term_success / num_samples
        two_rel = (two_term_success / num_samples) if (source and target) else None

        primary_metric = two_rel if two_rel is not None else all_rel
        variance = (primary_metric * (1.0 - primary_metric)) / num_samples
        std_err = math.sqrt(variance)

        z_val = 1.96 if confidence_level >= 0.95 else 1.645
        ci_lower = max(0.0, primary_metric - z_val * std_err)
        ci_upper = min(1.0, primary_metric + z_val * std_err)

        return {
            "two_terminal_reliability": two_rel,
            "all_terminal_reliability": all_rel,
            "confidence_interval_95": (round(ci_lower, 5), round(ci_upper, 5)),
            "standard_error": round(std_err, 6),
            "sample_trials": num_samples,
        }
