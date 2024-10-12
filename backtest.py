# Libraries
import time
import pandas as pd
import numpy as np

# Project files
import functions
from portfolio import Portfolio
from parameters import backtest_parameters


def main():
    """Main module. Contains basic backtest logic"""

    main_timer = time.time()

    start_date = backtest_parameters["start_date"]
    strategies = backtest_parameters["strategies"]
    initial_funds = backtest_parameters["initial_funds"]
    transaction_fee = backtest_parameters["transaction_fee"]
    ticker_list = backtest_parameters["ticker_list"]
    data_provider = backtest_parameters["data_provider"]

    # Initiate backtest parameters
    backtest_data = get_backtest_data(data_provider)
    end_date = str(backtest_data.last_valid_index())
    portfolio = Portfolio(start_date, end_date, strategies=strategies, funds=initial_funds, transaction_fee=transaction_fee)

    # Structure data
    ticker_data, market_days = structure_input_data(backtest_data, start_date, ticker_list)

    # Run backtest
    for i, date in enumerate(market_days, start=1):

        portfolio.deploy_strategies(ticker_data,date)
        portfolio.update_and_log(ticker_data, date)

        if i % 100 == 0:
            print(f"Backtesting.. Simulation {i} of {len(market_days)}")


    # Log comparable index in the backtest time frame
    log_index(start_date, end_date, data_provider)

    # Log results
    portfolio.log_back_test_results()

    print(f"backtest duration: {round((time.time() - main_timer)/60,2)} minutes")
def structure_input_data(data: pd.DataFrame, s_date: str, input_tickers: list) -> tuple:
    """Validates input parameters and isolates tickers according to said parameters"""

    grouped_data = data.groupby("Ticker")
    available_tickers= list(pd.unique(data['Ticker'].values))
    ticker_data = {}

    if not isinstance(input_tickers,list):
        print("input tickers must be a list")
        raise Exception

    if len(input_tickers)==0:
        print("No input tickers")
        raise Exception

    if input_tickers[0].lower() == "all":
        if len(input_tickers)>1:
            print("Invalid parameter ticker_list")
            raise Exception
        else:
            for key in available_tickers:
                ticker_data.update({key: grouped_data.get_group(key)})
    elif input_tickers[0].lower() == "half":

        for i, key in enumerate(available_tickers, start=1):
            if i % 2 == 0:
                ticker_data.update({key: grouped_data.get_group(key)})
    else:
        for key in available_tickers:
            if key in input_tickers:
                ticker_data.update({key: grouped_data.get_group(key)})

    if len(ticker_data) == 0:
        print("No data found")
        raise Exception

    # Define market days
    market_days = pd.unique(data["Date"])
    try:
        idx = np.where(market_days==s_date)[0][0]
        market_days = market_days[idx:]
    except Exception:
        raise Exception("Start date is not an open market day")



    return ticker_data, market_days
def log_index(s_date: str, end_date: str, data_provider: str):
    """Logs index in the backtest time period"""

    path = functions.get_absolute_path(f"Resources/Data/BacktestData/{data_provider}_index.csv")
    data = pd.read_csv(path, sep=",", index_col="date")
    log_path = functions.get_absolute_path(f"Results/index/{path.split('/')[-1]}")
    (data.loc[s_date:end_date, "index"] / data.loc[s_date, "index"]).to_csv(log_path, sep=",", header=False)
def get_backtest_data(data_provider: str) -> pd.DataFrame:
    """Fetches backtest data"""

    path = functions.get_absolute_path(f"Resources/Data/BacktestData/{data_provider}_historical_data.csv")
    data = pd.read_csv(path, sep=",", index_col=False)
    data.index = data["Date"]
    if data.empty:
        raise Exception
    return data

if (__name__ == "__main__"):
    # Suppress/hide warnings
    np.seterr(invalid='ignore')
    main()
