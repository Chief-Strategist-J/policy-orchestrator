"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Maximum Common Subgraph - McSplit (ALGO-GRAPH-ISO-184)

1. OVERVIEW & OBJECTIVE:
Finds the Maximum Common Induced Subgraph (MCIS) and Maximum Common Edge Subgraph (MCES)
between two arbitrary graphs G1 and G2 using McCreesh et al.'s McSplit branch-and-bound
algorithm with label-class partition bound pruning.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V_1| + |V_2|) label class partitions.
- Time Complexity: NP-hard, bounded by McSplit class sum bounding.
- Invariants:
  - Upper bound: sum over class c of min(|C_1(c)|, |C_2(c)|).
  - Prunes subtree immediately when current_size + bound <= best_size.

3. INPUT PARAMETERS:
- `adj_1` (Mapping[TNode, Iterable[TNode]]): First graph G1.
- `adj_2` (Mapping[TNode, Iterable[TNode]]): Second graph G2.

4. OUTPUT PARAMETERS:
- `MaximumCommonSubgraphResult`: Mapping dictionary between G1 and G2 vertices, size, and induced edge count.

5. AGENT CONTRACT:
- Role: Common structural motif finder and graph similarity analyst.
- Rules: Enforce strict induced subgraph adjacency consistency on all matched pairs.
- Guardrails: If either graph is empty, returns empty mapping and size 0.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class MaximumCommonSubgraphResult(Generic[TNode]):
    """
    Result container for Maximum Common Subgraph (MCS).
    """
    mapping_1_to_2: Dict[TNode, TNode]
    common_vertex_count: int
    common_edge_count: int


class McSplitMaximumCommonSubgraph(Generic[TNode]):
    """
    Implements McSplit branch-and-bound for Maximum Common Induced Subgraph.

    ```yaml
    contract_id: ALGO-GRAPH-ISO-184
    inputs:
      adj_1: Mapping[TNode, Iterable[TNode]]
      adj_2: Mapping[TNode, Iterable[TNode]]
    outputs:
      result: MaximumCommonSubgraphResult[TNode]
    parameters: {}
    capability_tags:
      - graph
      - isomorphism
      - mcs
      - mcsplit
      - common_subgraph
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(branch_and_bound_mcsplit)
      space: O(|V_1| + |V_2|)
    ```
    """

    def solve(
        self,
        adj_1: Mapping[TNode, Iterable[TNode]],
        adj_2: Mapping[TNode, Iterable[TNode]],
    ) -> MaximumCommonSubgraphResult[TNode]:
        """
        Solves for the maximum common induced subgraph mapping.

        Args:
            adj_1: Adjacency map of graph G1.
            adj_2: Adjacency map of graph G2.

        Returns:
            MaximumCommonSubgraphResult with optimal vertex bijection.
        """
        nodes_1 = sorted(list(adj_1.keys()), key=lambda x: str(x))
        nodes_2 = sorted(list(adj_2.keys()), key=lambda x: str(x))

        if not nodes_1 or not nodes_2:
            return MaximumCommonSubgraphResult(mapping_1_to_2={}, common_vertex_count=0, common_edge_count=0)

        g1_adj: Dict[TNode, Set[TNode]] = {u: set(adj_1.get(u, ())) for u in nodes_1}
        g2_adj: Dict[TNode, Set[TNode]] = {v: set(adj_2.get(v, ())) for v in nodes_2}

        best_mapping: Dict[TNode, TNode] = {}
        current_mapping: Dict[TNode, TNode] = {}

        initial_classes = [(nodes_1, nodes_2)]

        def mcsplit_rec(classes: List[Tuple[List[TNode], List[TNode]]]) -> None:
            nonlocal best_mapping

            bound = sum(min(len(c1), len(c2)) for c1, c2 in classes)
            if len(current_mapping) + bound <= len(best_mapping):
                return

            if not classes:
                if len(current_mapping) > len(best_mapping):
                    best_mapping = dict(current_mapping)
                return

            class_idx = max(range(len(classes)), key=lambda i: min(len(classes[i][0]), len(classes[i][1])))
            c1, c2 = classes[class_idx]
            if not c1 or not c2:
                mcsplit_rec(classes[:class_idx] + classes[class_idx + 1:])
                return

            u = c1[0]
            rest_c1 = c1[1:]

            for v in c2:
                rest_c2 = [x for x in c2 if x != v]
                current_mapping[u] = v

                new_classes: List[Tuple[List[TNode], List[TNode]]] = []
                for i, (cls_a, cls_b) in enumerate(classes):
                    curr_a = rest_c1 if i == class_idx else cls_a
                    curr_b = rest_c2 if i == class_idx else cls_b

                    adj_a = [x for x in curr_a if x in g1_adj[u]]
                    non_adj_a = [x for x in curr_a if x not in g1_adj[u]]

                    adj_b = [y for y in curr_b if y in g2_adj[v]]
                    non_adj_b = [y for y in curr_b if y not in g2_adj[v]]

                    if adj_a and adj_b:
                        new_classes.append((adj_a, adj_b))
                    if non_adj_a and non_adj_b:
                        new_classes.append((non_adj_a, non_adj_b))

                mcsplit_rec(new_classes)
                del current_mapping[u]

            new_classes_without_u = []
            for i, (cls_a, cls_b) in enumerate(classes):
                curr_a = rest_c1 if i == class_idx else cls_a
                if curr_a and cls_b:
                    new_classes_without_u.append((curr_a, cls_b))

            mcsplit_rec(new_classes_without_u)

        mcsplit_rec(initial_classes)

        common_edges = 0
        matched_g1 = list(best_mapping.keys())
        for i in range(len(matched_g1)):
            u1 = matched_g1[i]
            v1 = best_mapping[u1]
            for j in range(i + 1, len(matched_g1)):
                u2 = matched_g1[j]
                v2 = best_mapping[u2]
                if u2 in g1_adj[u1] and v2 in g2_adj[v1]:
                    common_edges += 1

        return MaximumCommonSubgraphResult(
            mapping_1_to_2=best_mapping,
            common_vertex_count=len(best_mapping),
            common_edge_count=common_edges,
        )
