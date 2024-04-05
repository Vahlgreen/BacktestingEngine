# Libraries
import yfinance as yf
import os
import pandas as pd
import datetime  # import datetime, timedelta
from datetime import timedelta, datetime
import numpy as np

# project files
from PortfolioClass import Portfolio
from LogFunctions import LogDeploymentResults, LoadLogs


def Main() -> None:
    # Initiate backtest parameters
    startDate = "01-01-2024"
    endDate = datetime.now().strftime('%Y-%m-%d')
    backtestData = GetBacktestData()
    portfolio = Portfolio()

    # reset log
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "Resources/BacktestResults.txt")
    if os.path.exists(data_file):
        os.remove(data_file)

    # Create enddates and run backtesting
    dateIterable = [date.strftime('%Y-%m-%d') for date in pd.date_range(startDate, endDate, freq='d').round("d")]

    for i, date in enumerate(dateIterable):
        print(f"Backtesting.. Simulation {i + 1} of {len(dateIterable)}")
        Backtest(backtestData, portfolio, endDate=date)


def GetBacktestData() -> pd.DataFrame:
    # Find directory (explicitly, to avoid issues on pe server)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "Resources/Backtestdata.csv")
    data = pd.read_csv(data_file, sep=",")

    data.index = data["Date"].apply(lambda x: x.split(" ")[0])
    data = data.drop("Date", axis=1)
    # backtestTickers = pd.DataFrame({"Name": ["AAPL", "AMZN", "SOUN", "PEP", "CRM", "TSLA", "NVDA", "T"]})
    if data.empty:
        raise Exception
    return data


def MomentumBasedStrategy(stockHist: pd.DataFrame, portfolio: Portfolio, flag: str) -> bool:
    if flag.lower() == "buy":
        filter1 = stockHist.values[-2] < stockHist.values[-1]

        # Filter2: short term moving average must be larger than long term moving average
        filter2 = np.mean(stockHist.values[-20:]) < np.mean(stockHist.values[-10:])

        # Filter3: stocks with RSI>70 is considered over-saturated.

        # look-back period
        n = 14
        rsi = 100 - (100 / (
                1 + stockHist.diff(1).mask(stockHist.diff(1) < 0, 0).ewm(alpha=1 / n, adjust=False).mean() /
                stockHist.diff(1).mask(stockHist.diff(1) > 0, -0.0).abs().ewm(alpha=1 / n, adjust=False).mean())).values[-1][0]

        filter3 = rsi < 70

        return filter1 and filter2 and filter3

    elif flag.lower() == "sell":
        # stoploss
        if stockHist.values[-1] < portfolio.holdings[stockHist.columns[0]][0] * 0.8 or stockHist.values[-1] > \
                portfolio.holdings[stockHist.columns[0]][0] * 1.2:
            return True
    else:
        raise Exception


def Backtest(data: pd.DataFrame, portfolio: Portfolio, endDate: str) -> None:
    # loop through exchange
    for stockTicker in data.columns:

        stockHist = pd.DataFrame({stockTicker: data[stockTicker]})
        curPrice = stockHist.values[-1][0]

        # Deploy strategy
        if stockTicker in portfolio.holdings.keys():
            if MomentumBasedStrategy(stockHist, portfolio, "sell"):
                if stockTicker in portfolio.holdings.keys():
                    portfolio.funds = portfolio.funds + curPrice * portfolio.holdings[stockTicker][1]
                    del portfolio.holdings[stockTicker]
                else:
                    # Todo: errorhandling
                    raise Exception
        else:
            if MomentumBasedStrategy(stockHist, portfolio, "buy"):
                # Todo: keep statistics on the amount of stocks passing the momentum criteria
                portfolio.pool.loc[len(portfolio.pool.index)] = [stockTicker, curPrice, 0]

    # If the pool is not empty we process and buy
    if portfolio.pool.shape[0] > 0:
        portfolio.PreparePool()
        for row in portfolio.pool.iterrows():
            series = row[1]
            curPrice = series["Price"]
            name = series["Name"]
            numUnits = series["UnitsToBuy"]

            if portfolio.funds >= curPrice:
                portfolio.funds = portfolio.funds - curPrice * numUnits
                portfolio.holdings[name] = (curPrice, numUnits)
            else:
                pass
                # Todo: errorhandling
                # raise Exception

    # Log results
    LogDeploymentResults(portfolio.GetPortfolioWorth() + portfolio.funds, endDate)


if (__name__ == "__main__"):
    Main()
    LoadLogs()
