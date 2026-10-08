// ================================================================================
// ALGORITHM & ARCHITECTURE BLUEPRINT: BEHAVIORAL ROLE NAMED CYPHER QUERIES
// ================================================================================
// Formula: FLOW_{VERB}_{ENTITY}_{CRITERIA}
// Target Nodes: RuleSet, StateMachine, WorkflowEngine
// ================================================================================

// name: FLOW_GET_BEHAVIORAL_ENGINES_BY_FEATURE
MATCH (s:DomainService {feature_name: $feature_name})
OPTIONAL MATCH (s)-[:ENFORCES_RULES]->(r:RuleSet)
OPTIONAL MATCH (s)-[:TRANSITIONS_STATE]->(m:StateMachine)
OPTIONAL MATCH (s)-[:RUNS_WORKFLOW]->(w:WorkflowEngine)
RETURN s.feature_name AS feature,
       r.id AS rules_id,
       r.file_path AS rules_path,
       m.id AS machine_id,
       m.file_path AS machine_path,
       w.id AS workflow_id,
       w.file_path AS workflow_path;

// name: FLOW_LIST_ALL_WORKFLOW_ENGINES
MATCH (w:WorkflowEngine)<-[:RUNS_WORKFLOW]-(s:DomainService)
RETURN s.feature_name AS feature,
       s.package_name AS package,
       w.id AS workflow_id,
       w.file_path AS workflow_path
ORDER BY s.package_name ASC, s.feature_name ASC;
