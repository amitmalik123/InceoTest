SELECT id,
       name,
       owner_id,
       modified_by,
       investment_min,
       solution_type,
       model_type,
       custodian,
       metadata,
       modified_date,
       risk_profile,
       CASE 
           WHEN benchmark IS NOT NULL THEN 
               (SELECT jsonb_agg(jsonb_build_object('name', elem->>'name'))
                FROM jsonb_array_elements(benchmark) AS elem)
           ELSE NULL 
       END AS benchmarks,
       CASE 
           WHEN investment_approach IS NOT NULL THEN 
               jsonb_build_object('name', investment_approach->>'name')
           ELSE NULL 
       END AS investment_approach,
       model_active_id as id,
       id as model_id,
       version,
       status,
       allocation_id,
       allocations,
       model_active_modified_by as modified_by,
       model_active_modified_date as modified_date
FROM public.vw_model where id = '{{response_model_id}}'