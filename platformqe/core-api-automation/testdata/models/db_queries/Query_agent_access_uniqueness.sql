
SELECT
    aa.agent_id                                                  AS "agent_id",
    aa.model_id                                                  AS "model_id",
    aa.model_version                                             AS "model_version",
    COUNT(*)                                                     AS "row_count"
FROM agent_access aa
GROUP BY aa.agent_id, aa.model_id, aa.model_version
HAVING COUNT(*) > 1
ORDER BY aa.model_id;
