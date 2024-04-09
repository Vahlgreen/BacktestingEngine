import pandas as pd
import os
import matplotlib.pyplot as plt
import csv


def LoadLogs() -> None:
    script_directory = os.path.dirname(os.path.abspath(__file__))

    data_file = os.path.join(script_directory, "Resources/Statistics/BacktestResults.csv")
    portfolioLog = pd.read_csv(data_file, sep=",", names=["TotalValue", "portfolioValue", "funds", "Date"])
    portfolioLog["Date"].apply(lambda x: x.split(" ")[0])
    portfolioLog["PortfolioIndex"] = portfolioLog["TotalValue"] / portfolioLog["TotalValue"].to_list()[0]

    data_file = os.path.join(script_directory, "Resources/Data/s&pIndex.csv")
    exchangeIndex = pd.read_csv(data_file, sep=",",names=["Date","S&P500"])
    portfolioLog["Date"] = exchangeIndex["Date"]

    ax = portfolioLog.plot(x="Date", y="PortfolioIndex")
    exchangeIndex.plot(x="Date", y="S&P500", ax=ax)
    plt.show(block=True)

    # Read returns
    data_file = os.path.join(script_directory, "Resources/Statistics/TradeReturns.csv")
    portfolioLog = pd.read_csv(data_file, sep=",", names=["Returns"])

    portfolioLog.plot.hist(bins=500)
    plt.show(block=True)


def ResetLogs(paths: list) -> None:
    for path in paths:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(script_directory, path)
        if os.path.exists(data_file):
            os.remove(data_file)


if __name__ == "__main__":
    LoadLogs()
