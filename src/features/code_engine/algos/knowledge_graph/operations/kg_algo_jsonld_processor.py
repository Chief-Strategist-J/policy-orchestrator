"""
JSON-LD CONTEXT EXPANSION AND GRAPH FLATTENER
Implementation Module for KgAlgoJsonldProcessor (ALGO-KG-164).

Strict Zero-Inline-Comment Doctrine enforced.
"""
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoJsonldProcessor:
    """
    --- contract:
      id: ALGO-KG-164
      name: KgAlgoJsonldProcessor
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(Fields)
        space: O(Triples)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - jsonld_expansion
      - jsonld_flattening
      - semantic_interop
      input_schema:
        doc: object
      output_schema:
        algorithm: string
        flattened_triples: array
    ---
    """
    def expand_and_flatten(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        context = doc.get("@context", {})
        doc_id = doc.get("@id", "urn:node:root")
        triples: List[Tuple[str, str, str]] = []
        for k, v in doc.items():
            if k.startswith("@"):
                continue
            expanded_pred = context.get(k, k)
            if isinstance(v, dict):
                nested_id = v.get("@id", f"urn:node:{k}")
                triples.append((doc_id, expanded_pred, nested_id))
                nested_res = self.expand_and_flatten(v)
                triples.extend(nested_res["flattened_triples"])
            elif isinstance(v, list):
                for item in v:
                    triples.append((doc_id, expanded_pred, str(item)))
            else:
                triples.append((doc_id, expanded_pred, str(v)))
        return {
            "algorithm": "ALGO-KG-164",
            "flattened_triples": triples,
            "triple_count": len(triples),
        }
