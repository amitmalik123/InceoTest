SELECT
    a.Id AS accountId,
    party.PartyId AS partyId, *
FROM
    Account a
    CROSS APPLY OPENJSON(a.Parties)
        WITH (
            PartyId UNIQUEIDENTIFIER '$.PartyId',
            RoleType NVARCHAR(100) '$.RoleType'
        ) AS party
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
        WHERE p.RoleType = 'AccountHolder' -- Change as needed
    )