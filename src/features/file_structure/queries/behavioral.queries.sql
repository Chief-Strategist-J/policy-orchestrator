-- ================================================================================
-- ALGORITHM & ARCHITECTURE BLUEPRINT: BEHAVIORAL ROLE NAMED SQL QUERIES
-- ================================================================================
-- Formula: FLOW_{VERB}_{ENTITY}_{CRITERIA}
-- Target Roles: RuleSet, StateMachine, WorkflowEngine
-- ================================================================================

-- name: FLOW_GET_BEHAVIORAL_NODES_BY_FEATURE
SELECT
    id,
    label,
    file_path,
    feature_name,
    properties_json
FROM file_structure_nodes
WHERE feature_name = :feature_name
  AND label IN ('RuleSet', 'StateMachine', 'WorkflowEngine')
ORDER BY label ASC;
