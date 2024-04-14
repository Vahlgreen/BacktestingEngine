import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import mplcursors

# project files
import functions
def LoadLogs() -> tuple:

    # Read logs
    # portfolio development
    data_file = functions.AbsPath("Resources/Results/PortfolioStates.csv")
    portfolioLog = pd.read_csv(data_file, sep=",", names=["TotalValue", "portfolioValue", "funds","Trades","Positions","Date"])
    portfolioLog["Date"].apply(lambda x: x.split(" ")[0])
    portfolioLog["PortfolioIndex"] = portfolioLog["TotalValue"] / portfolioLog["TotalValue"].to_list()[0]
    # rolling statistics
    portfolioLog["Moving Average"] = portfolioLog["PortfolioIndex"].rolling(window=50,min_periods=1).mean()
    portfolioLog["Volatility"] = portfolioLog["PortfolioIndex"].rolling(window=50,min_periods=1).std().fillna(0)

    # Index for comparison
    data_file = functions.AbsPath("Resources/Data/s&pIndex.csv")
    exchangeIndex = pd.read_csv(data_file, sep=",",names=["Date","S&P500"])

    # Create common dataframe
    portfolioLog["Date"] = exchangeIndex["Date"]
    portfolioLog["S&P500"] = exchangeIndex["S&P500"]

    #Returns are logged on a trade basis, and so the df has different length
    data_file = functions.AbsPath("Resources/Results/TradeReturns.csv")
    returns = pd.read_csv(data_file, sep=",", names=["Returns"])

    return portfolioLog, returns

def CreatePlots(portfolio_states: pd.DataFrame, trade_log: pd.DataFrame) -> None:

    # Create main plot. Portfolio index vs s&p 500
    fig = go.Figure()
    # portfolio
    fig.add_trace(go.Scatter(x=portfolio_states["Date"],
                             y=portfolio_states["PortfolioIndex"],
                             name="Portfolio index"))
                             #mode='markers',
                             #marker = dict(size=5)))

    # moving average
    fig.add_trace(go.Scatter(x=portfolio_states["Date"],
                             y=portfolio_states["Moving Average"],
                             name="Moving Average"))

    # confidence interval
    fig.add_traces([go.Scatter(x=portfolio_states["Date"],
                              y=portfolio_states["Moving Average"]-portfolio_states["Volatility"]
                              ,showlegend = False,
                              line_color = 'rgba(0,0,0,0)'),
                   go.Scatter(x=portfolio_states["Date"],
                              y=portfolio_states["Moving Average"]+portfolio_states["Volatility"],
                              name = 'Volatility',
                              line_color='rgba(0,0,0,0)',
                              fill='tonexty',fillcolor = 'rgba(255, 0, 0, 0.2)')])
    # s&p
    fig.add_trace(go.Scatter(x=portfolio_states["Date"],
                             y=portfolio_states["S&P500"],
                             name="S&P 500"))
                             #mode='markers',
                             #marker=dict(size=5)))

    #fig.update_traces(mode="markers+lines")
    fig.write_html(functions.AbsPath("Resources/Results/Plots/portfolio_vs_index.html"))
    fig.show()

    # trades and positions
    ax = portfolio_states.plot(x="Date",y="Trades",figsize=(15, 7))
    portfolio_states.plot(x="Date", y="Positions", ax=ax)
    plt.savefig(functions.AbsPath("Resources/Results/Plots/TradesAndPositions.png"))

    # portfolio returns
    hist_figure = px.histogram(trade_log, x="Returns", nbins=round(trade_log.shape[0] / 1.5))
    hist_figure.write_image(functions.AbsPath("Resources/Results/Plots/Returns.png"))
    #hist_figure.show()

if __name__ == "__main__":
    (portfolio_states,trade_log) = LoadLogs()
    CreatePlots(portfolio_states,trade_log)
