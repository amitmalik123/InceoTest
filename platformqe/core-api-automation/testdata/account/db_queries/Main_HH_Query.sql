SELECT LOWER(a.Id) AS Id
FROM Account a
WHERE a.AccountClassification = 'Household'
  AND a.Version = (
    SELECT MAX(v.Version)
    FROM Account v
    WHERE v.Id = a.Id
  )
  AND EXISTS (
    SELECT 1
    FROM Account c
    WHERE c.ParentAccountId = a.Id
      AND c.AccountClassification = 'CustodyAccount'
      AND c.Version = (
        SELECT MAX(vc.Version)
        FROM Account vc
        WHERE vc.Id = c.Id
      )
      AND EXISTS (
        SELECT 1
        FROM Account s
        WHERE s.ParentAccountId = c.Id
          AND s.AccountClassification = 'Sleeve'
          AND s.Version = (
            SELECT MAX(vs.Version)
            FROM Account vs
            WHERE vs.Id = s.Id
          )
      )
  );