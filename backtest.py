# Libraries
import time
import pandas as pd
import numpy as np

# project files
import functions
from portfolio import Portfolio
from parameters import data_provider, ticker_list
def main():
    main_timer = time.time()
    # Initiate backtest parameters
    backtest_data_path = functions.get_absolute_path(f"Resources/Data/BacktestData/{data_provider}_historical_data.csv")
    index_data_path =  functions.get_absolute_path(f"Resources/Data/BacktestData/{data_provider}_index.csv")

    backtest_data = get_backtest_data(backtest_data_path)
    start_date = "2001-01-03"
    end_date = str(backtest_data.last_valid_index())

    portfolio = Portfolio(start_date, end_date,funds=50000)

    # Structure data
    ticker_data, market_days = structure_input_data(backtest_data, start_date, ticker_list)

    # Run backtest
    for i, date in enumerate(market_days):
        timer = time.time()
        run_backtest(portfolio,date,end_date,ticker_data)
        if i % 10 == 0:
            print(f"Backtesting.. Simulation {i + 1} of {len(market_days)}")
        #print(time.time()-timer)

    # Log comparable index in the selected backtest time frame
    log_index(start_date, end_date, index_data_path)

    # logs results
    portfolio.log_back_test_results(ticker_data, end_date)

    print(f"backtest duration: {(time.time() - main_timer)/60} minutes)")

def run_backtest(portfolio: Portfolio, start_date: str, end_date: str, ticker_data: dict) -> None:
    pool = {}
    # loop through symbols
    for stock_ticker,stock_data in ticker_data.items():

        current_price = stock_data.at[start_date, "Open"]

        #if price is nan and in holding it means the stock is delisted. sell at entry price
        if pd.isna(current_price):
            if stock_ticker in portfolio.open_trades:
                portfolio.sell(stock_ticker, portfolio.open_trades[stock_ticker].entry_price, start_date)
            continue

        # Deploy strategy
        if stock_ticker in portfolio.open_trades:
            if strategy(stock_data, current_price, start_date, portfolio, stock_ticker, "sell"):
                portfolio.sell(stock_ticker, current_price, start_date)

        else:
            if strategy(stock_data, current_price, start_date, portfolio, stock_ticker, "buy"):
                pool.update({stock_ticker:current_price})

    # If the pool is not empty we process and buy
    if len(pool)>0:
        # Maintain equal risk. divide investment equally among stocks to trade.
        fund_proportion = portfolio.funds / len(pool)
        for stock_ticker, current_price in pool.items():
            position_size = int(fund_proportion/current_price)
            if position_size > 0 and portfolio.funds >= current_price * position_size:
                portfolio.buy(stock_ticker, position_size, current_price, start_date)



    portfolio.log_portfolio_state(ticker_data, start_date)

def log_index(start_date: str, end_date: str, index_path: str) -> None:
    data = pd.read_csv(index_path, sep=",", index_col="date")
    log_path = functions.get_absolute_path(f"Resources/Results/index/{index_path.split('/')[-1]}")
    (data.loc[start_date:end_date, "index"] / data.loc[start_date, "index"]).to_csv(log_path, sep=",", header=False)

def get_backtest_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(path, sep=",", index_col="Date")
    if data.empty:
        raise Exception
    return data

def strategy(stock_history: pd.DataFrame, current_price: float, date: str, portfolio: Portfolio, ticker: str,
             flag: str) -> bool:
    # implements the trading strategy.
    if flag.lower() == "buy":

        # Filter2: short term moving average must be larger than long term moving average
        # define lookback dates
        lowerDate = functions.subtract_days(date, 20)
        upperDate = functions.subtract_days(date, 10)
        #functions

        filter2 = np.mean(stock_history.loc[lowerDate:date,"Open"].values) < np.mean(stock_history.loc[upperDate:date,"Open"].values)

        # Filter3: stocks with RSI>70 is considered over-saturated.

        # n = 14
        # rsi = 100 - (100 / (
        #          1 + stock_history["Open"].diff(1).mask(stock_history["Open"].diff(1) < 0, 0).ewm(alpha=1 / n, adjust=False).mean() /
        #          stock_history["Open"].diff(1).mask(stock_history["Open"].diff(1) > 0, -0.0).abs().ewm(alpha=1 / n,
        #                                                                                adjust=False).mean())).values[-1]
        #
        # filter3 = rsi < 70

        return  filter2 #and filter3

    elif flag.lower() == "sell":
        lowerDate = functions.subtract_days(date, 20)
        upperDate = functions.subtract_days(date, 10)
        filter2 = np.mean(stock_history.loc[lowerDate:date,"Open"].values) > np.mean(stock_history.loc[upperDate:date,"Open"].values)

        if filter2:
            return True

        elif current_price < portfolio.open_trades[ticker].entry_price * 0.8 or current_price > \
                portfolio.open_trades[ticker].entry_price * 1.5:
            return True
        else:
            return False
    else:
        raise Exception
def structure_input_data(data: pd.DataFrame, start_date: str, input_tickers: list) -> tuple:
    grouped_data = data.groupby("Ticker")
    available_tickers= list(set(data['Ticker'].values))
    ticker_data = {}

    if not isinstance(input_tickers,list):
        print("input tickers must be a list")
        raise Exception

    if len(input_tickers)==0:
        print("No input tickers")
        raise Exception

    if input_tickers[0].lower() == "all":
        if len(input_tickers)>1:
            print("Choose 'all' or specific tickers")
            raise Exception
        else:
            for key in available_tickers:
                    ticker_data.update({key: grouped_data.get_group(key)})
    else:
        for key in available_tickers:
            if key in input_tickers:
                ticker_data.update({key: grouped_data.get_group(key)})

    if len(ticker_data) == 0:
        print("No data found")
        raise Exception

    # Define market days
    # All tickers has well-defined index for the entire period. pick the first one
    temp_tick = list(ticker_data.keys())[0]
    market_days = data[data["Ticker"].values == "AAPL"].index
    try:
        market_days.get_loc(start_date)
    except Exception:
        print("Start date is not an open market day")

    market_days = market_days[market_days.get_loc(start_date):].tolist()

    return ticker_data, market_days

if (__name__ == "__main__"):
    main()
