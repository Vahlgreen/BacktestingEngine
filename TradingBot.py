import yfinance as yf
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time
class PortfolioObject:
    def __init__(self, curPrice: float, units: int,transactionDate: str):
        self.curPrice = curPrice
        self.units = units
        self.transactionDate = transactionDate

    def GetTotalValue(self):
        return self.curPrice*self.units

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
def DumpFunds(funds: float) -> None:
    #TODO:explicit path
    with open("C:/Users/Vahlg/PycharmProjects/TradingBot/funds.p", "wb") as f:
        pickle.dump(funds,f)
        f.close()
def LoadFunds() -> float:
    # TODO:explicit path
    with  open("C:/Users/Vahlg/PycharmProjects/TradingBot/funds.p", "rb") as f:
        funds = pickle.load(f)
        f.close()
    return float(funds)
def ResetFunds(val: float = 10000) -> None:
    DumpFunds(float(val))
def BuyStock(portfolio: dict, funds: float, stockTicker: str, curPrice: float) -> None:
    if funds >= curPrice:
        funds = funds - curPrice
        portfolioObject = PortfolioObject(curPrice,1,datetime.now().strftime('%Y-%m-%d'))
        portfolio[stockTicker] = portfolioObject
        print(f"Bought {stockTicker}")
    else:
        pass
        #Todo: errorhandling
        #raise Exception
def SellStock(portfolio: dict, funds: float, stockTicker: str, curPrice: float):
    if stockTicker in portfolio.keys():
        funds = funds+curPrice
        del portfolio[stockTicker]
    else:
        #Todo: errorhandling
        raise Exception
def BackTestStrategy() -> None:
    quit()
def MomentumBasedStrategy(stockHist: yf.ticker.Ticker.history,flag: str) -> bool:
    # When the close crosses above the 25-day high of the close, we go long at the close.
    # When the close crosses below the 25-day high of the close, we sell at the close.
    period = 25
    curMax = 0
    if flag == "buy":
        #For some reason list[-x:-1] does not contain the last element of the list. However, list[-1] returns exactly that
        for obs in stockHist.iloc[-period+1:-1]:
            curMax = max(curMax, obs)
        return curMax > stockHist.iloc[-1]
    elif flag == "sell":
        for obs in stockHist.iloc[-period+1:-1]:
            curMax = max(curMax, obs)
        return curMax < stockHist.iloc[-1]
    else:
        raise Exception
def SummarizeRun(portfolio: dict):
    totValue = 0
    numStocks = len(portfolio.items())
    for key in portfolio.keys():
        totValue = totValue + portfolio[key].GetTotalValue()

    print(f"Portfolio consists of {numStocks} stocks\nTotal portfolio value: {totValue}")

def Main():
    #Todo: download sp500 ticker list every ?monday? and overwrite in disk
    exchange = pd.read_csv("tickersymbols.csv", nrows=500)  #sp500

    ResetFunds()
    ResetPortfolio()

    funds = LoadFunds()
    portfolio = LoadPortfolio()

    #loop through exchange
    for row in exchange.iterrows():
        stockTicker = row[1][0]

        #Ticker object
        stockObject = yf.Ticker(stockTicker)

        # Format is strict
        endDate = datetime.now().strftime('%Y-%m-%d')
        #APD
        stockHist = stockObject.history(start='2000-01-01', end=endDate)["Close"]

        if stockHist.empty:
            continue
        curPrice = stockHist.iloc[-1]

        #Evaluate strategy
        if stockTicker in portfolio.keys():
            if MomentumBasedStrategy(stockHist, "sell"):
                SellStock(portfolio, funds, curPrice, stockTicker)

        else:
            if MomentumBasedStrategy(stockHist, "buy"):
                #Todo:Do not buy on observation: Pool first
                BuyStock(portfolio,funds,stockTicker,curPrice)

    SummarizeRun(portfolio)

#d = datetime.today() - timedelta(days=days_to_subtract)





#momentum strat:


#When the close crosses above the 100-day high of the close, we go long at the close.
#When the close crosses below the lowest close in the last 100 days, we sell at the close.

#It’s based on monthly quotes in the ETFs SPY, TLT, EFA, and EEM.
#We rank all four ETFs every month based on last month’s performance/momentum.
#We go long the ONE ETF with the best performance the prior month (it doesn’t matter if negative or positive return).
#Hold for one month and rinse and repeat (or continue being long the same instrument)

if(__name__ ==  "__main__"):
    Main()