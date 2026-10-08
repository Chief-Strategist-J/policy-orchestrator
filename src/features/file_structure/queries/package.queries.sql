-- ================================================================================
-- ALGORITHM & ARCHITECTURE BLUEPRINT: PACKAGE ROLE NAMED SQL QUERIES
-- ================================================================================
-- Formula: FLOW_{VERB}_{ENTITY}_{CRITERIA}
-- Target Roles: PackageRoot, DomainService
-- ================================================================================

-- name: FLOW_GET_PACKAGE_SUMMARY
SELECT
    properties_json->>'package_name' AS package_name,
    COUNT(id) AS total_features
FROM file_structure_nodes
WHERE label = 'DomainService'
  AND properties_json->>'package_name' = :package_name
GROUP BY properties_json->>'package_name';

-- name: FLOW_LIST_ALL_PACKAGES
SELECT DISTINCT
    properties_json->>'package_name' AS package_name
FROM file_structure_nodes
WHERE properties_json->>'package_name' IS NOT NULL
ORDER BY package_name ASC;
