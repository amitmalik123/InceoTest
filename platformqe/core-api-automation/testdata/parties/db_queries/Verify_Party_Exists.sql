-- Verification query: returns 1 row only if the party exists.
-- Used by CleanupManager BEFORE running DELETE to confirm the record is real
-- and (optionally) was created by the expected user (CreatedBy column).
SELECT "Id", "CreatedBy", "CreatedDate", "IsDeleted"
FROM "Party"
WHERE "Id" = ?;
