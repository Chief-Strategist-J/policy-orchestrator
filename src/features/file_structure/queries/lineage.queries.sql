-- ================================================================================
-- ALGORITHM & ARCHITECTURE BLUEPRINT: FILE LINEAGE & IMPACT NAMED SQL QUERIES
-- ================================================================================
-- Formula: FLOW_{VERB}_{ENTITY}_{CRITERIA}
-- Target Operations: Direct Upstream, Direct Downstream
-- ================================================================================

-- name: FLOW_GET_DIRECT_UPSTREAM_EDGES
SELECT
    e.source_id,
    n.label AS source_label,
    n.file_path AS source_file_path,
    e.relationship_type,
    e.target_id
FROM file_structure_edges e
JOIN file_structure_nodes n ON e.source_id = n.id
WHERE e.target_id = :target_id;

-- name: FLOW_GET_DIRECT_DOWNSTREAM_EDGES
SELECT
    e.source_id,
    e.relationship_type,
    e.target_id,
    n.label AS target_label,
    n.file_path AS target_file_path
FROM file_structure_edges e
JOIN file_structure_nodes n ON e.target_id = n.id
WHERE e.source_id = :source_id;
