"""
GRAPH SCHEMA MIGRATION AND ENTITY UPGRADE ENGINE
Implementation Module for KgAlgoSchemaMigrator (ALGO-KG-152).

Strict Zero-Inline-Comment Doctrine enforced.
"""
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoSchemaMigrator:
    """
    --- contract:
      id: ALGO-KG-152
      name: KgAlgoSchemaMigrator
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(Entities + Migrations)
        space: O(Entities)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - schema_migration
      - entity_evolution
      - structural_upgrade
      input_schema:
        entities: array
        migration_rules: array
      output_schema:
        algorithm: string
        migrated_entities: array
        applied_count: integer
    ---
    """
    def migrate(self, entities: List[Dict[str, Any]], migration_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        migrated: List[Dict[str, Any]] = []
        applied_count = 0
        for ent in entities:
            curr = dict(ent)
            for rule in migration_rules:
                action = rule.get("action")
                target_type = rule.get("target_type")
                if target_type and curr.get("type") != target_type:
                    continue
                if action == "rename_prop":
                    old_k, new_k = rule.get("from"), rule.get("to")
                    if old_k in curr:
                        curr[new_k] = curr.pop(old_k)
                        applied_count += 1
                elif action == "add_prop":
                    k, v = rule.get("prop"), rule.get("default")
                    if k not in curr:
                        curr[k] = v
                        applied_count += 1
                elif action == "remove_prop":
                    k = rule.get("prop")
                    if k in curr:
                        del curr[k]
                        applied_count += 1
                elif action == "change_type":
                    new_type = rule.get("new_type")
                    if new_type:
                        curr["type"] = new_type
                        applied_count += 1
            migrated.append(curr)
        return {
            "algorithm": "ALGO-KG-152",
            "migrated_entities": migrated,
            "applied_count": applied_count,
        }
