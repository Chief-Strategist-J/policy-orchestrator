"""ALGORITHM & ARCHITECTURE BLUEPRINT: BELIEF PROPAGATION ON TREES (SUM-PRODUCT) (ALGO-GRAPH-PGM-269)

1. OVERVIEW & OBJECTIVE
Exact marginal inference in tree-structured probabilistic graphical models via two-pass message passing
(leaves-to-root and root-to-leaves) under the Sum-Product semiring, computing exact marginal distributions
for all discrete random variables in O(|V| * |K|^2) time without approximation or cyclic feedback loops.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V| * |K|^2 + |E| * |K|) storing factor tables and directional messages.
- Time Complexity: O(|E| * |K|^2) where K is the discrete state domain size.
- Invariants:
  - Directed acyclic or undirected tree structure contains zero cycles.
  - Marginal distributions at every variable node sum exactly to 1.0 (normalized).

3. INPUT PARAMETERS:
- tree_adjacency: Mapping[TNode, Collection[TNode]] acyclic undirected tree topology.
- node_potentials: Mapping[TNode, Sequence[float]] local variable evidence/priors psi_i(x_i).
- edge_potentials: Mapping[tuple[TNode, TNode], Sequence[Sequence[float]]] pairwise factor matrices psi_ij(x_i, x_j).
- root_node: Optional[TNode] arbitrary root for orienting the two-pass schedule.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'marginals': Dict[TNode, List[float]] exact posterior distributions P(X_i).
  - 'messages': Dict[tuple[TNode, TNode], List[float]] directional messages m_{i -> j}.
  - 'partition_function': float global normalizer Z.

5. AGENT CONTRACT:
- Strict zero-inline-comment policy.
- Numerical stabilization via L1 normalization of directional messages.
"""

from __future__ import annotations

from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoBeliefPropagationTree(Generic[TNode]):
    """Exact Sum-Product Belief Propagation for tree-structured graphical models.

    ```yaml
    contract:
      id: ALGO-GRAPH-PGM-269
      name: GraphAlgoBeliefPropagationTree
      inputs:
        - name: tree_adjacency
          type: Mapping[TNode, Collection[TNode]]
          description: Acyclic undirected tree structure.
        - name: node_potentials
          type: Mapping[TNode, Sequence[float]]
          description: Local prior/evidence vectors psi_i(x_i).
        - name: edge_potentials
          type: Mapping[tuple[TNode, TNode], Sequence[Sequence[float]]]
          description: Pairwise compatibility matrices psi_ij(x_i, x_j).
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Normalized marginals, edge messages, and partition constant Z.
      parameters:
        root_node: Optional[TNode] (default None)
      capability_tags:
        - PGM
        - EXACT_INFERENCE
        - SUM_PRODUCT
        - TREE_BP
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(|E| * |K|^2)
        space: O(|V| * |K| + |E| * |K|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        tree_adjacency: Mapping[TNode, Collection[TNode]],
        node_potentials: Mapping[TNode, Sequence[float]],
        edge_potentials: Mapping[tuple[TNode, TNode], Sequence[Sequence[float]]],
        root_node: Optional[TNode] = None,
    ) -> Dict[str, Any]:
        """Calculates exact marginals across all nodes using the Sum-Product algorithm."""
        nodes: List[TNode] = list(node_potentials.keys())
        if not nodes:
            return {"marginals": {}, "messages": {}, "partition_function": 1.0}

        root: TNode = root_node if root_node is not None and root_node in node_potentials else nodes[0]

        parents: Dict[TNode, Optional[TNode]] = {root: None}
        children: Dict[TNode, List[TNode]] = {u: [] for u in nodes}
        bfs_order: List[TNode] = [root]
        queue: List[TNode] = [root]
        visited: Set[TNode] = {root}

        head = 0
        while head < len(queue):
            curr = queue[head]
            head += 1
            for nbr in tree_adjacency.get(curr, []):
                if nbr in node_potentials and nbr not in visited:
                    visited.add(nbr)
                    parents[nbr] = curr
                    children[curr].append(nbr)
                    queue.append(nbr)
                    bfs_order.append(nbr)

        post_order: List[TNode] = list(reversed(bfs_order))

        messages: Dict[tuple[TNode, TNode], List[float]] = {}

        for u in post_order:
            p = parents[u]
            if p is not None:
                messages[(u, p)] = self._compute_message(
                    u, p, tree_adjacency, node_potentials, edge_potentials, messages, exclude=p
                )

        for u in bfs_order:
            for c in children[u]:
                messages[(u, c)] = self._compute_message(
                    u, c, tree_adjacency, node_potentials, edge_potentials, messages, exclude=c
                )

        marginals: Dict[TNode, List[float]] = {}
        for u in nodes:
            psi_u = list(node_potentials[u])
            k_states = len(psi_u)
            prod = list(psi_u)
            for nbr in tree_adjacency.get(u, []):
                if (nbr, u) in messages:
                    msg = messages[(nbr, u)]
                    for s in range(k_states):
                        prod[s] *= msg[s]
            total_mass = sum(prod)
            if total_mass > 0.0:
                marginals[u] = [v / total_mass for v in prod]
            else:
                marginals[u] = [1.0 / k_states] * k_states

        root_pot = list(node_potentials[root])
        for c in children[root]:
            if (c, root) in messages:
                for s in range(len(root_pot)):
                    root_pot[s] *= messages[(c, root)][s]
        partition_z: float = sum(root_pot)

        return {
            "marginals": marginals,
            "messages": messages,
            "partition_function": partition_z,
        }

    def _compute_message(
        self,
        src: TNode,
        dst: TNode,
        tree_adjacency: Mapping[TNode, Collection[TNode]],
        node_potentials: Mapping[TNode, Sequence[float]],
        edge_potentials: Mapping[tuple[TNode, TNode], Sequence[Sequence[float]]],
        messages: Dict[tuple[TNode, TNode], List[float]],
        exclude: Optional[TNode],
    ) -> List[float]:
        """Computes directional message vector m_{src -> dst}."""
        psi_src = list(node_potentials[src])
        src_k = len(psi_src)

        prod_incoming = list(psi_src)
        for nbr in tree_adjacency.get(src, []):
            if nbr != exclude and (nbr, src) in messages:
                inc_msg = messages[(nbr, src)]
                for s in range(src_k):
                    prod_incoming[s] *= inc_msg[s]

        factor = edge_potentials.get((src, dst))
        is_transposed = False
        if factor is None:
            factor = edge_potentials.get((dst, src))
            is_transposed = True

        dst_k = len(node_potentials[dst])
        out_msg = [0.0] * dst_k

        if factor is not None:
            for j in range(dst_k):
                total = 0.0
                for i in range(src_k):
                    w = factor[j][i] if is_transposed else factor[i][j]
                    total += prod_incoming[i] * w
                out_msg[j] = total
        else:
            uniform_val = sum(prod_incoming)
            out_msg = [uniform_val] * dst_k

        norm_sum = sum(out_msg)
        if norm_sum > 0.0:
            return [v / norm_sum for v in out_msg]
        return [1.0 / dst_k] * dst_k
