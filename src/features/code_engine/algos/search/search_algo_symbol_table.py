"""
================================================================================
ALGORITHM BLUEPRINT: HIERARCHICAL LEXICAL SYMBOL TABLE
================================================================================

1. OVERVIEW:
   A Hierarchical Lexical Symbol Table maps identifier names to their semantic
   definitions (type, kind, definition location, visibility) across nested scopes
   (global, module, class, function, block). Resolves variable lookups by traversing
   the lexical scope chain from innermost to outermost, tracking symbol shadowing
   and scope lifetime.

2. SCOPE CHAIN LIFECYCLE:
   - Push Scope: Enters block or function; creates child scope with parent pointer.
   - Declare Symbol: Inserts (name -> {kind, type, lineno, col}) in current scope.
   - Resolve Symbol: Searches current scope; if absent, recursively queries parent scope.
   - Pop Scope: Exits block; restores previous active scope.

3. COMPLEXITY ANALYSIS:
   - Insert: O(1) in active scope dictionary.
   - Resolution: O(D) where D is scope nesting depth (typically <= 10).

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, List, Any, Optional, Tuple


class LexicalScope:
    def __init__(self, name: str, scope_type: str, parent: Optional["LexicalScope"] = None) -> None:
        self.name: str = name
        self.scope_type: str = scope_type
        self.parent: Optional["LexicalScope"] = parent
        self.symbols: Dict[str, Dict[str, Any]] = {}
        self.children: List["LexicalScope"] = []


class SearchEngineSymbolTableAlgo:
    """
    --- contract:
      id: ALGO-SRCH-84
      name: SearchEngineSymbolTableAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(1) average
        space: O(TotalSymbols)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - symbol_table.indexer
      - identifiers.lookup
      - scope.symbols
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def __init__(self) -> None:
        self._global_scope: LexicalScope = LexicalScope("global", "global", None)
        self._current_scope: LexicalScope = self._global_scope

    def enter_scope(self, name: str, scope_type: str = "function") -> LexicalScope:
        new_scope = LexicalScope(name, scope_type, parent=self._current_scope)
        self._current_scope.children.append(new_scope)
        self._current_scope = new_scope
        return new_scope

    def exit_scope(self) -> None:
        if self._current_scope.parent:
            self._current_scope = self._current_scope.parent

    def define(self, name: str, kind: str, symbol_type: str = "Any", lineno: int = 1) -> None:
        self._current_scope.symbols[name] = {
            "name": name,
            "kind": kind,
            "type": symbol_type,
            "lineno": lineno,
            "scope": self._current_scope.name
        }

    def resolve(self, name: str) -> Optional[Dict[str, Any]]:
        curr = self._current_scope
        depth = 0
        while curr is not None:
            if name in curr.symbols:
                res = dict(curr.symbols[name])
                res["resolution_depth"] = depth
                res["is_shadowed"] = depth > 0
                return res
            curr = curr.parent
            depth += 1
        return None

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        declarations = payload.get("declarations", [])
        lookups = payload.get("lookups", [])

        self._global_scope = LexicalScope("global", "global", None)
        self._current_scope = self._global_scope

        for d in declarations:
            action = str(d.get("action", "define")).lower()
            if action == "enter":
                self.enter_scope(str(d.get("name", "inner")), str(d.get("type", "function")))
            elif action == "exit":
                self.exit_scope()
            elif action == "define":
                self.define(
                    name=str(d.get("name", "")),
                    kind=str(d.get("kind", "var")),
                    symbol_type=str(d.get("type", "Any")),
                    lineno=int(d.get("lineno", 1))
                )

        lookup_results: Dict[str, Any] = {}
        for l in lookups:
            name = str(l)
            lookup_results[name] = self.resolve(name)

        return {
            "algorithm": "ALGO-SRCH-87",
            "active_scope": self._current_scope.name,
            "lookup_results": lookup_results
        }
