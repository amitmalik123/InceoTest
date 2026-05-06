SELECT 
    securities_id,
    cusip,
    ticker,
    name,
    sub_asset_type_id
FROM public."Securities"
WHERE ticker = '{{request_ticker}}';
