import os
import pickle
import pandas as pd


class Portfolio:
    def __init__(self):
        self.funds = funds
        self.holdings = pd.DataFrame(columns=["BuyPrice", "Units"])
        self.pool = pd.DataFrame(columns=["Name", "Price", "UnitsToBuy"])
        self.tradeCounter = 0
        self.tradeReturns = []
        self.totValue = 0
