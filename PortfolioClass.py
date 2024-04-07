import os
import pickle
import pandas as pd


class Portfolio:
    def __init__(self, funds: float = 100000.0):
        self.funds = funds
        self.holdings = pd.DataFrame(columns=["BuyPrice", "Units"])
        self.pool = pd.DataFrame(columns=["Name", "Price", "UnitsToBuy"])
        self.tradeCounter = 0
        self.tradeReturns = []
        self.totValue = 0

        #Final report; Return%, Buy & Hold Return%, Buy & Hold Return, Sharpe Ratio, Sortino Ratio, Calmar Ratio, Max. Drawdown
        #Win Rate, Profit Factor, max trade duration,

    def PreparePool(self) -> None:
        # Prepares dataframe with stocks to buy. Also defines the order size in the process
        # Todo: Don't use 100% of available funds by default
        # maintain equal risk. divide investment equally among stocks to trade. divide price of the stock into that portion
        fundProportion = self.funds / self.pool.shape[0]

        # define number of units to buy
        self.pool['UnitsToBuy'] = self.pool.apply(lambda x: int(fundProportion / x.Price), axis=1)
        self.pool = self.pool[self.pool.apply(lambda x: True if x.UnitsToBuy > 0 else False, axis=1)]

    def ResetPool(self) -> None:
        self.pool = pd.DataFrame(columns=["Name", "Price", "UnitsToBuy"])
        self.tradeCounter = 0
    def RemoveTicker(self, ticker: str, currentPrice: float) -> None:
        self.tradeReturns.append(currentPrice / self.holdings.loc[ticker, "BuyPrice"])
        self.holdings = self.holdings.drop(ticker, axis=0)

    def AddTicker(self, ticker: str, numUnits: int, currentPrice: float) -> None:
        self.holdings.loc[ticker] = [currentPrice, numUnits]
        self.tradeCounter = self.tradeCounter + 1

    def GetPortfolioWorth(self, stockData: pd.DataFrame, date: str) -> float:
        totValue = 0
        if len(self.holdings) == 0:
            return totValue
        else:
            for key in self.holdings.index.to_list():
                currentPrice = stockData.loc[date, key]
                totValue = totValue + self.holdings.loc[key, "Units"] * currentPrice
            return totValue

    def SetPortfolioWorth(self, stockData: pd.DataFrame, date: str) -> None:
        self.totValue = self.funds
        for key in self.holdings.index.to_list():
            currentPrice = stockData.loc[date, key]
            self.totValue = self.totValue + self.holdings.loc[key, "Units"] * currentPrice

    def LogPortfolioState(self, endDate: str) -> None:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(script_directory, "Resources/Statistics/BacktestResults.txt")

        with open(data_file, "a") as f:
            f.write(f"{self.totValue},{self.totValue - self.funds},{self.funds},{self.tradeCounter}{endDate}\n")
            f.close()

    def LogTradeReturns(self) -> None:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(script_directory, "Resources/Statistics/TradeReturns.txt")
        printList = [str(num)+"\n" for num in self.tradeReturns]
        with open(data_file, "w") as f:
            f.writelines(printList)
            f.close()
