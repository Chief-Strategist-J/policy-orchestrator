"""
MULTI-TURN CHAT DIALOG DYNAMIC RELATION EXTRACTOR
Implementation Module for KgAlgoDialogRelationExtractor (ALGO-KG-183).

Strict Zero-Inline-Comment Doctrine enforced.
"""
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoDialogRelationExtractor:
    """
    --- contract:
      id: ALGO-KG-183
      name: KgAlgoDialogRelationExtractor
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(Turns)
        space: O(Extracted_Relations)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - dialog_extraction
      - conversational_kg
      - dynamic_relation_mining
      input_schema:
        turns: array
      output_schema:
        algorithm: string
        extracted_triples: array
    ---
    """
    def extract_from_dialog(self, turns: List[Dict[str, str]]) -> Dict[str, Any]:
        triples: List[Tuple[str, str, str]] = []
        user_entity = "User"
        for turn in turns:
            speaker = turn.get("speaker", "unknown")
            text = turn.get("text", "")
            if "likes" in text.lower():
                parts = text.lower().split("likes")
                if len(parts) == 2:
                    triples.append((speaker, "likes", parts[1].strip().strip(".")))
            elif "working on" in text.lower():
                parts = text.lower().split("working on")
                if len(parts) == 2:
                    triples.append((speaker, "works_on", parts[1].strip().strip(".")))
        return {
            "algorithm": "ALGO-KG-183",
            "extracted_triples": triples,
            "turns_processed": len(turns),
        }
