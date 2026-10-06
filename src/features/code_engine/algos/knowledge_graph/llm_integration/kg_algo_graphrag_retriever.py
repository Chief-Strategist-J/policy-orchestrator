"""
GRAPHRAG FOCUSED SUBGRAPH RETRIEVER AND PROMPT PACKER
Implementation Module for KgAlgoGraphragRetriever (ALGO-KG-171).

Strict Zero-Inline-Comment Doctrine enforced.
"""
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoGraphragRetriever:
    """
    --- contract:
      id: ALGO-KG-171
      name: KgAlgoGraphragRetriever
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(Entities * Hops)
        space: O(Prompt_Context)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - graphrag
      - prompt_packing
      - subgraph_retrieval
      input_schema:
        matched_entities: array
        triples: array
        max_hops: integer
      output_schema:
        algorithm: string
        retrieved_triples: array
        context_prompt: string
    ---
    """
    def retrieve_context(self, entities: List[str], triples: List[Tuple[str, str, str]], max_triples: int = 20) -> Dict[str, Any]:
        ent_set = set(entities)
        matched = [t for t in triples if t[0] in ent_set or t[2] in ent_set]
        selected = matched[:max_triples]
        lines = [f"- ({s}) --[{p}]--> ({o})" for s, p, o in selected]
        prompt_block = "### Knowledge Graph Context:\n" + "\n".join(lines) if lines else "No graph context found."
        return {
            "algorithm": "ALGO-KG-171",
            "retrieved_triples": selected,
            "context_prompt": prompt_block,
            "count": len(selected),
        }
