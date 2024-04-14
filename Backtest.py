# Libraries
import yfinance as yf
import os
import pandas as pd
from datetime import timedelta, datetime
import numpy as np

# project files
from PortfolioClass import Portfolio
import functions


def Main():
    # Initiate backtest parameters
    backtestData = GetBacktestData()
    startDate = "2020-01-02"
    endDate = str(backtestData.last_valid_index())
    portfolio = Portfolio(startDate, endDate)

    # establish trade dates
    marketDays = [date.strftime('%Y-%m-%d') for date in pd.date_range(startDate, endDate, freq='d').round("d") if
                    date.strftime('%Y-%m-%d') in backtestData.index.to_list()]

    if startDate not in marketDays:
        raise Exception("Start date not valid")

    # Run backtest
    for i, date in enumerate(marketDays):
        print(f"Backtesting.. Simulation {i + 1} of {len(marketDays)}")
        Backtest(backtestData, portfolio, date)

    # Log comparable index during backtest time frame
    LogIndexForLogScript(startDate, endDate, backtestData)

    # logs results
    portfolio.LogBackTestResults()

def LogIndexForLogScript(startDate: str, endDate: str, data: pd.DataFrame) -> None:
    data_file = functions.AbsPath("Resources/Data/s&pIndex.csv")
    (data.loc[startDate:endDate, "S&P500"] / data.loc[startDate, "S&P500"]).to_csv(data_file, sep=",", header=False)

def GetBacktestData() -> pd.DataFrame:
    # Find directory (explicitly, to avoid issues on pe server)
    data_file = functions.AbsPath("Resources/Data/s&p500.csv")
    data = pd.read_csv(data_file, sep=";", index_col="Date").drop("Unnamed: 0",axis=1)

    if data.empty:
        raise Exception
    return data

def MomentumBasedStrategy(stockHist: pd.DataFrame, currentPrice: float, date: str, portfolio: Portfolio, ticker: str,
                          flag: str) -> bool:
    # implements the trading strategy.
    if flag.lower() == "buy":

        # Filter 1: yesterday was lower than today
        filter1 = stockHist.values[-2] < stockHist.values[-1]

        # Filter2: short term moving average must be larger than long term moving average
        # define lookback dates
        lowerDate = functions.SubtractDays(date,20)
        upperDate = functions.SubtractDays(date,10)
        #functions

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
        lowerDate = functions.SubtractDays(date,20)
        upperDate = functions.SubtractDays(date,10)
        filter2 = np.mean(stockHist.loc[lowerDate:date].values) > np.mean(stockHist.loc[upperDate:date].values)

        if filter2:
            return True

        elif currentPrice < portfolio.openTrades[ticker].entryPrice * 0.8 or currentPrice > \
                portfolio.openTrades[ticker].entryPrice * 1.5:
            return True
        else:
            return False
    else:
        raise Exception


def Backtest(data: pd.DataFrame, portfolio: Portfolio, date: str) -> None:
    pool = pd.DataFrame(columns=["Name", "Price", "PositionSize"])
    # loop through symbols
    for stockTicker in data.columns:
        stockHist = pd.DataFrame({stockTicker: data[stockTicker]})
        currentPrice = stockHist.loc[date, stockTicker]

        if pd.isna(currentPrice):
            #Todo: if stock was delisted the portfolio should take the loss
            if stockTicker in portfolio.openTrades.keys():
                print("")
            continue

        # Deploy strategy
        if stockTicker in portfolio.openTrades.keys():
            if MomentumBasedStrategy(stockHist, currentPrice, date, portfolio, stockTicker, "sell"):
                portfolio.Sell(stockTicker, currentPrice, date)

        else:
            if MomentumBasedStrategy(stockHist, currentPrice, date, portfolio, stockTicker, "buy"):
                pool.loc[len(pool.index)] = [stockTicker, currentPrice, 0]

    # If the pool is not empty we process and buy
    if pool.shape[0] > 0:
        # Todo: Don't use 100% of available funds by default
        # maintain equal risk. divide investment equally among stocks to trade. divide price of the stock into that portion
        fundProportion = portfolio.funds / pool.shape[0]

        # position size
        pool['PositionSize'] = pool.apply(lambda x: int(fundProportion / x.Price), axis=1)
        pool = pool[pool.apply(lambda x: True if x.PositionSize > 0 else False, axis=1)]

        for row in pool.iterrows():
            series = row[1]
            currentPrice = series["Price"]
            name = series["Name"]
            positionSize = series["PositionSize"]

            if portfolio.funds >= currentPrice * positionSize:
                portfolio.Buy(name, positionSize, currentPrice, date)

    # Log results and reset stock pool
    portfolio.LogPortfolioState(data, date)


if (__name__ == "__main__"):
    Main()
