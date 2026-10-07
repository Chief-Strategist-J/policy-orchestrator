"""Johnson's Elementary Cycle Enumeration Algorithm.

Provides exact detection and enumeration of all elementary cycles in directed graphs
using Donald B. Johnson's circuit-finding algorithm with vertex blocking and unblocking.
"""

from typing import Dict, Generic, Hashable, List, Set, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoJohnsonCycleEnumeration(Generic[TNode]):
    """
    ---
    contract: ALGO-GRAPH-TRV-21
    layer: Domain Algorithm
    status: Production-Ready
    deterministic: true
    complexity:
      time: O((V + E) * (C + 1))
      space: O(V + E)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        self._nodes: List[TNode] = list(adjacency.keys())
        self._adj: Dict[TNode, List[TNode]] = {u: list(neighbors) for u, neighbors in adjacency.items()}
        for u in self._nodes:
            for v in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []
                    self._nodes.append(v)
        self._node_to_idx: Dict[TNode, int] = {node: i for i, node in enumerate(self._nodes)}

    def has_cycle(self) -> bool:
        visited: Dict[TNode, int] = {u: 0 for u in self._nodes}
        for node in self._nodes:
            if visited[node] == 0:
                if self._detect_cycle_dfs(node, visited):
                    return True
        return False

    def _detect_cycle_dfs(self, u: TNode, visited: Dict[TNode, int]) -> bool:
        visited[u] = 1
        for v in self._adj.get(u, []):
            if visited.get(v, 0) == 1:
                return True
            if visited.get(v, 0) == 0 and self._detect_cycle_dfs(v, visited):
                return True
        visited[u] = 2
        return False

    def enumerate_cycles(self, max_cycles: int = 1000, max_length: int = 100) -> List[List[TNode]]:
        cycles: List[List[TNode]] = []
        n = len(self._nodes)
        
        for i in range(n):
            if len(cycles) >= max_cycles:
                break
            start_node = self._nodes[i]
            subgraph_nodes = {self._nodes[j] for j in range(i, n)}
            scc_nodes = self._get_scc_with_node(start_node, subgraph_nodes)
            if not scc_nodes or start_node not in scc_nodes:
                continue
                
            blocked: Set[TNode] = set()
            blocked_map: Dict[TNode, Set[TNode]] = {u: set() for u in scc_nodes}
            stack: List[TNode] = []
            
            def unblock(u: TNode) -> None:
                if u in blocked:
                    blocked.remove(u)
                    for w in list(blocked_map.get(u, set())):
                        blocked_map[u].remove(w)
                        unblock(w)

            def circuit(v: TNode) -> bool:
                found = False
                stack.append(v)
                blocked.add(v)
                
                for w in self._adj.get(v, []):
                    if w not in scc_nodes:
                        continue
                    if w == start_node:
                        if len(stack) <= max_length:
                            cycles.append(list(stack))
                        found = True
                        if len(cycles) >= max_cycles:
                            return True
                    elif w not in blocked:
                        if circuit(w):
                            found = True
                            if len(cycles) >= max_cycles:
                                return True
                                
                if found:
                    unblock(v)
                else:
                    for w in self._adj.get(v, []):
                        if w in scc_nodes:
                            blocked_map[w].add(v)
                stack.pop()
                return found

            circuit(start_node)
            
        return cycles

    def _get_scc_with_node(self, target: TNode, allowed: Set[TNode]) -> Set[TNode]:
        index = 0
        indices: Dict[TNode, int] = {}
        lowlinks: Dict[TNode, int] = {}
        on_stack: Set[TNode] = set()
        stack: List[TNode] = []
        target_scc: Set[TNode] = set()

        def strongconnect(v: TNode) -> None:
            nonlocal index
            indices[v] = index
            lowlinks[v] = index
            index += 1
            stack.append(v)
            on_stack.add(v)

            for w in self._adj.get(v, []):
                if w not in allowed:
                    continue
                if w not in indices:
                    strongconnect(w)
                    lowlinks[v] = min(lowlinks[v], lowlinks[w])
                elif w in on_stack:
                    lowlinks[v] = min(lowlinks[v], indices[w])

            if lowlinks[v] == indices[v]:
                scc: Set[TNode] = set()
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.add(w)
                    if w == v:
                        break
                if target in scc:
                    target_scc.update(scc)

        for node in allowed:
            if node not in indices:
                strongconnect(node)
                if target_scc:
                    return target_scc
        return target_scc
