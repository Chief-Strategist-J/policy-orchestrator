-- ================================================================================
-- ALGORITHM & ARCHITECTURE BLUEPRINT: DOMAIN CORE ROLE NAMED SQL QUERIES
-- ================================================================================
-- Formula: FLOW_{VERB}_{ENTITY}_{CRITERIA}
-- Target Roles: DomainService, SchemaACL, DomainTypes, ContextBoundary, PublicFacade
-- ================================================================================

-- name: FLOW_GET_DOMAIN_CORE_NODES_BY_FEATURE
SELECT
    id,
    label,
    file_path,
    feature_name,
    properties_json
FROM file_structure_nodes
WHERE feature_name = :feature_name
  AND label IN ('DomainService', 'SchemaACL', 'DomainTypes', 'ContextBoundary', 'PublicFacade')
ORDER BY label ASC;

-- name: FLOW_LIST_DOMAIN_SERVICES_BY_OWNER
SELECT
    id,
    file_path,
    feature_name,
    properties_json->>'owner' AS owner,
    properties_json->>'status' AS status
FROM file_structure_nodes
WHERE label = 'DomainService'
  AND properties_json->>'owner' = :owner
ORDER BY feature_name ASC;
