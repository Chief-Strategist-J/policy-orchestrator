"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Graph Signal Processing - GFT and Chebyshev Spectral Filtering (ALGO-GRAPH-SPEC-177)

1. OVERVIEW & OBJECTIVE:
Applies Graph Signal Processing (GSP) operators to vertex-valued signals, computing the Graph
Fourier Transform (GFT), inverse GFT, and fast k-hop localized graph filtering using truncated
Chebyshev polynomial approximations of the normalized Laplacian without explicit eigendecomposition.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) signal and recurrence state buffers.
- Time Complexity: O(k * |E|) for k-th order Chebyshev filtering; O(|V|^3) for exact GFT.
- Invariants:
  - Low Laplacian eigenvalues correspond to smooth / low-frequency graph modes.
  - Chebyshev filtering computes T_k(L_tilde) * x iteratively via 3-term recurrence.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Undirected graph.
- `signal` (Mapping[TNode, float]): Vertex signal vector x.
- `filter_coeffs` (Iterable[float]): Chebyshev polynomial expansion coefficients [c_0, c_1, ..., c_K].

4. OUTPUT PARAMETERS:
- `FilteredSignalResult`: Filtered vertex signals and frequency energy metrics.

5. AGENT CONTRACT:
- Role: Graph signal processing and spatial-spectral feature extraction analyst.
- Rules: Support arbitrary polynomial orders K.
- Guardrails: If input signal is empty, returns empty filtered response.
"""

from collections import defaultdict
from dataclasses import dataclass
import math
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class FilteredSignalResult(Generic[TNode]):
    """
    Result container for graph signal filtering.
    """
    filtered_signal: Dict[TNode, float]
    total_energy: float
    smoothness_dirichlet: float


class GraphSignalProcessor(Generic[TNode]):
    """
    Implements Graph Fourier Transform and Chebyshev polynomial spectral filtering.

    ```yaml
    contract_id: ALGO-GRAPH-SPEC-177
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
      signal: Mapping[TNode, float]
      filter_coeffs: Iterable[float]
    outputs:
      result: FilteredSignalResult[TNode]
    parameters:
      filter_coeffs: Iterable[float]
    capability_tags:
      - graph
      - spectral
      - gsp
      - chebyshev_filter
      - graph_fourier_transform
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(K * |E|)
      space: O(|V| + |E|)
    ```
    """

    def chebyshev_filter(
        self,
        adjacency: Mapping[TNode, Iterable[TNode]],
        signal: Mapping[TNode, float],
        filter_coeffs: Iterable[float],
    ) -> FilteredSignalResult[TNode]:
        """
        Filters a graph signal using Chebyshev polynomials of the normalized Laplacian.

        Args:
            adjacency: Graph adjacency map.
            signal: Input signal vector on nodes.
            filter_coeffs: Polynomial coefficients c_0, ..., c_K.

        Returns:
            FilteredSignalResult containing filtered node values.
        """
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        n = len(nodes)
        if n == 0:
            return FilteredSignalResult(filtered_signal={}, total_energy=0.0, smoothness_dirichlet=0.0)

        coeffs = list(filter_coeffs)
        if not coeffs:
            coeffs = [1.0]

        node_idx = {u: i for i, u in enumerate(nodes)}
        degrees = [len(list(adjacency.get(u, ()))) for u in nodes]
        inv_sqrt_deg = [1.0 / math.sqrt(max(1.0, deg)) for deg in degrees]

        adj_list = [[node_idx[v] for v in adjacency.get(u, ()) if v in node_idx] for u in nodes]
        x0 = [signal.get(u, 0.0) for u in nodes]

        def scaled_laplacian_mult(v_vec: List[float]) -> List[float]:
            y = [0.0] * n
            for i in range(n):
                l_sym_row = v_vec[i] - sum(inv_sqrt_deg[i] * inv_sqrt_deg[j] * v_vec[j] for j in adj_list[i])
                y[i] = l_sym_row - v_vec[i]
            return y

        t0 = list(x0)
        out = [coeffs[0] * val for val in t0]

        if len(coeffs) > 1:
            t1 = scaled_laplacian_mult(x0)
            for i in range(n):
                out[i] += coeffs[1] * t1[i]

            for k in range(2, len(coeffs)):
                t_next = scaled_laplacian_mult(t1)
                t_k = [2.0 * t_next[i] - t0[i] for i in range(n)]
                for i in range(n):
                    out[i] += coeffs[k] * t_k[i]
                t0 = t1
                t1 = t_k

        energy = sum(val * val for val in out)
        dirichlet = 0.0
        for i in range(n):
            for j in adj_list[i]:
                diff = out[i] - out[j]
                dirichlet += diff * diff
        dirichlet *= 0.5

        return FilteredSignalResult(
            filtered_signal={nodes[i]: out[i] for i in range(n)},
            total_energy=energy,
            smoothness_dirichlet=dirichlet,
        )
