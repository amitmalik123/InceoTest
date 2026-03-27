SELECT
    a.Id AS accountId,
    party.PartyId,
    party.RoleType,
    attr.Type,
    attr.Value,
    a.Parties
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
WHERE a.Version = (
    SELECT MAX(a2.Version)
    FROM Account a2
    WHERE a2.Id = a.Id
)
AND NOT (
     party.RoleType = 'AccountHolder'
    AND EXISTS (
        SELECT 1
        FROM OPENJSON(party.Attributes)
        WITH (
            Type NVARCHAR(100) '$.Type',
            Value NVARCHAR(100) '$.Value'
        ) AS subattr
        WHERE subattr.Type = 'IsMailingAddress'
    )
);