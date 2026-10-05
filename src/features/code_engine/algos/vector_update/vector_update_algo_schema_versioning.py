"""
================================================================================
ALGORITHM BLUEPRINT: SCHEMA AND METADATA VERSIONING (ALGO-VEC-UPD-141)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Enforces schema evolution and metadata field migrations (expand-and-contract pattern),
   validating mandatory lineage fields across version boundaries.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorUpdateAlgoSchemaVersioning:
    """
    --- contract:
      id: ALGO-VEC-UPD-141
      name: VectorUpdateAlgoSchemaVersioning
      category: update
      complexity: O(F)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        metadata: dict[str, Any]
        current_schema_version: int
        target_schema_version: int
        field_migration_map: dict[str, str]
      output_schema:
        migrated_metadata: dict[str, Any]
        effective_version: int
        is_valid: bool
        missing_lineage_fields: list[str]
    ---
    """

    MANDATORY_LINEAGE_FIELDS = ["source_id", "model_version"]

    @classmethod
    def migrate_record(
        cls,
        metadata: Dict[str, Any],
        current_schema_version: int = 1,
        target_schema_version: int = 2,
        field_migration_map: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        migrated = dict(metadata)
        if field_migration_map and current_schema_version < target_schema_version:
            for old_key, new_key in field_migration_map.items():
                if old_key in migrated:
                    migrated[new_key] = migrated[old_key]

        migrated["schema_version"] = target_schema_version

        missing = [f for f in cls.MANDATORY_LINEAGE_FIELDS if f not in migrated or not migrated[f]]

        return {
            "migrated_metadata": migrated,
            "effective_version": target_schema_version,
            "is_valid": len(missing) == 0,
            "missing_lineage_fields": missing,
        }
