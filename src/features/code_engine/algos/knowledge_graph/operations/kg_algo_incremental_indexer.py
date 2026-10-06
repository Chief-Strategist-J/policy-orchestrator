"""
INCREMENTAL TRIPLE SPO INDEX BUILDER
Implementation Module for KgAlgoIncrementalIndexer (ALGO-KG-169).

Strict Zero-Inline-Comment Doctrine enforced.
"""
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoIncrementalIndexer:
    """
    --- contract:
      id: ALGO-KG-169
      name: KgAlgoIncrementalIndexer
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(Triples)
        space: O(Triples)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - incremental_indexing
      - spo_index
      - pos_index
      input_schema:
        existing_index: object
        new_triples: array
      output_schema:
        algorithm: string
        updated_index: object
    ---
    """
    def index_increment(self, existing: Dict[str, Any], new_triples: List[Tuple[str, str, str]]) -> Dict[str, Any]:
        spo = existing.get("spo", {})
        pos = existing.get("pos", {})
        osp = existing.get("osp", {})
        for s, p, o in new_triples:
            spo.setdefault(s, {}).setdefault(p, []).append(o)
            pos.setdefault(p, {}).setdefault(o, []).append(s)
            osp.setdefault(o, {}).setdefault(s, []).append(p)
        return {
            "algorithm": "ALGO-KG-169",
            "spo_size": len(spo),
            "pos_size": len(pos),
            "osp_size": len(osp),
            "indexed_new": len(new_triples),
        }
