SELECT c.Id, c.ParentAccountId, c.AccountClassification
FROM Account c
WHERE c.ParentAccountId = {{db_HH_account_id}}
  AND c.Version = (
    SELECT MAX(v.Version)
    FROM Account v
    WHERE v.Id = c.Id
  );