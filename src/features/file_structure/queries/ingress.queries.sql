-- ================================================================================
-- ALGORITHM & ARCHITECTURE BLUEPRINT: INGRESS DELIVERY ROLE NAMED SQL QUERIES
-- ================================================================================
-- Formula: FLOW_{VERB}_{ENTITY}_{CRITERIA}
-- Target Roles: IngressRouter, IngressHandler, RouteRules
-- ================================================================================

-- name: FLOW_GET_INGRESS_ENDPOINTS_BY_FEATURE
SELECT
    id,
    label,
    file_path,
    feature_name,
    properties_json
FROM file_structure_nodes
WHERE feature_name = :feature_name
  AND label IN ('IngressRouter', 'IngressHandler', 'RouteRules')
ORDER BY label ASC;

-- name: FLOW_LIST_INGRESS_ENDPOINTS_BY_PACKAGE
SELECT
    id,
    label,
    file_path,
    feature_name,
    properties_json
FROM file_structure_nodes
WHERE properties_json->>'package_name' = :package_name
  AND label IN ('IngressRouter', 'IngressHandler', 'RouteRules')
ORDER BY feature_name ASC, label ASC;
