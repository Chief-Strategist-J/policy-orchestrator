-- ================================================================================
-- ALGORITHM & ARCHITECTURE BLUEPRINT: MESSAGING ROLE NAMED SQL QUERIES
-- ================================================================================
-- Formula: FLOW_{VERB}_{ENTITY}_{CRITERIA}
-- Target Roles: EventProducer, TopicSpec, DeadLetterQueue, EventConsumer
-- ================================================================================

-- name: FLOW_GET_MESSAGING_NODES_BY_FEATURE
SELECT
    id,
    label,
    file_path,
    feature_name,
    properties_json
FROM file_structure_nodes
WHERE feature_name = :feature_name
  AND label IN ('EventProducer', 'TopicSpec', 'TopicsLock', 'DeadLetterQueue', 'EventConsumer')
ORDER BY label ASC;
