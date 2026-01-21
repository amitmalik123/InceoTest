-- Validate POST/INSERT operation for account
-- Usage: Verify new record was created in database

SELECT 
    id,
    name,
    created_date,
    created_by
FROM account_table
WHERE name = '{{created_name}}'
    AND created_by = '{{user_id}}'
ORDER BY created_date DESC
LIMIT 1;
