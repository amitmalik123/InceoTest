-- Sample SELECT query for hnebase
-- Usage: Verify data retrieved from API matches database

SELECT 
    permission_key as db_permission_key, permission_effect as db_permission_effect
FROM public.user_effective_permissions
WHERE sso_guid = '{{req_ssoguid}}';