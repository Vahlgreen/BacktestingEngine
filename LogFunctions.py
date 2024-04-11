import pandas as pd
import os
import matplotlib.pyplot as plt
import csv


def LoadLogs() -> None:
    script_directory = os.path.dirname(os.path.abspath(__file__))

    #Read logs
    #portfolio development
    data_file = os.path.join(script_directory, "Resources/Results/BacktestPortfolioStates.csv")
    portfolioLog = pd.read_csv(data_file, sep=",", names=["TotalValue", "portfolioValue", "funds","Trades","Positions","Date"])
    portfolioLog["Date"].apply(lambda x: x.split(" ")[0])
    portfolioLog["PortfolioIndex"] = portfolioLog["TotalValue"] / portfolioLog["TotalValue"].to_list()[0]

    #Index for comparison
    data_file = os.path.join(script_directory, "Resources/Data/s&pIndex.csv")
    exchangeIndex = pd.read_csv(data_file, sep=",",names=["Date","S&P500"])
    portfolioLog["Date"] = exchangeIndex["Date"]

    #Returns
    data_file = os.path.join(script_directory, "Resources/Results/TradeReturns.csv")
    returns = pd.read_csv(data_file, sep=",", names=["Returns"])

    #plots
    #portfolio
    ax = portfolioLog.plot(x="Date", y="PortfolioIndex",figsize=(15, 7))
    exchangeIndex.plot(x="Date", y="S&P500", ax=ax)
    plt.savefig(os.path.join(script_directory, "Resources/Results/Plots/portfolio_vs_index.png"))
    plt.show(block=True)

    #Trades and positions
    ax = portfolioLog.plot(x="Date",y="Trades",figsize=(15, 7))
    portfolioLog.plot(x="Date", y="Positions", ax=ax)
    plt.savefig(os.path.join(script_directory, "Resources/Results/Plots/TradesAndPositions.png"))
    plt.show(block=True)

    #Returns
    returns.plot.hist(bins=500,figsize=(15, 7))
    plt.savefig(os.path.join(script_directory, "Resources/Results/Plots/returns.png"))
    plt.show(block=True)


def ResetLogs(paths: list) -> None:
    for path in paths:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(script_directory, path)
        if os.path.exists(data_file):
            os.remove(data_file)


if __name__ == "__main__":
    LoadLogs()
