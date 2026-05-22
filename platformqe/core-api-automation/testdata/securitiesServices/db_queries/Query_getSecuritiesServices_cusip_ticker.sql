SELECT cusip as db_cusip, ticker as db_ticker FROM public."Securities" where cusip='{{request_cusip}}' AND
         ticker='{{request_ticker}}'