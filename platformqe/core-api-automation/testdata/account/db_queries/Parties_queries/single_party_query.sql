SELECT
  a.Id,
  p0.PartyId AS PartyId_0,
  p0.RoleType AS RoleType_0,
  p1.PartyId AS PartyId_1,
  p1.RoleType AS RoleType_1,
  p2.PartyId AS PartyId_2,
  p2.RoleType AS RoleType_2
FROM Account a
OUTER APPLY (
    SELECT PartyId, RoleType
    FROM (
        SELECT [value] AS json_value, [key]
        FROM OPENJSON(a.Parties)
    ) j
    CROSS APPLY OPENJSON(j.json_value)
    WITH (
        PartyId NVARCHAR(100),
        RoleType NVARCHAR(100)
    )
    WHERE j.[key] = 0
) AS p0
OUTER APPLY (
    SELECT PartyId, RoleType
    FROM (
        SELECT [value] AS json_value, [key]
        FROM OPENJSON(a.Parties)
    ) j
    CROSS APPLY OPENJSON(j.json_value)
    WITH (
        PartyId NVARCHAR(100),
        RoleType NVARCHAR(100)
    )
    WHERE j.[key] = 1
) AS p1
OUTER APPLY (
    SELECT PartyId, RoleType
    FROM (
        SELECT [value] AS json_value, [key]
        FROM OPENJSON(a.Parties)
    ) j
    CROSS APPLY OPENJSON(j.json_value)
    WITH (
        PartyId NVARCHAR(100),
        RoleType NVARCHAR(100)
    )
    WHERE j.[key] = 2
) AS p2
WHERE a.Version = (
    SELECT MAX(av.Version)
    FROM Account av
    WHERE av.Id = a.Id
)
AND (
    SELECT COUNT(*)
    FROM OPENJSON(a.Parties)
) = 3



