import yfinance as yf
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def DumpPortfolio(portfolio: dict):
    #

    with open("C:/Users/Vahlg/PycharmProjects/TradingBot/portfolio.p", "wb") as f:
        pickle.dump(portfolio,f)
        f.close()
def LoadPortfolio() -> dict:
    with  open("C:/Users/Vahlg/PycharmProjects/TradingBot/portfolio.p", "rb") as f:
        portfolio = pickle.load(f)
        f.close()
    return portfolio
def ResetPortfolio():
    DumpPortfolioToFile({})

def DumpCashstack(portfolio: dict):
    # explicit path
    with open("C:/Users/Vahlg/PycharmProjects/TradingBot/portfolio.p", "wb") as f:
        pickle.dump(portfolio,f)
        f.close()
def LoadCashstack() -> dict:
    with  open("C:/Users/Vahlg/PycharmProjects/TradingBot/portfolio.p", "rb") as f:
        portfolio = pickle.load(f)
        f.close()
    return portfolio
def ResetCashstack():
    DumpCashstack({})

# download sp500 ticker list every monday? and overwrite in disk
exchange = pd.read_csv("tickersymbols.csv",nrows=400)["Name"] # 411 stocks

stock = yf.Ticker("AMZN")

# GET TODAYS DATE AND CONVERT IT TO A STRING WITH YYYY-MM-DD FORMAT (YFINANCE EXPECTS THAT FORMAT)
end_date = datetime.now().strftime('%Y-%m-%d')
stockHist = stock.history(start='2022-01-01',end=end_date)["Close"]
print("")


#momentum strat:
#When the close crosses above the 25-day high of the close, we go long at the close.
#When the close crosses below the 25-day high of the close, we sell at the close.

#When the close crosses above the 100-day high of the close, we go long at the close.
#When the close crosses below the lowest close in the last 100 days, we sell at the close.

#It’s based on monthly quotes in the ETFs SPY, TLT, EFA, and EEM.
#We rank all four ETFs every month based on last month’s performance/momentum.
#We go long the ONE ETF with the best performance the prior month (it doesn’t matter if negative or positive return).
#Hold for one month and rinse and repeat (or continue being long the same instrument)