SELECT
    a.Id AS Id,
    party.PartyId AS partyId, 
    party.RoleType AS RoleType,
    attr.Type AS AttributeType
FROM
    Account a
    CROSS APPLY OPENJSON(a.Parties)
        WITH (
            PartyId UNIQUEIDENTIFIER '$.PartyId',
            RoleType NVARCHAR(100) '$.RoleType',
            Attributes NVARCHAR(MAX) AS JSON
        ) AS party
    OUTER APPLY OPENJSON(party.Attributes)
        WITH (
            Type NVARCHAR(100) '$.Type'
        ) AS attr
WHERE
    a.Version = (
        SELECT MAX(a2.Version)
        FROM Account a2
        WHERE a2.Id = a.Id
    )
    AND NOT EXISTS (
        SELECT 1
        FROM OPENJSON(a.Parties)
            WITH (
                RoleType NVARCHAR(100) '$.RoleType'
            ) AS p
        WHERE p.RoleType = 'AccountHolder'
    )