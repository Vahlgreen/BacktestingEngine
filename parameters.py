# Macrotrend or alphavantage or custom
data_provider = "custom"
# strategies. Choose one or more from strategy.py
strategies = ["SimpleMomentum", "StrategyAAPL"]
# All or half or specific tickers
ticker_list = ["all"]
# First observation is 2001-01-03. Exception is thrown if date is not a valid trade day
# Start date should be no less than 2001-02-01. This way look-back statistics will have sufficient data available
start_date = "2015-02-02"
# Initial funds.
initial_funds = 10000
# Transaction fee.
transaction_fee = 0.5



######################### CODE ASSUMPTIONS ######################
# 1. Code assumes all tickers have entries for all trade days between 2001-01-03 and 2024-03-27
# 2. Ticker data can be NaN if and only if the ticker is not currently listed. That is, no NaNs appear withing the time
#    duration in which the stock is listed. Only before and after.
# 3. All tickers must have following columns: 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Ticker'
# 4. All price observations are measured in the same currency
# 5. Currently, positions on a ticker that gets delisted will be sold at entry price
# 6. Indicator functions should always return a boolean value
# 7. For now, the portfolio distributes funds equally between all strategies