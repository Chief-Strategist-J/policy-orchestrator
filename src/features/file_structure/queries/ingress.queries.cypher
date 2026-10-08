// ================================================================================
// ALGORITHM & ARCHITECTURE BLUEPRINT: INGRESS DELIVERY ROLE NAMED CYPHER QUERIES
// ================================================================================
// Formula: FLOW_{VERB}_{ENTITY}_{CRITERIA}
// Target Nodes: IngressRouter, IngressHandler, RouteRules, GraphQLResolver, GRPCHandler, EventConsumer
// ================================================================================

// name: FLOW_GET_INGRESS_ROUTER_BY_FEATURE
MATCH (r:IngressRouter {feature_name: $feature_name})
OPTIONAL MATCH (r)-[:DELEGATES_TO]->(h:IngressHandler)
OPTIONAL MATCH (r)-[:EVALUATES_ROUTE_RULES]->(rules:RouteRules)
RETURN r.id AS router_id,
       r.file_path AS router_path,
       h.id AS handler_id,
       h.file_path AS handler_path,
       rules.id AS route_rules_id,
       rules.file_path AS route_rules_path;

// name: FLOW_GET_INGRESS_DELIVERY_PIPELINE
MATCH (c:Contract)-[:DEFINES_ROUTE]->(r:IngressRouter)-[:DELEGATES_TO]->(h:IngressHandler)-[:INVOKES_DOMAIN]->(s:DomainService)
WHERE s.feature_name = $feature_name
RETURN c.file_path AS contract_path,
       r.file_path AS router_path,
       h.file_path AS handler_path,
       s.file_path AS service_path;

// name: FLOW_LIST_ALL_INGRESS_ENDPOINTS_BY_PACKAGE
MATCH (p:PackageRoot {name: $package_name})-[:CONTAINS_FEATURE]->(s:DomainService)<-[:INVOKES_DOMAIN]-(h:IngressHandler)<-[:DELEGATES_TO]-(r:IngressRouter)
RETURN s.feature_name AS feature,
       r.id AS router_id,
       r.file_path AS router_path,
       h.id AS handler_id,
       h.file_path AS handler_path
ORDER BY feature ASC;
