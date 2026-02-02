SELECT 
    id AS "model_id",
    name,
    model_type,
    solution_type,
    custodian,
    investment_approach,
    COALESCE(
        (SELECT jsonb_agg(
            jsonb_build_object(
                'id', (elem->>'id')::int,
                'name', elem->>'name'
            ) ORDER BY (elem->>'id')::int
        )
        FROM jsonb_array_elements(
            CASE 
                WHEN jsonb_typeof(benchmark::jsonb) = 'array' 
                THEN benchmark::jsonb 
                ELSE '[]'::jsonb 
            END
        ) AS elem),
        '[]'::jsonb
    ) AS benchmark,
    investment_min,
    risk_profile,
    jsonb_build_object('ownerId', owner_id) AS owner,
    metadata,
    jsonb_agg(
        jsonb_build_object(
            'version', version,
            'status', status,
            'allocations', CASE 
                WHEN allocations IS NULL OR jsonb_array_length(allocations) = 0 
                THEN '[]'::jsonb
                ELSE (
                    SELECT jsonb_agg(
                        jsonb_build_object(
                            'cusip', alloc->>'Cusip',
                            'ticker', alloc->>'Ticker',
                            'weight', (alloc->>'Weight')::numeric,
                            'modelId', alloc->>'ModelId',
                            'entityType', alloc->>'EntityType',
                            'allocationName', alloc->>'AllocationName',
                            'allocations', '[]'::jsonb
                        )
                    )
                    FROM jsonb_array_elements(allocations) AS alloc
                )
            END,
            'publishedDate', CASE 
                WHEN status = 'Published' 
                THEN to_char(date_trunc('second', model_active_modified_date AT TIME ZONE 'UTC'), 'YYYY-MM-DD"T"HH24:MI:SS')
                ELSE NULL 
            END,
            'modifiedDate', to_char(date_trunc('second', model_active_modified_date AT TIME ZONE 'UTC'), 'YYYY-MM-DD"T"HH24:MI:SS'),
            'modifiedBy', model_active_modified_by,
            'createdBy', model_active_created_by
        ) ORDER BY version
    ) AS versions,
    to_char(date_trunc('second', modified_date AT TIME ZONE 'UTC'), 'YYYY-MM-DD"T"HH24:MI:SS') AS modifiedDate,
    modified_by as modifiedBy,
    created_by as createdBy
FROM public.vw_model m
WHERE status = 'Draft'
GROUP BY 
    id, name, model_type, solution_type, custodian, 
    investment_approach, benchmark, investment_min, risk_profile, 
    owner_id, metadata, modified_date, modified_by, created_by
