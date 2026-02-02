SELECT id AS model_id,
       name,
       owner_id,
       modified_by,
       investment_min,
       solution_type,
       model_type,
       custodian,
       metadata,
       to_char(
            date_trunc('milliseconds', modified_date AT TIME ZONE 'UTC'),
            'YYYY-MM-DD"T"HH24:MI:SS.FF4"Z"'
        ) AS modified_date,
       risk_profile,
       -- Filter benchmark JSON to only include 'id' and 'name' fields, with camelCase keys
       COALESCE(
           (
               SELECT jsonb_agg(
                   jsonb_build_object(
                       'id', (elem->>'id')::int,
                       'name', elem->>'name'
                   )
                   ORDER BY (elem->>'id')::int
               )
               FROM jsonb_array_elements(benchmark::jsonb) AS elem
           ),
           '[]'::jsonb
       ) AS benchmark,
       investment_approach,
       version,
       status,
       allocation_id AS allocationId,
       -- Rebuild allocations JSON with camelCase keys, return [] if null
       COALESCE(
           (
               SELECT jsonb_agg(
                   jsonb_build_object(
                       'cusip', alloc->>'Cusip',
                       'ticker', alloc->>'Ticker',
                       'weight', (alloc->>'Weight')::numeric,
                       'modelId', alloc->>'ModelId',
                       'entityType', alloc->>'EntityType',
                       'allocationName', alloc->>'AllocationName',
                       'allocations', (
                           SELECT COALESCE(
                               jsonb_agg(
                                   jsonb_build_object(
                                       'name', child->>'name',
                                       'weight', (child->>'weight')::numeric,
                                       'assetType', child->>'assetType',
                                       'assetClass', child->>'assetClass',
                                       'entityType', child->>'entityType',
                                       'assetSubClass', child->>'assetSubClass'
                                   )
                               ),
                               '[]'::jsonb
                           )
                           FROM jsonb_array_elements(alloc->'Allocations') AS child
                       )
                   )
               )
               FROM jsonb_array_elements(allocations::jsonb) AS alloc
           ),
           '[]'::jsonb
       ) AS allocations,
       model_active_modified_by,
       to_char(
            date_trunc('milliseconds', model_active_modified_date AT TIME ZONE 'UTC'),
            'YYYY-MM-DD"T"HH24:MI:SS.FF5"Z"'
        ) AS model_active_modified_date
FROM public.vw_model
WHERE status = 'Draft';
