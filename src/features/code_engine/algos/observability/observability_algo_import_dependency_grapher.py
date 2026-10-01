"""
Module: search_engine_algo_import_dependency_grapher
Architecture: Search Engine Algorithm 21 — Import Dependency Grapher and Cycle Detector

Blueprint:
- Parses import statements (standard library, third-party, local relative/absolute imports).
- Constructs a directed graph (DAG / Digraph) of module dependencies.
- Runs Tarjan's Strongly Connected Components (SCC) or DFS cycle detector to flag circular import loops.
- Computes topological build order and isolated orphan modules.
- Zero-Inline-Comment Doctrine strictly enforced.
"""

from __future__ import annotations
import ast
import os
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple


@dataclass
class ImportNode:
    module_path: str
    direct_imports: Set[str] = field(default_factory=set)
    imported_by: Set[str] = field(default_factory=set)


@dataclass
class DependencyGraphReport:
    total_modules: int
    total_edges: int
    has_cycles: bool
    cycles: List[List[str]]
    topological_order: List[str]
    orphan_modules: List[str]


class ImportDependencyGrapher:
    def __init__(self) -> None:
        self.nodes: Dict[str, ImportNode] = {}

    def add_module_from_source(self, module_name: str, code: str) -> ImportNode:
        node = self._get_or_create(module_name)
        try:
            tree = ast.parse(code)
            for item in ast.walk(tree):
                if isinstance(item, ast.Import):
                    for alias in item.names:
                        target = alias.name.split(".")[0]
                        node.direct_imports.add(target)
                        self._get_or_create(target).imported_by.add(module_name)
                elif isinstance(item, ast.ImportFrom):
                    if item.module:
                        target = item.module.split(".")[0]
                        node.direct_imports.add(target)
                        self._get_or_create(target).imported_by.add(module_name)
        except SyntaxError:
            pass
        return node

    def _get_or_create(self, name: str) -> ImportNode:
        if name not in self.nodes:
            self.nodes[name] = ImportNode(module_path=name)
        return self.nodes[name]

    def detect_cycles(self) -> List[List[str]]:
        visited: Dict[str, int] = {k: 0 for k in self.nodes}
        cycles: List[List[str]] = []
        stack: List[str] = []

        def dfs(node_key: str):
            visited[node_key] = 1
            stack.append(node_key)
            for neighbor in self.nodes[node_key].direct_imports:
                if neighbor in visited:
                    if visited[neighbor] == 1:
                        cycle_start_idx = stack.index(neighbor)
                        cycles.append(list(stack[cycle_start_idx:] + [neighbor]))
                    elif visited[neighbor] == 0:
                        dfs(neighbor)
            stack.pop()
            visited[node_key] = 2

        for node_key in list(self.nodes.keys()):
            if visited[node_key] == 0:
                dfs(node_key)

        return cycles

    def topological_sort(self) -> List[str]:
        in_degrees: Dict[str, int] = {k: 0 for k in self.nodes}
        for node in self.nodes.values():
            for target in node.direct_imports:
                if target in in_degrees:
                    in_degrees[target] += 1

        queue = [k for k, deg in in_degrees.items() if deg == 0]
        order: List[str] = []

        while queue:
            curr = queue.pop(0)
            order.append(curr)
            for target in self.nodes[curr].direct_imports:
                if target in in_degrees:
                    in_degrees[target] -= 1
                    if in_degrees[target] == 0:
                        queue.append(target)

        return order

    def build_report(self) -> DependencyGraphReport:
        cycles = self.detect_cycles()
        order = self.topological_sort()
        orphans = [
            k for k, node in self.nodes.items()
            if len(node.direct_imports) == 0 and len(node.imported_by) == 0
        ]
        total_edges = sum(len(node.direct_imports) for node in self.nodes.values())

        return DependencyGraphReport(
            total_modules=len(self.nodes),
            total_edges=total_edges,
            has_cycles=len(cycles) > 0,
            cycles=cycles,
            topological_order=order,
            orphan_modules=orphans,
        )
