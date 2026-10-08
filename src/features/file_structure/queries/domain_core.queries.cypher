// ================================================================================
// ALGORITHM & ARCHITECTURE BLUEPRINT: DOMAIN CORE ROLE NAMED CYPHER QUERIES
// ================================================================================
// Formula: FLOW_{VERB}_{ENTITY}_{CRITERIA}
// Target Nodes: DomainService, SchemaACL, DomainTypes, ContextBoundary, PublicFacade
// ================================================================================

// name: FLOW_GET_DOMAIN_SERVICE_BY_FEATURE
MATCH (s:DomainService {feature_name: $feature_name})
RETURN s.id AS service_id,
       s.file_path AS service_path,
       s.owner AS owner,
       s.status AS status,
       s.flags AS flags,
       s.migrations AS migrations,
       s.contract_version AS contract_version,
       s.package_name AS package_name;

// name: FLOW_GET_DOMAIN_CORE_NEXUS
MATCH (s:DomainService {feature_name: $feature_name})
OPTIONAL MATCH (cb:ContextBoundary)-[:GOVERNS_BOUNDARY]->(s)
OPTIONAL MATCH (pf:PublicFacade)-[:EXPORTS_FACADE]->(s)
OPTIONAL MATCH (dt:DomainTypes)-[:TYPED_BY]->(acl:SchemaACL)
RETURN s.id AS service_id,
       s.file_path AS service_path,
       cb.file_path AS context_path,
       pf.file_path AS facade_path,
       dt.file_path AS types_path,
       acl.file_path AS schema_path;

// name: FLOW_FIND_ALL_DOMAIN_SERVICES_BY_STATUS
MATCH (s:DomainService {status: $status})
RETURN s.feature_name AS feature_name,
       s.package_name AS package_name,
       s.owner AS owner,
       s.file_path AS file_path
ORDER BY s.package_name ASC, s.feature_name ASC;
