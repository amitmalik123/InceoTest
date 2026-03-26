SELECT 
    id AS model_id,
    version_metadata->>'taxManagementEligible' AS "taxManagementEligible",
    version_metadata->>'taxManagementRequired' AS "taxManagementRequired",
    version_metadata::text AS metadata_raw
FROM public.vw_model
WHERE id = '{{test_model_id}}'
LIMIT 1