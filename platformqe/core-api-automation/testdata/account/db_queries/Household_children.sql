SELECT a.*
FROM Account a
WHERE a.AccountClassification IN ('Household')
  AND a.Version = (
    SELECT MAX(v.Version)
    FROM Account v
    WHERE v.Id = a.Id
  )
  AND EXISTS (
    SELECT 1
    FROM Account c
    WHERE c.ParentAccountId = a.Id
      AND c.Version = (
        SELECT MAX(vc.Version)
        FROM Account vc
        WHERE vc.Id = c.Id
      )
  );