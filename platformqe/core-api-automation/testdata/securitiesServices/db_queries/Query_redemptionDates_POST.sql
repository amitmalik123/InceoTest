SELECT
    fund_name AS db_fund_name,
    redemption_window_begin,
    redemption_window_end,
    fund_cik AS db_fund_cik
FROM public."IntervalFundRedemptionDates"
WHERE fund_cik = '{{request_fund_cik}}'
ORDER BY redemption_window_begin DESC;