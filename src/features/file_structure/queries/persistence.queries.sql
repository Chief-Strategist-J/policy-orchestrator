-- ================================================================================
-- ALGORITHM & ARCHITECTURE BLUEPRINT: PERSISTENCE ROLE NAMED SQL QUERIES
-- ================================================================================
-- Formula: FLOW_{VERB}_{ENTITY}_{CRITERIA}
-- Target Roles: RepositoryPort, RepositoryAdapter, NamedQuery, DatabaseMigration
-- ================================================================================

-- name: FLOW_GET_PERSISTENCE_NODES_BY_FEATURE
SELECT
    id,
    label,
    file_path,
    feature_name,
    properties_json
FROM file_structure_nodes
WHERE feature_name = :feature_name
  AND label IN ('RepositoryPort', 'RepositoryAdapter', 'NamedQuery', 'DatabaseMigration')
ORDER BY label ASC;
