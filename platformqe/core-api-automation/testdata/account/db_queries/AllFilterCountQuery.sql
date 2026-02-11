WITH LatestAccounts AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY Id ORDER BY Version DESC) AS rn
    FROM Account
)
SELECT COUNT(1)
FROM LatestAccounts a
CROSS APPLY OPENJSON(a.Parties)
  WITH (
    RoleType NVARCHAR(100) '$.roleType',
    PartyId UNIQUEIDENTIFIER '$.partyId'
  ) p
CROSS APPLY OPENJSON(a.Identifiers)
  WITH (
    Type NVARCHAR(100) '$.type'
  ) i
WHERE a.rn = 1
  AND a.AccountClassification = 'Account'
  AND a.AccountType = 'corporate'
  AND a.AccountSubType = 'BankorTrustCompanyTaxable'
  AND p.RoleType = 'Trustee'
  AND p.PartyId = '7e2b1c3a-4d5e-6f7a-8b9c-0d1e2f3a4b5c'
  AND i.Type = 'AccountNumber'
  -- Add changeState filter if needed