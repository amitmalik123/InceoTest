DELETE FROM public."Securities"
WHERE cusip = '{{payload_unique_cusip}}'
LIMIT 1;
