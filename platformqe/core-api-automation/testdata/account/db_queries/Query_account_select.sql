-- Sample SELECT query for account
-- Usage: Verify data retrieved from API matches database

SELECT 
    id,
    name,
    description,
    status,
    created_date,
    updated_date
FROM account_table
WHERE id = '{{resource_id}}'
    AND status = '{{expected_status}}'
ORDER BY created_date DESC;
