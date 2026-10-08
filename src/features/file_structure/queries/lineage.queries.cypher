// ================================================================================
// ALGORITHM & ARCHITECTURE BLUEPRINT: FILE LINEAGE & IMPACT NAMED CYPHER QUERIES
// ================================================================================
// Formula: FLOW_{VERB}_{ENTITY}_{CRITERIA}
// Target Operations: Direct Upstream, Direct Downstream, Transitive Lineage, Blast Radius
// ================================================================================

// name: FLOW_GET_DIRECT_UPSTREAM_LINEAGE
MATCH (source)-[r]->(target {id: $id})
RETURN source.id AS source_id,
       labels(source)[0] AS source_label,
       source.file_path AS source_file_path,
       source.layer AS source_layer,
       type(r) AS relationship,
       target.id AS target_id;

// name: FLOW_GET_DIRECT_DOWNSTREAM_LINEAGE
MATCH (source {id: $id})-[r]->(target)
RETURN source.id AS source_id,
       type(r) AS relationship,
       target.id AS target_id,
       labels(target)[0] AS target_label,
       target.file_path AS target_file_path,
       target.layer AS target_layer;

// name: FLOW_FIND_TRANSITIVE_UPSTREAM_PATHS
MATCH path = (ancestor)-[*1..5]->(target {id: $id})
RETURN ancestor.id AS ancestor_id,
       labels(ancestor)[0] AS ancestor_label,
       ancestor.file_path AS ancestor_file_path,
       length(path) AS depth,
       [rel IN relationships(path) | type(rel)] AS relationship_chain;

// name: FLOW_FIND_TRANSITIVE_DOWNSTREAM_PATHS
MATCH path = (source {id: $id})-[*1..5]->(descendant)
RETURN descendant.id AS descendant_id,
       labels(descendant)[0] AS descendant_label,
       descendant.file_path AS descendant_file_path,
       length(path) AS depth,
       [rel IN relationships(path) | type(rel)] AS relationship_chain;
