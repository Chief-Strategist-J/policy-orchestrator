// ================================================================================
// ALGORITHM & ARCHITECTURE BLUEPRINT: PACKAGE ROLE NAMED CYPHER QUERIES
// ================================================================================
// Formula: FLOW_{VERB}_{ENTITY}_{CRITERIA}
// Target Nodes: PackageRoot, DomainService (Package Isolation & Feature Registry)
// ================================================================================

// name: FLOW_GET_PACKAGE_FEATURES
MATCH (p:PackageRoot {id: $id})-[:CONTAINS_FEATURE]->(s:DomainService)
RETURN s.feature_name AS name,
       s.owner AS owner,
       s.status AS status,
       s.flags AS flags,
       s.migrations AS migrations,
       s.contract_version AS contract_version;

// name: FLOW_LIST_ALL_PACKAGES_AND_FEATURES
MATCH (p:PackageRoot)-[:CONTAINS_FEATURE]->(s:DomainService)
RETURN p.name AS package,
       count(s) AS total_features,
       collect(s.feature_name) AS features
ORDER BY package ASC;

// name: FLOW_AUDIT_CROSS_PACKAGE_ISOLATION
MATCH (p1:PackageRoot)-[:CONTAINS_FEATURE]->(s1:DomainService)
MATCH (p2:PackageRoot)-[:CONTAINS_FEATURE]->(s2:DomainService)
WHERE p1 <> p2
OPTIONAL MATCH crossPath = (s1)-[*1..2]-(s2)
RETURN p1.name AS pkg1,
       p2.name AS pkg2,
       count(crossPath) AS cross_package_leaks;
