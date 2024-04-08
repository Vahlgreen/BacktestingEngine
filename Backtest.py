# Libraries
import yfinance as yf
import os
import pandas as pd
from datetime import timedelta, datetime
import numpy as np

# project files
from PortfolioClass import Portfolio
from LogFunctions import LoadLogs, ResetLogs


def Main() -> None:
    # Initiate backtest parameters
    startDate = "01-01-2000"
    endDate = datetime.now().strftime('%Y-%m-%d')
    backtestData = GetBacktestData()
    portfolio = Portfolio()
    logPaths = ["Resources/Statistics/BacktestResults.csv", "Resources/Statistics/TradeReturns.csv"]

    # reset logs
    ResetLogs(logPaths)

    # Create enddates and run backtesting
    dateIterable = [date.strftime('%Y-%m-%d') for date in pd.date_range(startDate, endDate, freq='d').round("d") if
                    date.strftime('%Y-%m-%d') in backtestData.index.to_list()]

    for i, date in enumerate(dateIterable):
        print(f"Backtesting.. Simulation {i + 1} of {len(dateIterable)}")
        Backtest(backtestData, portfolio, date)

    portfolio.LogTradeReturns()
    LogIndexForLogScript(dateIterable,backtestData)
def LogIndexForLogScript(dateIterable: list, data: pd.DataFrame) -> None:
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "Resources/Data/s&pIndex.csv")

    startDate = dateIterable[0]
    endDate = dateIterable[-1]
    (data.loc[startDate:endDate,"S&P500"]/data.loc[startDate,"S&P500"]).to_csv(data_file,sep=",",header=False)

def GetBacktestData() -> pd.DataFrame:
    # Find directory (explicitly, to avoid issues on pe server)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "Resources/Data/Backtestdata.csv")
    data = pd.read_csv(data_file,index_col="Date", sep=",")

    if data.empty:
        raise Exception
    return data


def MomentumBasedStrategy(stockHist: pd.DataFrame, currentPrice: float, date: str, portfolio: Portfolio, ticker: str,
                          flag: str) -> bool:
    if flag.lower() == "buy":

        # Filter 1: yesterday was lower than today
        filter1 = stockHist.values[-2] < stockHist.values[-1]

        # Filter2: short term moving average must be larger than long term moving average
        # define lookback dates
        lowerDate = (datetime.strptime(date, '%Y-%m-%d').date() - timedelta(days=20)).strftime('%Y-%m-%d')
        upperDate = (datetime.strptime(date, '%Y-%m-%d').date() - timedelta(days=10)).strftime('%Y-%m-%d')
        filter2 = np.mean(stockHist.loc[lowerDate:date].values) < np.mean(stockHist.loc[upperDate:date].values)

        # Filter3: stocks with RSI>70 is considered over-saturated.

        # look-back period
        n = 14
        rsi = 100 - (100 / (
                1 + stockHist.diff(1).mask(stockHist.diff(1) < 0, 0).ewm(alpha=1 / n, adjust=False).mean() /
                stockHist.diff(1).mask(stockHist.diff(1) > 0, -0.0).abs().ewm(alpha=1 / n,
                                                                              adjust=False).mean())).values[-1][0]

        filter3 = rsi < 70

        return filter1 and filter2 and filter3

    elif flag.lower() == "sell":
        lowerDate = (datetime.strptime(date, '%Y-%m-%d').date() - timedelta(days=20)).strftime('%Y-%m-%d')
        upperDate = (datetime.strptime(date, '%Y-%m-%d').date() - timedelta(days=10)).strftime('%Y-%m-%d')
        filter2 = np.mean(stockHist.loc[lowerDate:date].values) > np.mean(stockHist.loc[upperDate:date].values)

        if filter2:
            return True

        elif currentPrice < portfolio.holdings.loc[ticker, "BuyPrice"] * 0.8 or currentPrice > \
                portfolio.holdings.loc[ticker, "BuyPrice"] * 1.5:
            return True
        else:
            return False
    else:
        raise Exception


def Backtest(data: pd.DataFrame, portfolio: Portfolio, date: str) -> None:
    # loop through symbols
    for stockTicker in data.columns:
        stockHist = pd.DataFrame({stockTicker: data[stockTicker]})
        currentPrice = stockHist.loc[date, stockTicker]

        if pd.isna(currentPrice):
            continue

        # Deploy strategy
        if stockTicker in portfolio.holdings.index.to_list():
            if MomentumBasedStrategy(stockHist, currentPrice, date, portfolio, stockTicker, "sell"):
                portfolio.funds = portfolio.funds + currentPrice * portfolio.holdings.loc[stockTicker, "Units"]
                portfolio.RemoveTicker(stockTicker, currentPrice)

        else:
            if MomentumBasedStrategy(stockHist, currentPrice, date, portfolio, stockTicker, "buy"):
                portfolio.pool.loc[len(portfolio.pool.index)] = [stockTicker, currentPrice, 0]

    # If the pool is not empty we process and buy
    if portfolio.pool.shape[0] > 0:
        portfolio.PreparePool()
        for row in portfolio.pool.iterrows():
            series = row[1]
            currentPrice = series["Price"]
            name = series["Name"]
            numUnits = series["UnitsToBuy"]

            if portfolio.funds >= currentPrice * numUnits:
                portfolio.funds = portfolio.funds - currentPrice * numUnits
                portfolio.AddTicker(name, numUnits, currentPrice)

    # Log results and reset stock pool
    portfolio.SetPortfolioWorth(data, date)
    portfolio.LogPortfolioState(date)
    portfolio.ResetPool()


if (__name__ == "__main__"):
    Main()
    LoadLogs()
