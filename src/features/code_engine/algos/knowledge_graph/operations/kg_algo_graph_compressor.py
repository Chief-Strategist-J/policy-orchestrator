"""
GRAPH ADJACENCY BITMAP COMPRESSION AND COMPACT ENCODING
Implementation Module for KgAlgoGraphCompressor (ALGO-KG-159).

Strict Zero-Inline-Comment Doctrine enforced.
"""
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoGraphCompressor:
    """
    --- contract:
      id: ALGO-KG-159
      name: KgAlgoGraphCompressor
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(V * D)
        space: O(Compressed_Bytes)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - graph_compression
      - varint_encoding
      - adjacency_deltas
      input_schema:
        sorted_adj_list: object
      output_schema:
        algorithm: string
        compressed_deltas: object
        compression_ratio: number
    ---
    """
    def compress_adjacency(self, adj: Dict[int, List[int]]) -> Dict[str, Any]:
        compressed: Dict[str, List[int]] = {}
        raw_ints = 0
        comp_ints = 0
        for node, neighbors in adj.items():
            sorted_neighs = sorted(list(set(neighbors)))
            raw_ints += len(sorted_neighs)
            deltas: List[int] = []
            prev = 0
            for i, target in enumerate(sorted_neighs):
                if i == 0:
                    deltas.append(target - node)
                else:
                    deltas.append(target - prev - 1)
                prev = target
            compressed[str(node)] = deltas
            comp_ints += len(deltas)
        ratio = (comp_ints / max(1, raw_ints)) if raw_ints > 0 else 1.0
        return {
            "algorithm": "ALGO-KG-159",
            "compressed_deltas": compressed,
            "raw_edges_count": raw_ints,
            "compression_ratio": round(ratio, 4),
        }
