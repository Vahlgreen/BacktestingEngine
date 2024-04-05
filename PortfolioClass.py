import os
import pickle
import pandas as pd

class Portfolio:
    def __init__(self, funds: float = 100000.0):
        self.funds = funds
        self.holdings = {}
        self.pool = pd.DataFrame(columns=["Name","Price","UnitsToBuy"])

    def PreparePool(self) -> None:
        # Prepares dataframe with stocks to buy. Also defines the order size in the process
        # Todo: Don't use 100% of available funds by default

        # maintain equal risk. divide investment equally among stocks to trade. divide price of the stock into that portion
        fundProportion = self.funds / self.pool.shape[0]

        # define number of units to buy
        self.pool['UnitsToBuy'] = self.pool.apply(lambda x: int(fundProportion / x.Price), axis=1)

        self.pool = self.pool[self.pool.apply(lambda x: True if x.UnitsToBuy > 0 else False, axis=1)]

    def DumpPortfolio(self, portfolioFile: str) -> None:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(script_directory, portfolioFile)
        with open(data_file, "wb") as f:
            pickle.dump(self, f)
            f.close()

    def GetPortfolioWorth(self) -> float:
        totValue = 0
        if len(self.holdings) == 0:
            return totValue
        else:
            for key in self.holdings.keys():
                totValue = totValue + self.holdings[key][0]*self.holdings[key][1] #pris*antal
            return totValue

# class Stock:
#     def __init__(self,transactionDate: str,):
#         self.transactionDate = transactionDate
    # @staticmethod
    # def DumpFunds(funds: float) -> None:
    #     script_directory = os.path.dirname(os.path.abspath(__file__))
    #     data_file = os.path.join(script_directory, "Resources/funds.p")
    #     with open(data_file, "wb") as f:
    #         pickle.dump(funds, f)
    #         f.close()

    # def LoadPortfolio(portfolioFile: str) -> dict:
    #     script_directory = os.path.dirname(os.path.abspath(__file__))
    #     data_file = os.path.join(script_directory, portfolioFile)
    #     with  open(data_file, "rb") as f:
    #         portfolio = pickle.load(f)
    #         f.close()
    #     return portfolio

    # def LoadFunds(self) -> float:
    #     script_directory = os.path.dirname(os.path.abspath(__file__))
    #     data_file = os.path.join(script_directory, "Resources/funds.p")
    #     with  open(data_file, "rb") as f:
    #         funds = pickle.load(f)
    #         f.close()
    #     return float(funds)