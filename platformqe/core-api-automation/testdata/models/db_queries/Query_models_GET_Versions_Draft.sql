-- Query to validate versions for Draft models only
SELECT
    id AS "model_id",
    jsonb_agg(
        jsonb_build_object(
            'version', version,
            'status', status,
            'allocations',
            CASE
                WHEN allocations IS NULL
                     OR jsonb_array_length(allocations) = 0
                THEN '[]'::jsonb
                ELSE (
                    SELECT jsonb_agg(
                        jsonb_build_object(
                            'allocations', '[]'::jsonb,
                            'entityType', alloc->>'EntityType',
                            'allocationName', alloc->>'AllocationName',
                            'modelId', alloc->>'ModelId',
                            'cusip', alloc->>'Cusip',
                            'ticker', alloc->>'Ticker',
                            'weight', (alloc->>'Weight')::numeric
                        )
                    )
                    FROM jsonb_array_elements(allocations) AS alloc
                )
            END,
            'publishedDate',
            CASE
                WHEN status = 'Published'
                THEN to_char(
                    date_trunc('second', model_active_modified_date AT TIME ZONE 'UTC'),
                    'YYYY-MM-DD"T"HH24:MI:SS.FFFFFF"Z"'
                )
                ELSE NULL
            END,
            'modifiedDate', to_char(
                date_trunc('second', model_active_modified_date AT TIME ZONE 'UTC'),
                'YYYY-MM-DD"T"HH24:MI:SS.FFFFFF"Z"'
            ),
            'modifiedBy', model_active_modified_by,
            'createdBy', model_active_created_by
        )
        ORDER BY version
    ) AS versions
FROM public.vw_model m
WHERE status = 'Draft'
GROUP BY id
ORDER BY id;
