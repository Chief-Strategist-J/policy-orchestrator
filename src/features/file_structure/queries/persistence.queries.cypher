// ================================================================================
// ALGORITHM & ARCHITECTURE BLUEPRINT: PERSISTENCE ROLE NAMED CYPHER QUERIES
// ================================================================================
// Formula: FLOW_{VERB}_{ENTITY}_{CRITERIA}
// Target Nodes: RepositoryPort, RepositoryAdapter, NamedQuery, DatabaseMigration, SchemaLock, DatabasePool
// ================================================================================

// name: FLOW_GET_PERSISTENCE_CHAIN_BY_FEATURE
MATCH (s:DomainService {feature_name: $feature_name})
OPTIONAL MATCH (s)-[:CONSUMES_PORT]->(p:RepositoryPort)-[:IMPLEMENTED_BY]->(a:RepositoryAdapter)
OPTIONAL MATCH (a)-[:EXECUTES_QUERY]->(q:NamedQuery)-[:DEPENDS_ON_DDL]->(m:DatabaseMigration)
OPTIONAL MATCH (m)-[:LOCKED_BY]->(sl:SchemaLock)
RETURN s.feature_name AS feature,
       p.file_path AS port_path,
       a.file_path AS adapter_path,
       q.file_path AS query_path,
       m.file_path AS migration_path,
       sl.file_path AS schema_lock_path;

// name: FLOW_LIST_ALL_MIGRATIONS_BY_PACKAGE
MATCH (p:PackageRoot {name: $package_name})-[:CONTAINS_FEATURE]->(s:DomainService)
MATCH (s)-[:CONSUMES_PORT]->()-[:IMPLEMENTED_BY]->()-[:EXECUTES_QUERY]->()-[:DEPENDS_ON_DDL]->(m:DatabaseMigration)
RETURN s.feature_name AS feature,
       m.id AS migration_id,
       m.file_path AS migration_path
ORDER BY migration_id ASC;
