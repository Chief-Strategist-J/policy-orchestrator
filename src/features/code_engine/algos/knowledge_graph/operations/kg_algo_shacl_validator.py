"""
SHACL GRAPH CONSTRAINTS AND SHAPE CONFORMANCE VALIDATOR
Implementation Module for KgAlgoShaclValidator (ALGO-KG-157).

Strict Zero-Inline-Comment Doctrine enforced.
"""
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoShaclValidator:
    """
    --- contract:
      id: ALGO-KG-157
      name: KgAlgoShaclValidator
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(Entities * Shapes)
        space: O(Violations)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - shacl_validation
      - shape_conformance
      - schema_integrity
      input_schema:
        entities: array
        shapes: array
      output_schema:
        algorithm: string
        conforms: boolean
        violations: array
    ---
    """
    def validate_shapes(self, entities: List[Dict[str, Any]], shapes: List[Dict[str, Any]]) -> Dict[str, Any]:
        violations: List[Dict[str, Any]] = []
        for ent in entities:
            ent_id = ent.get("id", "unknown")
            ent_type = ent.get("type")
            for shape in shapes:
                if shape.get("target_class") != ent_type:
                    continue
                for prop_shape in shape.get("property_shapes", []):
                    prop_path = prop_shape.get("path")
                    min_count = prop_shape.get("min_count", 0)
                    max_count = prop_shape.get("max_count", float('inf'))
                    val = ent.get(prop_path)
                    count = 0 if val is None else (len(val) if isinstance(val, list) else 1)
                    if count < min_count:
                        violations.append({
                            "entity_id": ent_id,
                            "shape": shape.get("id"),
                            "property": prop_path,
                            "violation": f"Min count violation: expected >={min_count}, got {count}",
                        })
                    if count > max_count:
                        violations.append({
                            "entity_id": ent_id,
                            "shape": shape.get("id"),
                            "property": prop_path,
                            "violation": f"Max count violation: expected <={max_count}, got {count}",
                        })
                    expected_datatype = prop_shape.get("datatype")
                    if expected_datatype and val is not None:
                        if expected_datatype == "int" and not isinstance(val, int):
                            violations.append({"entity_id": ent_id, "property": prop_path, "violation": "Datatype mismatch: expected int"})
                        elif expected_datatype == "str" and not isinstance(val, str):
                            violations.append({"entity_id": ent_id, "property": prop_path, "violation": "Datatype mismatch: expected str"})
        return {
            "algorithm": "ALGO-KG-157",
            "conforms": len(violations) == 0,
            "violation_count": len(violations),
            "violations": violations,
        }
