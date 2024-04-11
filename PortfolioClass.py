import os
import pickle
import pandas as pd
from datetime import timedelta, datetime
import math


class Portfolio:
    def __init__(self, startDate: str, endDate: str, funds: float = 100000.0):
        self.funds = funds
        #Todo: Delete holdings and use exclusively open trades and tradehistory
        self.holdings = pd.DataFrame(columns=["entryPrice", "Units"])
        self.startDate = startDate
        self.endDate = endDate
        self.openTrades = {}
        self.tradeHistory = []
        self.maxDrawdown = 1
        self.totValuePrimo = funds
        self.totValue = funds
        self.historicalStates = []
        self.transactionFee = 0.5
    def Sell(self, ticker: str, currentPrice: float, date) -> None:
        # Complete trade
        self.tradeHistory.append(self.openTrades[ticker].CompleteTrade(currentPrice, date))

        #adjust funds
        self.funds = self.funds + currentPrice * self.holdings.loc[ticker, "Units"] - self.transactionFee

        # Remove asset from holdings
        del self.openTrades[ticker]
        self.holdings = self.holdings.drop(ticker, axis=0)

    def Buy(self, ticker: str, numUnits: int, currentPrice: float, date: str) -> None:
        #Trade object
        newTrade = Trade(currentPrice, numUnits, date, ticker)

        #Add trade to holdings
        self.openTrades[ticker] = newTrade
        self.holdings.loc[ticker] = [currentPrice, numUnits]

        #adjust funds
        self.funds = self.funds - currentPrice * numUnits - self.transactionFee

    def GetPortfolioValue(self, stockData: pd.DataFrame, date: str) -> float:
        #portfolio value includes funds (cash)
        #Uses today's price to compute portfolio value.
        self.totValue = 0
        for key in self.holdings.index.to_list():
            currentPrice = stockData.loc[date, key]
            self.totValue = self.totValue + self.holdings.loc[key, "Units"] * currentPrice

        #Discount back to start?
        #timeDiff = datetime.strptime(self.endDate, '%Y-%m-%d').date() - datetime.strptime(self.startDate,'%Y-%m-%d').date()
        #self.totValue *= math.exp(-0.5*timeDiff.days)

        #Todo: Drawndown should be computed every timestep
        self.maxDrawdown = min(self.maxDrawdown, self.totValue / self.totValuePrimo)
        return self.totValue + self.funds

    def LogPortfolioState(self, data: pd.DataFrame, date: str) -> None:
        #Logs portfolio state each timestep
        totalPortfolioValue = self.GetPortfolioValue(data, date)
        assetValue = max(totalPortfolioValue - self.funds, 0)

        #Todo: Consider more appropriate datastructure
        self.historicalStates.append((totalPortfolioValue, assetValue, self.funds, len(self.tradeHistory), len(self.openTrades), date))

    def LogBackTestResults(self) -> None:
        #Summarizes backtest and prints to files
        script_directory = os.path.dirname(os.path.abspath(__file__))

        nTrades = len(self.tradeHistory)
        nDays = (datetime.strptime(self.endDate, '%Y-%m-%d').date() - datetime.strptime(self.startDate,
                                                                                              '%Y-%m-%d').date()).days
        portfolioReturn = self.totValue / self.totValuePrimo
        winCount = 0
        maxTradeDuration = 0
        averageProfit = 0
        averageLoss = 0
        listOfReturns = []

        #Loop through trades and compute statistics
        for trade in self.tradeHistory:
            winCount += trade.win

            timeDiff = datetime.strptime(trade.sellDate, '%Y-%m-%d').date() - datetime.strptime(trade.buyDate,
                                                                                                '%Y-%m-%d').date()
            #Todo: Does not consider currently open trades
            maxTradeDuration = max(maxTradeDuration, timeDiff.days)

            listOfReturns.append(trade.exitPrice / trade.entryPrice)

            if trade.win:
                averageProfit += (trade.exitPrice - trade.entryPrice) * trade.units
            else:
                averageLoss += (trade.entryPrice - trade.exitPrice) * trade.units

        averageReturn = sum(listOfReturns) / len(listOfReturns)
        sharpeDeviation = sum([((x - averageReturn) ** 2) for x in listOfReturns]) / len(listOfReturns)
        sortinoDeviation = sum([((x - averageReturn) ** 2) for x in listOfReturns if x < 1]) / len(listOfReturns)

        # To report
        sharpeRatio = (portfolioReturn - 0.5) / sharpeDeviation
        sortinoRatio = (portfolioReturn - 0.5) / sortinoDeviation
        averageProfit = averageProfit / nTrades
        averageLoss = averageLoss / nTrades
        winRate = winCount / nTrades
        lossRate = 1 - winRate
        profitFactor = (winRate * averageProfit) / (lossRate * averageLoss)

        logString = f"Total portfolio return: {portfolioReturn}\n" \
                    f"Average profit: {averageProfit}\n" \
                    f"Average loss: {averageLoss}\n" \
                    f"Profit factor: {profitFactor}\n" \
                    f"Max drawdown: {self.maxDrawdown}\n" \
                    f"Win Rate: {winRate}\n" \
                    f"Sharpe Ratio: {sharpeRatio}\n" \
                    f"Sortino Ratio: {sortinoRatio}\n" \
                    f"Longest position held: {maxTradeDuration} days\n" \
                    f"Number of trades: {len(self.tradeHistory)}\n" \
                    f"Average trades pr day: {len(self.tradeHistory)/nDays}"

        data_file = os.path.join(script_directory, "Resources/Results/BacktestResults.txt")
        with open(data_file, "w") as f:
            f.write(logString)
            f.close()

        data_file = os.path.join(script_directory, "Resources/Results/BacktestPortfolioStates.csv")
        logString = ""
        for state in self.historicalStates:
            logString += f"{state[0]},{state[1]},{state[2]},{state[3]},{state[4]},{state[5]}\n"

        with open(data_file, "a") as f:
            f.write(logString)
            f.close()

        data_file = os.path.join(script_directory, "Resources/Results/TradeReturns.csv")
        printList = [str(trade.GetReturn()) + "\n" for trade in self.tradeHistory]
        with open(data_file, "w") as f:
            f.writelines(printList)
            f.close()
class Trade:
    def __init__(self, entryPrice: float, units: int, buyDate: str, ticker: str):
        self.entryPrice = entryPrice
        self.units = units
        self.buyDate = buyDate
        self.ticker = ticker
        self.completed = False
        self.exitPrice = 0
        self.sellDate = ""
        self.win = False

    def CompleteTrade(self, currentPrice: float, date: str):
        self.exitPrice = currentPrice
        self.sellDate = date
        self.win = self.entryPrice < currentPrice

        return self

    def GetReturn(self) -> float:
        return self.exitPrice / self.entryPrice
