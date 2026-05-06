-- Sample SELECT query for hnebase
-- Usage: Verify data retrieved from API matches database
-- Joins entities, entity_permissions, and permissions tables to get permission details for a given sso_guid

SELECT 
    p.permission_key as db_permission_key, 
    ep.permission_effect as db_permission_effect
FROM public.entities e
INNER JOIN public.entity_permissions ep ON e.entity_id = ep.entity_id
INNER JOIN public.permissions p ON ep.permission_id = p.permission_id
WHERE e.sso_guid = '{{req_ssoguid}}';