import yfinance as yf
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

import requests
import json

def DumpPortfolio(portfolio: dict) -> None:
    #Todo: explicit path
    with open("C:/Users/Vahlg/PycharmProjects/TradingBot/portfolio.p", "wb") as f:
        pickle.dump(portfolio,f)
        f.close()
def LoadPortfolio() -> dict:
    with  open("C:/Users/Vahlg/PycharmProjects/TradingBot/portfolio.p", "rb") as f:
        portfolio = pickle.load(f)
        f.close()
    return portfolio
def ResetPortfolio(val: dict = {}) -> None:
    DumpPortfolio({})
def DumpCashstack(cashstack: float) -> None:
    # explicit path
    with open("C:/Users/Vahlg/PycharmProjects/TradingBot/cashstack.p", "wb") as f:
        pickle.dump(cashstack,f)
        f.close()
def LoadCashstack() -> float:
    with  open("C:/Users/Vahlg/PycharmProjects/TradingBot/cashstack.p", "rb") as f:
        cashstack = pickle.load(f)
        f.close()
    return float(cashstack)
def ResetCashstack(val: float = 10000) -> None:
    DumpCashstack(float(val))
def BuyStock(portfolio: dict, cashstack: float, stock: yf.ticker.Ticker) -> None:
    curPrice = stock.history()['Close'].iloc[-1]
    if stock[1]["Name"] not in portfolio.keys() and cashstack>curPrice:
        cashstack = cashstack - curPrice
    else:
        #Todo: errorhandling
        raise Exception

def get_stock_price(symbol):
    """get a stock price from yahoo finance"""

    url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=" + symbol
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)

    return data['quoteResponse']['result'][0]['regularMarketPrice']

def Main():
    #Todo: download sp500 ticker list every monday? and overwrite in disk
    exchange = pd.read_csv("tickersymbols.csv", nrows=400)#["Name"]  # 411 stocks

    ResetCashstack()
    ResetPortfolio()

    cashstack = LoadCashstack()
    portfolio = LoadPortfolio()



    #check næste gang
    #print(get_stock_price('AAPL'))


    #loop through
    for row in exchange.iterrows():
        stockTicker = row[1]["Name"]
        # GET TODAYS DATE AND CONVERT IT TO A STRING WITH YYYY-MM-DD FORMAT (YFINANCE EXPECTS THAT FORMAT)
        end_date = datetime.now().strftime('%Y-%m-%d')
        stock = yf.Ticker(stockTicker)
        stockHist = stock.history(start='2022-01-01', end=end_date)["Close"]
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

if(__name__ ==  "__main__"):
    Main()