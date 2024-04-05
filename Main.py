# def Backtest(exchange: pd.DataFrame, portfolio: Portfolio, endDate: str = datetime.now().strftime('%Y-%m-%d')) -> None:
#     # loop through exchange
#     for row in exchange.iterrows():
#         stockTicker = row[1][0]
#         print(stockTicker)
#         # Ticker object
#         stockObject = yf.Ticker(stockTicker)
#
#         # Date format is strict
#         stockHist = stockObject.history(start='2000-01-01', end=endDate)["Close"]
#
#         if not ValidateHistoryData(stockHist, endDate):
#             continue
#         curPrice = stockHist.iloc[-1]
#
#         # Deploy strategy
#         if stockTicker in portfolio.holdings.keys():
#             if MomentumBasedStrategy(stockObject, endDate, "sell"):
#                 if stockTicker in portfolio.holdings.keys():
#                     print(f"Selling {stockTicker}")
#                     portfolio.funds = portfolio.funds + curPrice * portfolio.holdings[stockTicker][1]
#                     del portfolio.holdings[stockTicker]
#                 else:
#                     # Todo: errorhandling
#                     raise Exception
#         else:
#             if MomentumBasedStrategy(stockObject, endDate, "buy"):
#                 # Todo: keep statistics on the amount of stocks passing the momentum criteria
#                 portfolio.pool.loc[len(portfolio.pool.index)] = [stockTicker, curPrice, 0]
#
#     # If the pool is not empty we process and buy
#     if portfolio.pool.shape[0] > 0:
#         portfolio.PreparePool()
#         for row in portfolio.pool.iterrows():
#             series = row[1]
#             curPrice = series["Price"]
#             name = series["Name"]
#             numUnits = series["UnitsToBuy"]
#
#             if portfolio.funds >= curPrice:
#                 portfolio.funds = portfolio.funds - curPrice * numUnits
#                 portfolio.holdings[name] = (curPrice, numUnits)
#                 print(f"Bought {name}")
#             else:
#                 pass
#                 # Todo: errorhandling
#                 # raise Exception
#     else:
#         print("No stocks found")
#
#     # Log results
#     LogDeploymentResults(portfolio.GetPortfolioWorth() + portfolio.funds, endDate)
# def ValidateHistoryData(stockHist: yf.ticker.Ticker.history, endDate: str) -> bool:
#     # Check if empty
#     if stockHist.empty:
#         return False
#     # Check if last observations i more than a week old
#     elif stockHist.last_valid_index().strftime('%Y-%m-%d') < (
#             datetime.strptime(endDate, '%Y-%m-%d').date() - timedelta(weeks=1)).strftime('%Y-%m-%d'):
#         return False
#     else:
#         return True

# def MomentumBasedStrategy(stock: yf.ticker.Ticker, endDate: str, flag: str) -> bool:
#     stockHistOpen = stock.history(start='2000-01-01', end=endDate)["Open"]
#     stockHistClose = stock.history(start='2000-01-01', end=endDate)["Close"]
#     # Filter1: Yesterday close must be lower than today's open
#     filter1 = stockHistClose.iloc[-2] < stockHistOpen.iloc[-1]
#
#     # Filter2: short term moving average must be larger than long term moving average
#     filter2 = stat.mean(stockHistClose.iloc[-20:]) < stat.mean(stockHistClose.iloc[-10:])
#
#     # Filter3: stocks with RSI>70 is considered over-saturated. Rsi is not applied to sell condition
#     # Cast to df for one-liner
#     df = pd.DataFrame(stockHistClose, columns=["Close"])
#     # look-back period
#     n = 14
#     rsi = 100 - (100 / (
#             1 + df['Close'].diff(1).mask(df['Close'].diff(1) < 0, 0).ewm(alpha=1 / n, adjust=False).mean() /
#             df['Close'].diff(1).mask(df['Close'].diff(1) > 0, -0.0).abs().ewm(alpha=1 / n, adjust=False).mean()))[-1]
#
#     filter3 = rsi < 70
#
#     if flag.lower() == "buy":
#         return filter1 and filter2 and filter3
#     elif flag.lower() == "sell":
#         return not filter1 and not filter2
#     else:
#         raise Exception
