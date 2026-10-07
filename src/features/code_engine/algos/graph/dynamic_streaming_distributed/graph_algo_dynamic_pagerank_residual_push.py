"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Dynamic PageRank with Residual Push (ALGO-GRAPH-DYN-204)

1. OVERVIEW & OBJECTIVE:
Maintains PageRank scores dynamically on evolving graphs using forward residual error pushes,
adjusting node scores and propagating residual discrepancies locally when edges are added or
removed without requiring expensive full-graph power iterations.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) storage for PageRank estimates and residual vectors.
- Time Complexity: O(|delta_E| / epsilon) proportional to push volume.
- Invariants:
  - Conserved invariant: p(u) + sum_{v in V} r(v) * PPR(v, u) == PageRank(u).
  - Pushes terminate when all residuals r(u) <= epsilon * deg(u).

3. INPUT PARAMETERS:
- `alpha` (float): Teleportation damping factor (default: 0.85).
- `epsilon` (float): Residual push threshold (default: 1e-4).

4. OUTPUT PARAMETERS:
- `DynamicPageRankResult`: PageRank score dictionary, current residuals, and push count.

5. AGENT CONTRACT:
- Role: Real-time web ranking and dynamic importance analyst.
- Rules: Zero inline comments in method bodies.
- Guardrails: Non-positive epsilon raises ValueError.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class DynamicPageRankResult(Generic[TNode]):
    """
    Result container for dynamic PageRank updates.
    """
    scores: Dict[TNode, float]
    residuals: Dict[TNode, float]
    total_pushes: int


class GraphAlgoDynamicPagerankResidualPush(Generic[TNode]):
    """
    Maintains online PageRank estimates via local residual push operations.

    ```yaml
    contract_id: ALGO-GRAPH-DYN-204
    inputs:
      alpha: float
      epsilon: float
    outputs:
      result: DynamicPageRankResult[TNode]
    parameters:
      alpha: float
      epsilon: float
    capability_tags:
      - graph
      - dynamic
      - pagerank
      - residual_push
      - ranking
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|delta_E| / epsilon)
      space: O(|V| + |E|)
    ```
    """

    def __init__(self, alpha: float = 0.85, epsilon: float = 1e-4) -> None:
        """
        Args:
            alpha: Damping parameter in (0, 1).
            epsilon: Convergence residual threshold.
        """
        if not (0.0 < alpha < 1.0):
            raise ValueError("alpha must be in (0, 1).")
        if epsilon <= 0.0:
            raise ValueError("epsilon must be positive.")

        self._alpha = alpha
        self._eps = epsilon
        self._adj: Dict[TNode, Set[TNode]] = defaultdict(set)
        self._scores: Dict[TNode, float] = defaultdict(float)
        self._residuals: Dict[TNode, float] = defaultdict(float)
        self._nodes: Set[TNode] = set()
        self._pushes = 0

    def add_node(self, u: TNode) -> None:
        """
        Registers a new node and initializes its residual.

        Args:
            u: Node identifier.
        """
        if u not in self._nodes:
            self._nodes.add(u)
            self._residuals[u] = 1.0

    def add_edge(self, u: TNode, v: TNode) -> DynamicPageRankResult[TNode]:
        """
        Adds directed edge u -> v and triggers localized residual push.

        Args:
            u: Source node.
            v: Target node.

        Returns:
            DynamicPageRankResult containing updated PageRank scores.
        """
        self.add_node(u)
        self.add_node(v)

        if v not in self._adj[u]:
            self._adj[u].add(v)
            self._residuals[u] += self._scores[u]
            self._push_all()

        return self.get_scores()

    def remove_edge(self, u: TNode, v: TNode) -> DynamicPageRankResult[TNode]:
        """
        Removes directed edge u -> v and updates residuals.

        Args:
            u: Source node.
            v: Target node.

        Returns:
            DynamicPageRankResult containing updated PageRank scores.
        """
        if u in self._adj and v in self._adj[u]:
            self._adj[u].remove(v)
            self._residuals[u] += self._scores[u]
            self._push_all()

        return self.get_scores()

    def _push_all(self) -> None:
        queue: List[TNode] = [u for u in self._nodes if self._residuals[u] > self._eps]

        while queue:
            u = queue.pop(0)
            res = self._residuals[u]
            if res <= self._eps:
                continue

            self._pushes += 1
            self._scores[u] += (1.0 - self._alpha) * res
            self._residuals[u] = 0.0

            out_deg = len(self._adj[u])
            if out_deg > 0:
                push_amount = (self._alpha * res) / out_deg
                for v in self._adj[u]:
                    self._residuals[v] += push_amount
                    if self._residuals[v] > self._eps and v not in queue:
                        queue.append(v)
            else:
                self._residuals[u] += self._alpha * res

    def get_scores(self) -> DynamicPageRankResult[TNode]:
        """
        Returns normalized PageRank scores.

        Returns:
            DynamicPageRankResult with current scores.
        """
        tot = sum(self._scores.values())
        norm_scores = {u: (self._scores[u] / tot) if tot > 0 else (1.0 / len(self._nodes)) for u in self._nodes}

        return DynamicPageRankResult(
            scores=norm_scores,
            residuals=dict(self._residuals),
            total_pushes=self._pushes,
        )
