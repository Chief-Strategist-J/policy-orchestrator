-- ================================================================================
-- ALGORITHM & ARCHITECTURE BLUEPRINT: FILE STRUCTURE NAMED SQL QUERIES
-- ================================================================================
-- Formula: FLOW_{VERB}_{ENTITY}_{CRITERIA}
-- All queries are parameterized. Raw inline SQL construction is strictly forbidden.
-- ================================================================================

-- name: FLOW_INSERT_FILE_NODE
INSERT INTO file_structure_nodes (
    id,
    label,
    file_path,
    feature_name,
    properties_json,
    created_at,
    updated_at
) VALUES (
    :id,
    :label,
    :file_path,
    :feature_name,
    :properties_json,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (id) DO UPDATE SET
    label = EXCLUDED.label,
    file_path = EXCLUDED.file_path,
    feature_name = EXCLUDED.feature_name,
    properties_json = EXCLUDED.properties_json,
    updated_at = CURRENT_TIMESTAMP;

-- name: FLOW_GET_FILE_NODE_BY_ID
SELECT
    id,
    label,
    file_path,
    feature_name,
    properties_json,
    created_at,
    updated_at
FROM file_structure_nodes
WHERE id = :id;

-- name: FLOW_FIND_FILE_NODES_BY_FEATURE_NAME
SELECT
    id,
    label,
    file_path,
    feature_name,
    properties_json,
    created_at,
    updated_at
FROM file_structure_nodes
WHERE feature_name = :feature_name
ORDER BY label ASC, id ASC;

-- name: FLOW_FIND_FILE_NODES_BY_LABEL
SELECT
    id,
    label,
    file_path,
    feature_name,
    properties_json,
    created_at,
    updated_at
FROM file_structure_nodes
WHERE label = :label
ORDER BY feature_name ASC, id ASC;

-- name: FLOW_LIST_ALL_FILE_NODES
SELECT
    id,
    label,
    file_path,
    feature_name,
    properties_json,
    created_at,
    updated_at
FROM file_structure_nodes
ORDER BY feature_name ASC, label ASC, id ASC;

-- name: FLOW_COUNT_FILE_NODES_BY_FEATURE
SELECT
    feature_name,
    COUNT(id) AS total_nodes
FROM file_structure_nodes
GROUP BY feature_name
ORDER BY total_nodes DESC;

-- name: FLOW_INSERT_DEPENDENCY_EDGE
INSERT INTO file_structure_edges (
    source_id,
    target_id,
    relationship_type,
    properties_json,
    created_at
) VALUES (
    :source_id,
    :target_id,
    :relationship_type,
    :properties_json,
    CURRENT_TIMESTAMP
)
ON CONFLICT (source_id, target_id, relationship_type) DO UPDATE SET
    properties_json = EXCLUDED.properties_json;

-- name: FLOW_GET_DEPENDENCY_EDGE_BY_ENDPOINTS
SELECT
    source_id,
    target_id,
    relationship_type,
    properties_json,
    created_at
FROM file_structure_edges
WHERE source_id = :source_id
  AND target_id = :target_id
  AND relationship_type = :relationship_type;

-- name: FLOW_LIST_UPSTREAM_DEPENDENCIES_BY_TARGET_ID
SELECT
    e.source_id AS id,
    n.label,
    n.file_path,
    n.feature_name,
    e.relationship_type AS relationship,
    e.properties_json AS edge_properties
FROM file_structure_edges e
JOIN file_structure_nodes n ON e.source_id = n.id
WHERE e.target_id = :target_id
ORDER BY n.label ASC, n.id ASC;

-- name: FLOW_LIST_DOWNSTREAM_DEPENDENTS_BY_SOURCE_ID
SELECT
    e.target_id AS id,
    n.label,
    n.file_path,
    n.feature_name,
    e.relationship_type AS relationship,
    e.properties_json AS edge_properties
FROM file_structure_edges e
JOIN file_structure_nodes n ON e.target_id = n.id
WHERE e.source_id = :source_id
ORDER BY n.label ASC, n.id ASC;

-- name: FLOW_LIST_ALL_EDGES_BY_RELATIONSHIP_TYPE
SELECT
    e.source_id,
    sn.label AS source_label,
    e.target_id,
    tn.label AS target_label,
    e.relationship_type,
    e.properties_json,
    e.created_at
FROM file_structure_edges e
JOIN file_structure_nodes sn ON e.source_id = sn.id
JOIN file_structure_nodes tn ON e.target_id = tn.id
WHERE e.relationship_type = :relationship_type
ORDER BY e.source_id ASC, e.target_id ASC;

-- name: FLOW_COUNT_EDGES_BY_TYPE
SELECT
    relationship_type,
    COUNT(1) AS total_edges
FROM file_structure_edges
GROUP BY relationship_type
ORDER BY total_edges DESC;

-- name: FLOW_DELETE_FILE_NODE_BY_ID
DELETE FROM file_structure_nodes
WHERE id = :id;

-- name: FLOW_DELETE_EDGES_BY_NODE_ID
DELETE FROM file_structure_edges
WHERE source_id = :id OR target_id = :id;

-- name: FLOW_DELETE_ALL_GRAPH_RECORDS
DELETE FROM file_structure_edges;
DELETE FROM file_structure_nodes;

-- name: FLOW_FIND_ORPHAN_NODES
SELECT
    n.id,
    n.label,
    n.file_path,
    n.feature_name
FROM file_structure_nodes n
LEFT JOIN file_structure_edges es ON n.id = es.source_id
LEFT JOIN file_structure_edges et ON n.id = et.target_id
WHERE es.source_id IS NULL AND et.target_id IS NULL
ORDER BY n.feature_name ASC, n.label ASC;

-- name: FLOW_LIST_FEATURE_TOPOLOGY_SUMMARY
SELECT
    n.feature_name,
    COUNT(DISTINCT n.id) AS total_nodes,
    COUNT(DISTINCT e.source_id || '-' || e.target_id) AS total_edges
FROM file_structure_nodes n
LEFT JOIN file_structure_edges e ON n.id = e.source_id
GROUP BY n.feature_name
ORDER BY n.feature_name ASC;
