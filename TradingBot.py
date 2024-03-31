import yfinance as yf
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

class PortfolioObject:
    def __init__(self, curPrice: float, units: int,transactionDate: str):
        self.curPrice = curPrice
        self.units = units
        self.transactionDate = transactionDate

    def GetTotalValue(self):
        return self.curPrice*self.units
def DumpPortfolio(portfolio: dict) -> None:
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "portfolio.p")
    with open(data_file, "wb") as f:
        pickle.dump(portfolio,f)
        f.close()
def LoadPortfolio() -> dict:
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "portfolio.p")
    with  open(data_file, "rb") as f:
        portfolio = pickle.load(f)
        f.close()
    return portfolio
def ResetPortfolio(val=None) -> None:
    if val is None:
        val = {}
    DumpPortfolio(val)
def DumpFunds(funds: float) -> None:
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "funds.p")
    with open(data_file, "wb") as f:
        pickle.dump(funds,f)
        f.close()
def LoadFunds() -> float:
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "funds.p")
    with  open(data_file, "rb") as f:
        funds = pickle.load(f)
        f.close()
    return float(funds)
def ResetFunds(val: float = 10000) -> None:
    DumpFunds(float(val))
def BuyStock(portfolio: dict, funds: float, stockTicker: str, curPrice: float, numUnits: int) -> None:
    if funds >= curPrice:
        funds = funds - curPrice*numUnits
        portfolioObject = PortfolioObject(curPrice,numUnits,datetime.now().strftime('%Y-%m-%d'))
        portfolio[stockTicker] = portfolioObject
        print(f"Bought {stockTicker}")
    else:
        #Todo: errorhandling
        #raise Exception
        print("")
def SellStock(portfolio: dict, funds: float, stockTicker: str, curPrice: float) -> None:
    if stockTicker in portfolio.keys():
        funds = funds+curPrice*portfolio[stockTicker].units()
        del portfolio[stockTicker]
    else:
        #Todo: errorhandling
        raise Exception
def BackTestStrategy() -> None:
    pass
def MomentumBasedStrategy(stockHist: yf.ticker.Ticker.history,flag: str) -> bool:

    if flag == "buy":
        if stockHist.iloc[-1]>stockHist.iloc[-2]:
            return True
        else:
            return False
    else:
        if stockHist.iloc[-1]<stockHist.iloc[-2]:
            return True
        else:
            return False
    # # When the close crosses above the 25-day high of the close, we go long at the close.
    # # When the close crosses below the 25-day high of the close, we sell at the close.
    # period = 25
    # curMax = 0
    # if flag == "buy":
    #     #For some reason list[-x:-1] does not contain the last element of the list. However, list[-1] returns exactly that
    #     for obs in stockHist.iloc[-period+1:-1]:
    #         curMax = max(curMax, obs)
    #     return curMax < stockHist.iloc[-1]
    # elif flag == "sell":
    #     for obs in stockHist.iloc[-period+1:-1]:
    #         curMax = max(curMax, obs)
    #     return curMax > stockHist.iloc[-1]
    # else:
    #     raise Exception
def CreateBacktestOutput(portfolio: dict, funds: float,endDate: str) -> None:

    #Todo: save primo numbers to file for monthly recap
    #Todo: perhaps make portfolio custom class?

    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "BacktestResults.p")
    with open(data_file, "rb") as f:
        backTestResults = pickle.load(f)
        f.close()

    backTestResults.loc[len(backTestResults.index)] = [GetPortfolioWorth(portfolio), funds,datetime.date(endDate)]

    with open(data_file, "wb") as f:
        pickle.dump(backTestResults, f)
        f.close()
def GetPortfolioWorth(portfolio: dict) -> float:
    totValue = 0
    for key in portfolio.keys():
        totValue = totValue + portfolio[key].GetTotalValue()
    return totValue
def PrepareStockPool(stockPool: dict, stockTicker: str, curPrice: float, stockHist: yf.ticker.Ticker.history) -> None:
    stockPool["Name"].append(stockTicker)
    stockPool["Price"].append(curPrice)

    #Given a pd.dataframe we can compute RSI as a one-liner
    df = pd.DataFrame(stockHist,columns=["Close"])

    #look-back period
    n = 14

    #RSI computation
    df['Rsi'] = 100 - (100 / (
            1 + df['Close'].diff(1).mask(df['Close'].diff(1) < 0, 0).ewm(alpha=1 / n, adjust=False).mean() /
        df['Close'].diff(1).mask(df['Close'].diff(1) > 0, -0.0).abs().ewm(alpha=1 / n, adjust=False).mean()))

    stockPool["Rsi"].append(df["Rsi"].iloc[-1])
def ProcessStockPool(stockPool: dict, portfolio: dict,funds: float) -> None:
    #Process and buy stockpool.
    #Todo: Don't use 100% of available funds by default
    df = pd.DataFrame(stockPool)

    #cleanup. stocks with RSI>70 is considered over-saturated
    df = df[df.apply(lambda x: True if x.Rsi < 70 else False, axis=1)]
    df = df.sort_values("Rsi")

    #allocate funds based on distribution of RSI
    df['Temp'] = df.apply(lambda x: 1 / (x.Rsi ** 2), axis=1)
    df['FundProportion'] = df.apply(lambda x: (1/(x.Rsi ** 2))/df["Temp"].sum(), axis=1)

    #define number of units to buy
    df['UnitsToBuy'] = df.apply(lambda x: int(x.FundProportion*funds/x.Price), axis=1)

    for row in df.iterrows():
        series = row[1]
        BuyStock(portfolio,funds,series["Name"],series["Price"],series["UnitsToBuy"])
def ValidateHistoryData(stockHist: yf.ticker.Ticker.history,endDate: str) -> bool:
    if stockHist.empty:
        return False
    elif stockHist.last_valid_index().strftime('%Y-%m-%d') < (datetime.date(endDate) - timedelta(weeks=1)).strftime('%Y-%m-%d'):
        return False
    else:
        return True
def Deploy(exchange: pd.DataFrame,endDate: str = datetime.now().strftime('%Y-%m-%d')) -> None:

    stockPool = {
        "Name": [],
        "Price":[],
        "Rsi":[]
    }
    ResetFunds()
    ResetPortfolio()

    funds = LoadFunds()
    portfolio = LoadPortfolio()

    #For statistics
    #primoPortfolio = GetPortfolioWorth(portfolio)
    #loop through exchange
    for row in exchange.iterrows():
        stockTicker = row[1][0]
        print(stockTicker)
        #Ticker object
        stockObject = yf.Ticker(stockTicker)

        #Date format is strict
        stockHist = stockObject.history(start='2000-01-01', end=endDate)["Close"]

        if not ValidateHistoryData(stockHist,endDate):
            continue
        curPrice = stockHist.iloc[-1]

        #Deploy strategy
        if stockTicker in portfolio.keys():
            if MomentumBasedStrategy(stockHist, "sell"):
                SellStock(portfolio, funds, curPrice, stockTicker)

        else:
            if MomentumBasedStrategy(stockHist, "buy"):
                #Todo: keep statistics on the amount of stocks passing the momentum criteria
                print(f"Considering {stockTicker}")
                PrepareStockPool(stockPool,stockTicker,curPrice,stockHist)
    #If the pool is not empty we process and buy
    if stockPool["Name"] != []:
        ProcessStockPool(stockPool,portfolio,funds)
        CreateBacktestOutput(portfolio,funds,endDate)
    else:
        print("No stocks found")
def Backtest(exchange: pd.DataFrame,startDate: str, endDate: str) -> None:
    #reset backtest results before run
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "BacktestResults.p")
    with open(data_file, "wb") as f:
        pickle.dump(pd.DataFrame(columns=["TotalValue","Funds","TransactionDate"]),f)
        f.close()

    dateIterable = pd.date_range(startDate,endDate,freq='d')
    for date in dateIterable:
        Deploy(exchange,endDate=date)

def Main(deployOrBacktest: str) -> None:
    #Find directory (explicitly, to avoid issues on pe server)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "tickersymbols.csv")

    #on deployment, we take all 500 stocks and deploy the algorithm
    exchange = pd.read_csv(data_file, nrows=250)  # sp500
    #On backtest we choose one or more stocks to backtest the algorithm
    backtestTickerList = pd.DataFrame({"Name":["AAPL","AMZN","SOUN","PEP","CRM","TSLA","NVDA"]})

    if deployOrBacktest.lower() == "deploy":
        # Todo: download sp500 ticker list every ?monday? and overwrite in disk
        Deploy(exchange)

    elif deployOrBacktest.lower() == "backtest":
        exchange = backtestTickerList#exchange[exchange.apply(lambda x: True if x.TICKERS in backtestTickerList else False, axis=1)]
        if exchange.empty:
            raise Exception
        Backtest(exchange,"01-01-2015",datetime.now().strftime('%Y-%m-%d'))


#momentum strat:
#When the close crosses above the 100-day high of the close, we go long at the close.
#When the close crosses below the lowest close in the last 100 days, we sell at the close.

#It’s based on monthly quotes in the ETFs SPY, TLT, EFA, and EEM.
#We rank all four ETFs every month based on last month’s performance/momentum.
#We go long the ONE ETF with the best performance the prior month (it doesn’t matter if negative or positive return).
#Hold for one month and rinse and repeat (or continue being long the same instrument)

if(__name__ ==  "__main__"):
    #Main("Deploy")
    Main("Backtest")