"""
================================================================================
ALGORITHM BLUEPRINT: SCIP & LSIF CODE INTELLIGENCE INDEX
================================================================================

1. OVERVIEW:
   SCIP (Sourcegraph Code Intelligence Protocol) and LSIF (Language Server Index
   Format) are precomputed symbol graph index formats. By indexing compiler-accurate
   definitions, references, and hover documentation into globally unique symbol URIs
   (`scheme manager package version descriptor`), SCIP allows sub-millisecond
   cross-repository code navigation and reference discovery without running active
   language server instances.

2. SCIP SYMBOL URI SYNTAX:
   - Format: `<scheme> <manager> <package_name> <version> <descriptor>`
   - Example: `scip-python pypi requests 2.31.0 requests.get().`
   - Document Occurrence:
       - Range: [start_line, start_col, end_line, end_col]
       - Symbol: globally qualified symbol string
       - Symbol Roles: Definition (1), Reference (2), Read (4), Write (8).

3. COMPLEXITY ANALYSIS:
   - Query: O(1) hash map lookup for symbol occurrences across multiple files.
   - Storage: Compact Protobuf / JSON structured document format.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside function bodies.
================================================================================
"""

from typing import Dict, List, Any, Optional, Set


class SearchEngineScipLsifIndexAlgo:
    """
    Implements SCIP/LSIF code intelligence index generation, document indexing, and cross-reference queries.
    """

    def __init__(self) -> None:
        self._symbol_index: Dict[str, List[Dict[str, Any]]] = {}
        self._documents: Dict[str, Dict[str, Any]] = {}

    def format_symbol_uri(self, scheme: str, manager: str, package: str, version: str, descriptor: str) -> str:
        """
        Formats a standardized SCIP symbol identifier.
        """
        return f"{scheme} {manager} {package} {version} {descriptor}"

    def add_occurrence(
        self,
        document_uri: str,
        symbol_uri: str,
        range_coords: List[int],
        role: str = "reference",
        docstring: Optional[str] = None
    ) -> None:
        """
        Registers a symbol occurrence in a document.
        """
        occ = {
            "document_uri": document_uri,
            "range": range_coords,
            "role": role,
            "docstring": docstring
        }
        if symbol_uri not in self._symbol_index:
            self._symbol_index[symbol_uri] = []
        self._symbol_index[symbol_uri].append(occ)

        if document_uri not in self._documents:
            self._documents[document_uri] = {"occurrences": []}
        self._documents[document_uri]["occurrences"].append({
            "symbol": symbol_uri,
            "range": range_coords,
            "role": role
        })

    def find_references(self, symbol_uri: str) -> List[Dict[str, Any]]:
        """
        Finds all reference occurrences of the given symbol URI.
        """
        all_occs = self._symbol_index.get(symbol_uri, [])
        return [occ for occ in all_occs if occ["role"] == "reference"]

    def find_definition(self, symbol_uri: str) -> Optional[Dict[str, Any]]:
        """
        Finds the primary definition occurrence of the symbol URI.
        """
        all_occs = self._symbol_index.get(symbol_uri, [])
        for occ in all_occs:
            if occ["role"] == "definition":
                return occ
        return None

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes SCIP indexing and symbol queries.
        """
        occurrences_raw = payload.get("occurrences", [])
        query_symbol = payload.get("query_symbol")

        for occ in occurrences_raw:
            self.add_occurrence(
                document_uri=str(occ.get("document_uri", "")),
                symbol_uri=str(occ.get("symbol_uri", "")),
                range_coords=occ.get("range", [1, 0, 1, 10]),
                role=str(occ.get("role", "reference")),
                docstring=occ.get("docstring")
            )

        definition = None
        references = []
        if query_symbol:
            s_sym = str(query_symbol)
            definition = self.find_definition(s_sym)
            references = self.find_references(s_sym)

        return {
            "algorithm": "ALGO-SRCH-91",
            "indexed_symbols_count": len(self._symbol_index),
            "indexed_documents_count": len(self._documents),
            "query_symbol": query_symbol,
            "definition": definition,
            "references": references,
            "reference_count": len(references)
        }
