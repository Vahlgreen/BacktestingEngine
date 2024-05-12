import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output


# project files
import functions
from parameters import data_provider
def load_logs() -> tuple:

    # Read logs
    # portfolio development
    data_file = functions.get_absolute_path("Results/portfolio_states.csv")
    portfolio_log = pd.read_csv(data_file, sep=",")
    portfolio_log["date"].apply(lambda x: x.split(" ")[0])
    portfolio_log["portfolio_index"] = portfolio_log["total_value"] / portfolio_log["total_value"].to_list()[0]
    portfolio_log["cummulative_returns"] = (portfolio_log["return"]-1).cumsum()

    # rolling statistics
    portfolio_log["moving_average"] = portfolio_log["portfolio_index"].rolling(window=50,min_periods=1).mean()
    portfolio_log["volatility"] = portfolio_log["portfolio_index"].rolling(window=50,min_periods=1).std().fillna(0)

    # Index for comparison
    data_file = functions.get_absolute_path(f"Results/Index/{data_provider}_index.csv")
    exchange_index = pd.read_csv(data_file, sep=",",names=["date","index"])

    # Create common dataframe
    portfolio_log["date"] = exchange_index["date"]
    portfolio_log["exchange_index"] = exchange_index["index"]

    #Returns are logged on a trade basis, and so the df has different length
    data_file = functions.get_absolute_path("Results/returns.csv")
    trade_returns = pd.read_csv(data_file, sep=",", names=["returns"])

    return portfolio_log, trade_returns

def create_figures(states: pd.DataFrame, trade_returns: pd.DataFrame) -> dict:

    # Create main plot. Portfolio index vs s&p 500
    portfolio_vs_index_fig = go.Figure()
    # portfolio
    portfolio_vs_index_fig.add_trace(go.Scatter(x=states["date"],
                             y=states["portfolio_index"],
                             name="Portfolio index",
                             line=dict(color="blue"),
                             customdata=states[["portfolio_index","total_value","asset_value", "funds","trades","positions","date"]],
                             hovertemplate=
                            "portfolio index: <b>%{customdata[0]}</b><br>" +
                            "total equity: <b>%{customdata[1]:$,.0f}</b><br>" +
                            "asset value: <b>%{customdata[2]:$,.0f}</b><br>" +
                            "funds: <b>%{customdata[3]:$,.0f}</b><br>" +
                            "trades: <b>%{customdata[4]}</b><br>" +
                            "positions: <b>%{customdata[5]}</b><br>" +
                            "date: <b>%{customdata[6]}</b><br>" +
                            "<extra></extra>"))
    portfolio_vs_index_fig.add_trace(go.Scatter(x=states["date"],
                             y=states["exchange_index"],
                             name="S&P 500",
                             line=dict(color="purple"),
                             hoverinfo='skip'))

    # moving average
    portfolio_vs_index_fig.add_trace(go.Scatter(x=states["date"],
                             y=states["moving_average"],
                             name="Moving average",
                             line=dict(color="grey"),
                             hoverinfo='skip'))

    portfolio_vs_index_fig.add_hline(y=states["portfolio_index"].max(), line_width=1.5, line_dash = "dash",line_color="green", name="peak")
    portfolio_vs_index_fig.add_hline(y=states["portfolio_index"].min(), line_width=1.5, line_dash="dash", line_color="red", name="Max drawdown")

    # confidence interval
    # portfolio_vs_index_fig.add_traces([go.Scatter(x=states["date"],
    #                            y=states["movingAverage"] - states["volatility"],
    #                            showlegend = False,
    #                            line_color = 'rgba(0,0,0,0)',
    #                            hoverinfo='skip'),
    #                go.Scatter(x=states["date"],
    #                           y=states["movingAverage"] + states["volatility"],
    #                           name = 'Volatility',
    #                           line_color='rgba(0,0,0,0)',
    #                           fill='tonexty', fillcolor = 'rgba(255, 0, 0, 0.2)',
    #                           hoverinfo='skip')])



    portfolio_vs_index_fig.write_html(functions.get_absolute_path("Results/Plots/portfolio_vs_index.html"))
    #portfolio_vs_index_fig.show()

    # risk and cummulative returns
    risk_cum_return_fig = make_subplots(specs=[[{"secondary_y": True}]])
    risk_cum_return_fig.add_trace(go.Scatter(x=states["date"],
                             y=states["cummulative_returns"],
                             name="Cummulative returns"))
    risk_cum_return_fig.add_trace(go.Scatter(x=states["date"],
                             y=states["risk"],
                             name="Risk"),secondary_y=True)
    risk_cum_return_fig.write_html(functions.get_absolute_path("Results/Plots/cum_returns_and_risk.html"))
    #risk_cum_return_fig.show()

    funds_and_asset_value_fig = go.Figure()
    funds_and_asset_value_fig.add_trace(go.Scatter(x=states["date"],
                             y=states["funds"],
                             name="Funds"))
    funds_and_asset_value_fig.add_trace(go.Scatter(x=states["date"],
                             y=states["asset_value"],
                             name="Asset value"))

    # positions
    positions_fig = go.Figure()
    positions_fig.add_trace(go.Scatter(x=states["date"],
                             y=states["positions"],
                             name="pos"))

    # portfolio returns
    hist_figure = px.histogram(trade_returns, x="returns", nbins=round(trade_returns.shape[0] / 1.5))
    hist_figure.write_html(functions.get_absolute_path("Results/Plots/Returns.html"))

    # winrate, risk and funds
    wr_risk_funds_fig = go.Figure()#make_subplots(specs=[[{"secondary_y": True}]])
    wr_risk_funds_fig.add_trace(go.Scatter(x=states["date"],
                             y=states["win_rate"],
                             name="Win rate", opacity = 0.25,line_dash = "dash"))
    wr_risk_funds_fig.add_trace(go.Scatter(x=states["date"],
                             y=states["risk"],
                             name="Risk", opacity = 0.25,line_dash = "dash"))
    wr_risk_funds_fig.add_trace(go.Scatter(x=states["date"],
                             y=states["risk"]*states["win_rate"],
                             name="Risk x Winrate",opacity = 0.75))

    return_dict = {
        "portfolio_vs_index_fig": portfolio_vs_index_fig,
        "risk_cum_return_fig": risk_cum_return_fig,
        "hist_figure": hist_figure,
        "funds_and_asset_value_fig": funds_and_asset_value_fig,
        "positions_fig": positions_fig,
        "wr_risk_funds_fig": wr_risk_funds_fig
    }

    return return_dict

def create_dashboard(figures: dict):

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    port_index = figures["portfolio_vs_index_fig"]
    risk_cum_return_fig= figures["risk_cum_return_fig"]
    hist_fig = figures["hist_figure"]
    funds_and_asset_value_fig = figures["funds_and_asset_value_fig"]
    positions_fig = figures["positions_fig"]
    wr_risk_funds_fig = figures["wr_risk_funds_fig"]

    # Charts
    app.layout = dbc.Container(
        [
            html.H1("Backtest Results"),

            # Charts
            dbc.Row(
                [
                    dbc.Col([dcc.Graph(figure=port_index)], width=12),
                ],justify="center",style={"height": "100%"}),
            dbc.Row(
                [
                    dbc.Col([dcc.Graph(figure=hist_fig)], width=12)
                ]),
            dbc.Row(
                [
                    dbc.Col([dcc.Graph(figure=risk_cum_return_fig)], width=12),
                ]),
            dbc.Row(
                [
                    dbc.Col([dcc.Graph(figure=funds_and_asset_value_fig)], width=12),
                ]),
            dbc.Row(
                [
                    dbc.Col([dcc.Graph(figure=positions_fig)], width=12),
                ]),
            dbc.Row(
                [
                    dbc.Col([dcc.Graph(figure=wr_risk_funds_fig)], width=12),
                ])
        ]
    )

    app.run_server(host="localhost", debug=True, use_reloader=False)
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

    fig.write_html(functions.get_absolute_path("Results/Plots/index_comparison.html"))
    fig.show()
if __name__ == "__main__":
    portfolio_states, trade_log = load_logs()
    figures = create_figures(portfolio_states, trade_log)
    create_dashboard(figures)
    #plot_indices()