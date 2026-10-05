"""
================================================================================
ALGORITHM BLUEPRINT: INSTRUCTION & QUERY PREFIXES (ALGO-VEC-TRFM-06)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Applies deterministic asymmetric task prefixes ("query: ", "passage: ", or custom
   instruction prompts) to raw text prior to tokenization. Validates prefix consistency
   against model configuration to prevent cross-space corruption (V2/V3 compliance).

2. ARCHITECTURAL ROLE:
   Transformer and Retriever role (Layer 1). Guarantees consistent vector space
   partitioning across asymmetric query-document retrieval models (e.g. E5, BGE, GTE).

3. EXECUTION FLOW:
   a. Check text and prompt configuration.
   b. Look up prefix by task type ('query', 'document', 'clustering', 'classification').
   c. If custom instruction is provided, prepend formatted prompt template.
   d. Return prefixed text, prefix applied, and audit metadata.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorTransformAlgoInstructionPrefixes:
    """
    --- contract:
      id: ALGO-VEC-TRFM-06
      name: VectorTransformAlgoInstructionPrefixes
      category: transform
      complexity: O(|text|)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        text: str
        task_type: str
        model_family: str
        custom_instruction: str
      output_schema:
        task_type: str
        prefix_applied: str
        original_length: int
        prefixed_length: int
        prefixed_text: str
    ---
    """

    DEFAULT_PREFIXES = {
        "e5": {
            "query": "query: ",
            "document": "passage: ",
            "symmetric": "",
        },
        "bge": {
            "query": "Represent this sentence for searching relevant passages: ",
            "document": "",
            "symmetric": "",
        },
        "gte": {
            "query": "Represent this query for retrieving relevant documents: ",
            "document": "",
            "symmetric": "",
        },
    }

    @staticmethod
    def apply_prefix(
        text: str,
        task_type: str = "query",
        model_family: str = "e5",
        custom_instruction: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not text:
            return {
                "task_type": task_type,
                "prefix_applied": "",
                "original_length": 0,
                "prefixed_length": 0,
                "prefixed_text": "",
            }

        orig_len = len(text)

        if custom_instruction:
            prefix = custom_instruction.strip() + " "
        else:
            family_prefixes = VectorTransformAlgoInstructionPrefixes.DEFAULT_PREFIXES.get(
                model_family.lower(),
                VectorTransformAlgoInstructionPrefixes.DEFAULT_PREFIXES["e5"],
            )
            prefix = family_prefixes.get(task_type.lower(), "")

        prefixed_text = prefix + text

        return {
            "task_type": task_type,
            "prefix_applied": prefix,
            "original_length": orig_len,
            "prefixed_length": len(prefixed_text),
            "prefixed_text": prefixed_text,
        }
