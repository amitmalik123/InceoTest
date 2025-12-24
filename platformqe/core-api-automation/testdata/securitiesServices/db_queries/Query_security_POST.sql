SELECT
    securities_id,
    cusip,
    ticker,
    name 
FROM public."Securities" where cusip='{{payload_unique_cusip}}'