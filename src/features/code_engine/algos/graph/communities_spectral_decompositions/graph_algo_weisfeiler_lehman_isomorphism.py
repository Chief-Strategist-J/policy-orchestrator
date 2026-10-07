"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Weisfeiler-Lehman Isomorphism and Color Refinement (ALGO-GRAPH-ISO-181)

1. OVERVIEW & OBJECTIVE:
Executes the Weisfeiler-Lehman (1-WL / k-WL) color refinement iterative partition algorithm
to produce canonical graph certificates, hash signatures, and decide graph isomorphism for
planar graphs, trees, and almost all random graphs.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) hash mapping and multiset buffers.
- Time Complexity: O(iterations * (|V| + |E|)).
- Invariants:
  - Isomorphic graphs always produce identical color refinement histograms and hashes.
  - Generates deterministic hash representations invariant to vertex ordering.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Graph to hash or test.
- `initial_labels` (Optional[Mapping[TNode, str]]): Optional initial vertex features/labels.
- `iterations` (int): Number of color refinement iterations (default: 3).

4. OUTPUT PARAMETERS:
- `WLHashResult`: Canonical SHA256/hex fingerprint, stable color histogram, and iteration count.

5. AGENT CONTRACT:
- Role: Graph isomorphism tester, structural deduplicator, and graph hashing engine.
- Rules: Enforce deterministic sorting of neighbor multiset color signatures.
- Guardrails: Two non-isomorphic graphs with equal 1-WL hashes (e.g., Decahedron vs 2-pentagons) are acknowledged as indistinguishable by 1-WL.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class WLHashResult:
    """
    Result container for Weisfeiler-Lehman graph hashing.
    """
    canonical_hash: str
    color_histogram: Dict[str, int]
    iterations_run: int


class WeisfeilerLehmanIsomorphism(Generic[TNode]):
    """
    Computes 1-WL color refinement canonical hashes and isomorphism tests.

    ```yaml
    contract_id: ALGO-GRAPH-ISO-181
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
      initial_labels: Optional[Mapping[TNode, str]]
      iterations: int
    outputs:
      result: WLHashResult
    parameters:
      iterations: int
    capability_tags:
      - graph
      - isomorphism
      - weisfeiler_lehman
      - color_refinement
      - canonical_hash
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(iterations * (|V| + |E|))
      space: O(|V| + |E|)
    ```
    """

    def __init__(self, iterations: int = 3) -> None:
        """
        Args:
            iterations: Number of color refinement rounds.
        """
        self._iterations = max(1, iterations)

    def hash_graph(
        self,
        adjacency: Mapping[TNode, Iterable[TNode]],
        initial_labels: Optional[Mapping[TNode, str]] = None,
    ) -> WLHashResult:
        """
        Computes the canonical WL hash fingerprint of a graph.

        Args:
            adjacency: Graph adjacency map.
            initial_labels: Optional initial vertex label mapping.

        Returns:
            WLHashResult containing SHA256 hex digest and color histogram.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        if not nodes:
            return WLHashResult(
                canonical_hash=hashlib.sha256(b"EMPTY_GRAPH").hexdigest(),
                color_histogram={},
                iterations_run=0,
            )

        adj: Dict[TNode, List[TNode]] = {u: sorted(list(adjacency.get(u, ())), key=lambda x: str(x)) for u in nodes}

        if initial_labels is not None:
            colors = {u: str(initial_labels.get(u, "0")) for u in nodes}
        else:
            colors = {u: str(len(adj[u])) for u in nodes}

        all_histograms: Counter = Counter(colors.values())

        for _ in range(self._iterations):
            new_colors: Dict[TNode, str] = {}
            for u in nodes:
                neighbor_colors = sorted(colors[v] for v in adj[u] if v in colors)
                signature = f"{colors[u]}-" + ",".join(neighbor_colors)
                new_color = hashlib.sha256(signature.encode("utf-8")).hexdigest()[:16]
                new_colors[u] = new_color

            colors = new_colors
            all_histograms.update(colors.values())

        sorted_hist_items = sorted(all_histograms.items())
        hist_str = ";".join(f"{col}:{cnt}" for col, cnt in sorted_hist_items)
        canonical_digest = hashlib.sha256(hist_str.encode("utf-8")).hexdigest()

        return WLHashResult(
            canonical_hash=canonical_digest,
            color_histogram=dict(all_histograms),
            iterations_run=self._iterations,
        )

    def are_isomorphic(
        self,
        adj_1: Mapping[TNode, Iterable[TNode]],
        adj_2: Mapping[TNode, Iterable[TNode]],
    ) -> bool:
        """
        Tests if two graphs are isomorphic according to the WL-1 test.

        Args:
            adj_1: First graph.
            adj_2: Second graph.

        Returns:
            True if WL signatures match, False otherwise.
        """
        h1 = self.hash_graph(adj_1)
        h2 = self.hash_graph(adj_2)
        return h1.canonical_hash == h2.canonical_hash
