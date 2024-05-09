import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import mplcursors

# project files
import functions
from parameters import data_provider
def load_logs() -> tuple:

    # Read logs
    # portfolio development
    data_file = functions.get_absolute_path("Resources/Results/portfolio_states.csv")
    portfolio_log = pd.read_csv(data_file, sep=",", names=["totalValue", "portfolioValue", "funds","trades","positions","date"])
    portfolio_log["date"].apply(lambda x: x.split(" ")[0])
    portfolio_log["portfolioIndex"] = portfolio_log["totalValue"] / portfolio_log["totalValue"].to_list()[0]
    # rolling statistics
    portfolio_log["movingAverage"] = portfolio_log["portfolioIndex"].rolling(window=50,min_periods=1).mean()
    portfolio_log["volatility"] = portfolio_log["portfolioIndex"].rolling(window=50,min_periods=1).std().fillna(0)

    # Index for comparison
    data_file = functions.get_absolute_path(f"Resources/Results/Index/{data_provider}_index.csv")
    exchange_index = pd.read_csv(data_file, sep=",",names=["date","index"])

    # Create common dataframe
    portfolio_log["date"] = exchange_index["date"]
    portfolio_log["exchangeIndex"] = exchange_index["index"]

    #Returns are logged on a trade basis, and so the df has different length
    data_file = functions.get_absolute_path("Resources/Results/trade_returns.csv")
    returns = pd.read_csv(data_file, sep=",", names=["returns"])

    return portfolio_log, returns

def create_plots(states: pd.DataFrame, trades: pd.DataFrame) -> None:

    # Create main plot. Portfolio index vs s&p 500
    fig = go.Figure()
    # portfolio
    fig.add_trace(go.Scatter(x=states["date"],
                             y=states["portfolioIndex"],
                             name="Portfolio index",
                             customdata=states[["portfolioIndex","totalValue","portfolioValue", "funds","trades","positions"]],
                             hovertemplate=
                            "portfolioIndex: <b>%{customdata[0]}</b><br>" +
                            "total equity: <b>%{customdata[1]:$,.0f}</b><br>" +
                            "asset value: <b>%{customdata[2]:$,.0f}</b><br>" +
                            "funds: <b>%{customdata[3]:$,.0f}</b><br>" +
                            "trades: <b>%{customdata[4]}</b><br>" +
                            "positions: <b>%{customdata[5]}</b><br>" +
                            "<extra></extra>"))

    # # moving average
    # fig.add_trace(go.Scatter(x=states["date"],
    #                          y=states["movingAverage"],
    #                          name="Moving Average"))

    # confidence interval
    fig.add_traces([go.Scatter(x=states["date"],
                               y=states["movingAverage"] - states["volatility"],
                               showlegend = False,
                               line_color = 'rgba(0,0,0,0)',
                               hoverinfo='skip'),
                   go.Scatter(x=states["date"],
                              y=states["movingAverage"] + states["volatility"],
                              name = 'Volatility',
                              line_color='rgba(0,0,0,0)',
                              fill='tonexty', fillcolor = 'rgba(255, 0, 0, 0.2)',
                              hoverinfo='skip')])
    # s&p
    fig.add_trace(go.Scatter(x=states["date"],
                             y=states["exchangeIndex"],
                             name="S&P 500"))
                             #mode='markers',
                             #marker=dict(size=5)))

    fig.write_html(functions.get_absolute_path("Resources/Results/Plots/portfolio_vs_index.html"))
    fig.show()

    # trades and positions
    ax = states.plot(x="date", y="trades", figsize=(15, 7))
    states.plot(x="date", y="positions", ax=ax)
    plt.savefig(functions.get_absolute_path("Resources/Results/Plots/TradesAndPositions.png"))

    # portfolio returns
    hist_figure = px.histogram(trades, x="returns", nbins=round(trades.shape[0] / 1.5))
    hist_figure.write_image(functions.get_absolute_path("Resources/Results/Plots/Returns.png"))
    #hist_figure.show()

def plot_indices():
    path = functions.get_absolute_path("Resources/Data/BacktestData/")
    dir_list = os.listdir(path)
    files_list = [name for name in dir_list if "index" in name.split("_")[1]]

    fig = go.Figure()

    for file in files_list:
        label = f"{file.split('_')[0]}"
        exchange_index = pd.read_csv(path+file, sep=",")
        exchange_index["index"] = exchange_index["index"]/exchange_index["index"].iloc[0]
        fig.add_trace(go.Scatter(x=exchange_index["date"],
                                 y=exchange_index["index"],
                                 name=label))

    fig.write_html(functions.get_absolute_path("Resources/Results/Plots/index_comparison.html"))
    fig.show()
if __name__ == "__main__":
    portfolio_states, trade_log = load_logs()
    create_plots(portfolio_states, trade_log)
    #plot_indices()