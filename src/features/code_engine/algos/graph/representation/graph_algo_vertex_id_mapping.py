"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: VERTEX ID DICTIONARY MAPPING (ALGO-GRAPH-REP-10)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Provides high-performance, bidirectional symbol-to-dense-integer ID mapping
   for arbitrary node types (UUIDs, URIs, strings, custom entity models).
   Enables 0-indexed dense array indexing for CSR/CSC, matrices, and GNN tensors,
   while translating query results back to human-readable external identifiers.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(1) expected lookup in both directions, O(V log V) deterministic creation.
   - Space Complexity: O(V) compact dictionary storage.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Builder.
   - Rule: Never compare internal integer IDs across different snapshots.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar

NodeId = TypeVar("NodeId")


class GraphAlgoVertexIdMapping(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-REP-10
      name: GraphAlgoVertexIdMapping
      version: 1.0.0
      category: graph_representation
      capability_tags: [graph, representation, vertex_id_mapping, dictionary_encoding, symbol_table]
      inputs:
        type: object
        required: [symbols]
        properties:
          symbols:
            type: array
            items: {type: string}
      outputs:
        type: object
        required: [symbol_to_int, int_to_symbol, size]
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V log V)
        space: O(V)
    ---
    """

    @staticmethod
    def create_mapping(
        symbols: List[str],
        start_index: int = 0,
    ) -> Dict[str, Any]:
        unique_symbols = sorted(list(dict.fromkeys(symbols)))
        symbol_to_int: Dict[str, int] = {
            sym: start_index + idx for idx, sym in enumerate(unique_symbols)
        }
        int_to_symbol: List[str] = unique_symbols

        return {
            "symbol_to_int": symbol_to_int,
            "int_to_symbol": int_to_symbol,
            "start_index": start_index,
            "size": len(unique_symbols),
        }

    @staticmethod
    def encode_edges(
        edges: List[Dict[str, Any]],
        symbol_to_int: Dict[str, int],
    ) -> List[Tuple[int, int, float]]:
        encoded: List[Tuple[int, int, float]] = []
        for edge in edges:
            src = str(edge.get("source", ""))
            tgt = str(edge.get("target", ""))
            wt = float(edge.get("weight", 1.0))
            if src in symbol_to_int and tgt in symbol_to_int:
                encoded.append((symbol_to_int[src], symbol_to_int[tgt], wt))
        return encoded

    @staticmethod
    def decode_path(
        integer_path: List[int],
        int_to_symbol: List[str],
        start_index: int = 0,
    ) -> List[str]:
        decoded: List[str] = []
        for idx in integer_path:
            pos = idx - start_index
            if 0 <= pos < len(int_to_symbol):
                decoded.append(int_to_symbol[pos])
        return decoded
