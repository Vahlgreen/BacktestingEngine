import os
import pickle
import pandas as pd
from datetime import timedelta, datetime
import numpy as np

#Project files
import functions

#TODO: log top three stocks and associated results. Perhaps plot those equity curves

class Portfolio:
    def __init__(self, startDate: str, endDate: str, funds: float = 100000.0):
        self.funds = funds
        self.startDate = startDate
        self.endDate = endDate
        self.openTrades = {}
        self.tradeHistory = []
        self.maxDrawdown = 1
        self.totValuePrimo = funds
        self.totValue = funds
        self.stateLog = []
        self.tradeLog = {}
        self.transactionFee = 0.5

    def Sell(self, ticker: str, currentPrice: float, date: str) -> None:
        # Complete trade
        trade = self.openTrades[ticker].CompleteTrade(currentPrice, date)
        self.tradeHistory.append(trade)

        # adjust funds
        self.funds = self.funds + currentPrice * self.openTrades[ticker].positionSize - self.transactionFee

        # log trade
        if date in self.tradeLog.keys():
            self.tradeLog[date].update({ticker: (trade.return_, trade.gain, trade.entryDate, trade.duration)})
        else:
            self.tradeLog[date]={ticker: (trade.return_, trade.gain, trade.entryDate, trade.duration)}

        # Remove asset from holdings
        del self.openTrades[ticker]

    def Buy(self, ticker: str, positionSize: int, currentPrice: float, date: str) -> None:
        # Trade object
        newTrade = Trade_(currentPrice, positionSize, date, ticker)

        # Add trade to holdings
        self.openTrades[ticker] = newTrade

        # adjust funds
        self.funds = self.funds - currentPrice * positionSize - self.transactionFee

    def GetPortfolioValue(self, stockData: pd.DataFrame, date: str) -> float:
        # portfolio value includes funds (cash)
        # Uses today's price to compute portfolio value.
        self.totValue = 0
        for key in self.openTrades.keys():
            currentPrice = stockData.loc[date, key]
            self.totValue += self.openTrades[key].positionSize * currentPrice

        return self.totValue + self.funds

    def LogPortfolioState(self, data: pd.DataFrame, date: str) -> None:
        # Logs portfolio state each timestep
        totalPortfolioValue = self.GetPortfolioValue(data, date)
        assetValue = max(totalPortfolioValue - self.funds, 0)

        self.maxDrawdown = min(self.maxDrawdown, totalPortfolioValue / self.totValuePrimo)

        # Todo: Consider more appropriate datastructure
        self.stateLog.append(
            (round(totalPortfolioValue), round(assetValue), round(self.funds), len(self.tradeHistory), len(self.openTrades), date))

    def LogBackTestResults(self) -> None:
        # Summarizes backtest and prints to files

        nTrades = len(self.tradeHistory)
        nDays = functions.DateDiff(self.startDate,self.endDate)
        portfolioReturn = (self.totValue+self.funds) / self.totValuePrimo
        winCount = 0
        maxTradeDuration = (0,"")
        listOfReturns = np.array([])
        listOfLosses = np.array([])
        listOfProfits = np.array([])

        # Loop through trades and compute statistics
        for trade in self.tradeHistory:
            if trade.win:
                winCount += trade.win
                #maybe use combined average?
                listOfProfits = np.append(listOfProfits, trade.profit)
            else:
                listOfLosses = np.append(listOfLosses, trade.loss)

            # Todo: Consider currently open trades
            if maxTradeDuration[0] < trade.duration:
                maxTradeDuration = (trade.duration,trade.ticker)

            listOfReturns = np.append(listOfReturns, trade.return_)

        averageProfit = np.mean(listOfProfits)
        averageLoss = np.mean(listOfLosses)
        averageReturn = np.mean(listOfReturns)
        sharpDeviation = np.std(listOfReturns)
        sortinoDeviation = np.std(listOfReturns, where=listOfReturns < 1)

        sharpeRatio = (averageReturn - 0.5) / sharpDeviation
        sortinoRatio = (averageReturn - 0.5) / sortinoDeviation
        winRate = winCount / nTrades
        lossRate = 1 - winRate
        profitFactor = (winRate * averageProfit) / (lossRate * averageLoss)

        logString = f"Total portfolio return:            {round((portfolioReturn-1)*100,1)}%\n" \
                    f"Average profit:                    ${round(averageProfit)}\n" \
                    f"Average Profit var. coefficient:   {round(np.std(listOfProfits)/averageProfit,1)}%\n"\
                    f"Average loss:                      ${round(averageLoss)}\n" \
                    f"Average loss var. coefficient:     {round(np.std(listOfLosses)/averageLoss,1)}%\n"\
                    f"Profit factor:                     {round(profitFactor,1)}\n" \
                    f"Max drawdown:                      {round((self.maxDrawdown-1)*100,1)}%\n" \
                    f"Win Rate:                          {round(winRate*100,1)}%\n" \
                    f"Sharpe Ratio:                      {round(sharpeRatio,1)}\n" \
                    f"Sortino Ratio:                     {round(sortinoRatio,1)}\n" \
                    f"Longest position held ({maxTradeDuration[1]}):      {maxTradeDuration[0]} days\n" \
                    f"Number of trades:                  {len(self.tradeHistory)}\n" \
                    f"Average trades pr day:             {round(len(self.tradeHistory) / nDays,1)}"

        data_file = functions.AbsPath("Resources/Results/BacktestResults.txt")
        with open(data_file, "w") as f:
            f.write(logString)
            f.close()

        data_file = functions.AbsPath("Resources/Results/PortfolioStates.csv")
        logString = ""
        for state in self.stateLog:
            logString += f"{state[0]},{state[1]},{state[2]},{state[3]},{state[4]},{state[5]}\n"

        with open(data_file, "w") as f:
            f.write(logString)
            f.close()

        data_file = functions.AbsPath("Resources/Results/TradeReturns.csv")
        printList = [str(trade.return_) + "\n" for trade in self.tradeHistory]
        with open(data_file, "w") as f:
            f.writelines(printList)
            f.close()

        data_file = functions.AbsPath("Resources/Results/TradeLog.txt")
        logString = ""
        for date in self.tradeLog.keys():
            logString = logString + f"{date}\n"
            for ticker in self.tradeLog[date]:
                info = self.tradeLog[date][ticker]
                logString += f"ticker: {ticker} Return: {round(info[0],2)}, gain: {round(info[1])}, entry date: {info[2]}, duration: {info[3]}\n"
            logString += "\n"
        with open(data_file, "w") as f:
            f.write(logString)
            f.close()
class Trade_:
    def __init__(self, entryPrice: float, positionSize: int, entryDate: str, ticker: str):
        self.entryPrice = entryPrice
        self.positionSize = positionSize
        self.entryDate = entryDate
        self.ticker = ticker
        self.completed = False
        self.exitPrice = 0
        self.exitDate = ""
        self.win = False
        self.duration = 0
        self.profit = 0
        self.loss = 0
        self.return_ = 0
        self.gain = 0

    def CompleteTrade(self, currentPrice: float, exitDate: str):
        self.exitPrice = currentPrice
        self.exitDate = exitDate
        self.win = self.entryPrice < self.exitPrice
        if self.win:
            self.profit = (self.exitPrice - self.entryPrice) * self.positionSize
        else:
            self.loss = (self.entryPrice - self.exitPrice) * self.positionSize

        self.gain = (self.exitPrice - self.entryPrice) * self.positionSize
        self.duration = functions.DateDiff(self.entryDate,self.exitDate)
        self.return_ = self.exitPrice / self.entryPrice
        return self

