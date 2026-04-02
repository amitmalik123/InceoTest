WITH ExcludedIds AS (
    SELECT a.Id
    FROM Account a
    WHERE a.Version = (
        SELECT MAX(a2.Version)
        FROM Account a2
        WHERE a2.Id = a.Id
    )
    AND NOT EXISTS (
        SELECT 1
        FROM OPENJSON(a.Parties)
            WITH (
                PartyId UNIQUEIDENTIFIER '$.PartyId',
                RoleType NVARCHAR(100) '$.RoleType',
                Attributes NVARCHAR(MAX) AS JSON
            ) AS party
        OUTER APPLY OPENJSON(party.Attributes)
            WITH (
                Type NVARCHAR(100) '$.Type',
                Value NVARCHAR(100) '$.Value'
            ) AS attr
        WHERE
            party.PartyId = '3FA85F64-5717-4562-B3FC-2C963F66AFA6'
            AND party.RoleType = 'AccountHolder'
            AND attr.Type = 'IsMailingAddress'
            AND attr.Value = 'string'
    )
)
SELECT
    a.Id,
    party.PartyId,
    party.RoleType,
    attr.Type,
    attr.Value
FROM Account a
CROSS APPLY OPENJSON(a.Parties)
    WITH (
        PartyId UNIQUEIDENTIFIER '$.PartyId',
        RoleType NVARCHAR(100) '$.RoleType',
        Attributes NVARCHAR(MAX) AS JSON
    ) AS party
OUTER APPLY OPENJSON(party.Attributes)
    WITH (
        Type NVARCHAR(100) '$.Type',
        Value NVARCHAR(100) '$.Value'
    ) AS attr
WHERE a.Id IN (SELECT Id FROM ExcludedIds)
AND a.Version = (
    SELECT MAX(a2.Version)
    FROM Account a2
    WHERE a2.Id = a.Id
)
AND party.PartyId IS NOT NULL
AND party.RoleType IS NOT NULL
AND attr.Type IS NOT NULL
AND attr.Value IS NOT NULL