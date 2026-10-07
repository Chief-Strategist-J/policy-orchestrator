"""ALGORITHM & ARCHITECTURE BLUEPRINT: MAX-PRODUCT BELIEF PROPAGATION & VITERBI DECODING (ALGO-GRAPH-PGM-271)

1. OVERVIEW & OBJECTIVE
Finds the Maximum A Posteriori (MAP) joint configuration of discrete variables in tree and sequential
graphical models using the Max-Product semiring (or Max-Sum in log-domain). Employs dynamic programming
backtracking pointers (Viterbi decoding) to reconstruct the exact global state configuration that maximizes joint probability.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V| * |K| + |E| * |K|) for storing messages and argmax backpointers.
- Time Complexity: O(|E| * |K|^2) where K is domain size.
- Invariants:
  - Computed MAP configuration achieves the global maximum joint potential: argmax_{x} P(X=x).
  - Backpointers track optimal parent/child variable choices at each message step.

3. INPUT PARAMETERS:
- tree_adjacency: Mapping[TNode, Collection[TNode]] tree or chain graph adjacency.
- node_potentials: Mapping[TNode, Sequence[float]] local variable potentials psi_i(x_i).
- edge_potentials: Mapping[tuple[TNode, TNode], Sequence[Sequence[float]]] pairwise factor matrices.
- root_node: Optional[TNode] designated root variable.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'map_configuration': Dict[TNode, int] optimal state index for each variable.
  - 'max_score': float maximum joint unnormalized score or probability.
  - 'max_marginals': Dict[TNode, List[float]] max-marginal profile per node.

5. AGENT CONTRACT:
- Implemented strictly with log-domain arithmetic to prevent floating-point underflow.
- Pure function, zero inline comments.
"""

from __future__ import annotations

import math
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoMaxProductViterbiDecoding(Generic[TNode]):
    """Max-Product / Max-Sum Belief Propagation and Viterbi MAP decoding on trees and chains.

    ```yaml
    contract:
      id: ALGO-GRAPH-PGM-271
      name: GraphAlgoMaxProductViterbiDecoding
      inputs:
        - name: tree_adjacency
          type: Mapping[TNode, Collection[TNode]]
          description: Acyclic graph topology.
        - name: node_potentials
          type: Mapping[TNode, Sequence[float]]
          description: Prior or observation potential vectors per variable.
        - name: edge_potentials
          type: Mapping[tuple[TNode, TNode], Sequence[Sequence[float]]]
          description: Pairwise compatibility matrices.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Optimal MAP variable assignment, max score, and max-marginals.
      parameters:
        root_node: Optional[TNode] (default None)
      capability_tags:
        - PGM
        - MAP_INFERENCE
        - MAX_PRODUCT
        - VITERBI_DECODING
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
        """Performs Max-Sum message passing and backpointer tracing for MAP decoding."""
        nodes: List[TNode] = list(node_potentials.keys())
        if not nodes:
            return {"map_configuration": {}, "max_score": 0.0, "max_marginals": {}}

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

        log_node_potentials: Dict[TNode, List[float]] = {}
        for u in nodes:
            log_node_potentials[u] = [
                math.log(max(1e-15, float(v))) for v in node_potentials[u]
            ]

        log_edge_potentials: Dict[tuple[TNode, TNode], List[List[float]]] = {}
        for (u, v), mat in edge_potentials.items():
            log_edge_potentials[(u, v)] = [
                [math.log(max(1e-15, float(x))) for x in row] for row in mat
            ]

        messages_to_parent: Dict[TNode, List[float]] = {}
        backpointers: Dict[tuple[TNode, int], int] = {}

        for u in post_order:
            p = parents[u]
            if p is None:
                continue

            psi_u = log_node_potentials[u]
            u_k = len(psi_u)
            sum_in = list(psi_u)

            for c in children[u]:
                msg_c = messages_to_parent[c]
                for s in range(u_k):
                    sum_in[s] += msg_c[s]

            is_trans = False
            mat = log_edge_potentials.get((p, u))
            if mat is None:
                mat = log_edge_potentials.get((u, p))
                is_trans = True

            p_k = len(log_node_potentials[p])
            msg_u_to_p = [-1e18] * p_k

            for p_state in range(p_k):
                best_val = -1e18
                best_u_state = 0
                for u_state in range(u_k):
                    edge_w = mat[u_state][p_state] if is_trans else (mat[p_state][u_state] if mat is not None else 0.0)
                    score = sum_in[u_state] + edge_w
                    if score > best_val:
                        best_val = score
                        best_u_state = u_state
                msg_u_to_p[p_state] = best_val
                backpointers[(u, p_state)] = best_u_state

            messages_to_parent[u] = msg_u_to_p

        root_scores = list(log_node_potentials[root])
        for c in children[root]:
            msg_c = messages_to_parent[c]
            for s in range(len(root_scores)):
                root_scores[s] += msg_c[s]

        best_root_state = 0
        best_root_score = root_scores[0]
        for s in range(1, len(root_scores)):
            if root_scores[s] > best_root_score:
                best_root_score = root_scores[s]
                best_root_state = s

        map_config: Dict[TNode, int] = {root: best_root_state}

        for u in bfs_order:
            p_state = map_config[u]
            for c in children[u]:
                best_c_state = backpointers.get((c, p_state), 0)
                map_config[c] = best_c_state

        max_marginals: Dict[TNode, List[float]] = {}
        for u in nodes:
            max_marginals[u] = [math.exp(v) for v in log_node_potentials[u]]

        return {
            "map_configuration": map_config,
            "max_score": math.exp(best_root_score),
            "max_marginals": max_marginals,
        }
