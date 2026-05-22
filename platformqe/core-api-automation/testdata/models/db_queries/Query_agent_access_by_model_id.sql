
SELECT
    aa.agent_access_id                                           AS "agent_access_id",
    aa.agent_id                                                  AS "agent_id",
    aa.model_id                                                  AS "model_id",
    aa.model_version                                             AS "model_version"
FROM agent_access aa
WHERE aa.model_id = '{{tx_created_model_id}}'::uuid
ORDER BY aa.agent_access_id;
