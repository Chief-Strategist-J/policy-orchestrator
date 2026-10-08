// ================================================================================
// ALGORITHM & ARCHITECTURE BLUEPRINT: MESSAGING ROLE NAMED CYPHER QUERIES
// ================================================================================
// Formula: FLOW_{VERB}_{ENTITY}_{CRITERIA}
// Target Nodes: EventProducer, TopicSpec, TopicsLock, DeadLetterQueue, EventConsumer
// ================================================================================

// name: FLOW_GET_FEATURE_MESSAGING_TOPOLOGY
MATCH (s:DomainService {feature_name: $feature_name})
OPTIONAL MATCH (s)-[:EMITS_EVENT]->(p:EventProducer)-[:PUBLISHES_TO]->(t:TopicSpec)
OPTIONAL MATCH (t)-[:LOCKED_BY]->(tl:TopicsLock)
OPTIONAL MATCH (t)-[:FALLBACK_DLQ]->(dlq:DeadLetterQueue)
OPTIONAL MATCH (t)-[:DELIVERS_TO]->(c:EventConsumer)-[:TRIGGERS_DOMAIN]->(targetService:DomainService)
RETURN s.feature_name AS publisher,
       p.file_path AS producer_path,
       t.file_path AS topic_spec_path,
       tl.file_path AS topics_lock_path,
       dlq.file_path AS dlq_path,
       c.file_path AS consumer_path,
       targetService.feature_name AS subscriber;

// name: FLOW_FIND_ALL_CROSS_FEATURE_EVENT_CHOREOGRAPHIES
MATCH (pService:DomainService)-[:EMITS_EVENT]->()-[:PUBLISHES_TO]->(t:TopicSpec)-[:DELIVERS_TO]->()-[:TRIGGERS_DOMAIN]->(cService:DomainService)
RETURN pService.feature_name AS publisher_feature,
       pService.package_name AS publisher_package,
       t.id AS topic_id,
       cService.feature_name AS subscriber_feature,
       cService.package_name AS subscriber_package;
