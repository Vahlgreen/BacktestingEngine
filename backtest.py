# Libraries
import time
import pandas as pd
import numpy as np

# project files
import functions
from portfolio import Portfolio
from parameters import data_provider
def main():
    main_timer = time.time()
    # Initiate backtest parameters
    backtest_data_path = functions.get_absolute_path(f"Resources/Data/BacktestData/{data_provider}_historical_data.csv")
    index_data_path =  functions.get_absolute_path(f"Resources/Data/BacktestData/{data_provider}_index.csv")

    backtest_data = get_backtest_data(backtest_data_path)
    start_date = "2000-01-03"
    end_date = str(backtest_data.last_valid_index())

    portfolio = Portfolio(start_date, end_date,funds=50000)

    #structure data
    grouped_data = backtest_data.groupby("Ticker")
    tickers= list(set(backtest_data['Ticker'].values))
    ticker_data = {}
    for key in tickers:
        ticker_data.update({key:grouped_data.get_group(key)})

    #{key:value for (key,value) in dictonary.items()}

    #Define market days
    temp = backtest_data[backtest_data["Ticker"].values == "MMM"].index
    try:
        temp.get_loc(start_date)
    except Exception:
        print("Start date is not an open market day")

    market_days = temp[temp.get_loc(start_date):].tolist()

    # Run backtest
    for i, date in enumerate(market_days):
        #timer = time.time()
        run_backtest(backtest_data, portfolio, date,ticker_data)
        if i % 10 == 0:
            print(f"Backtesting.. Simulation {i + 1} of {len(market_days)}")
        #print(time.time()-timer)


    # Log comparable index in the selected backtest time frame
    log_index(start_date, end_date, index_data_path)
    # logs results
    portfolio.log_back_test_results()
    print(f"backtest duration: {(time.time() - main_timer)/60} minutes)")
def run_backtest(data: pd.DataFrame, portfolio: Portfolio, date: str, ticker_data: dict) -> None:
    pool = {}
    # loop through symbols
    #Todo: somehow only parse the indicies between start date and end date
    for stock_ticker,stock_data in ticker_data.items():
        #locate stock data
        current_price = stock_data.at[date, "Open"]

        if pd.isna(current_price):
            #TODO: take loss if stock is in holdings
            if stock_ticker in portfolio.open_trades:
                portfolio.sell(stock_ticker, portfolio.open_trades[stock_ticker].entry_price, date)

            continue

        # Deploy strategy
        if stock_ticker in portfolio.open_trades:
            if strategy(stock_data, current_price, date, portfolio, stock_ticker, "sell"):
                portfolio.sell(stock_ticker, current_price, date)

        else:
            if strategy(stock_data, current_price, date, portfolio, stock_ticker, "buy"):
                pool.update({stock_ticker:current_price})

    # If the pool is not empty we process and buy
    if len(pool)>0:
        # Todo: Don't use 100% of available funds by default
        # maintain equal risk. divide investment equally among stocks to trade. divide price of the stock into that portion
        fund_proportion = portfolio.funds / len(pool)
        for stock_ticker, current_price in pool.items():
            position_size = int(fund_proportion/current_price)
            if position_size > 0 and portfolio.funds >= current_price * position_size:
                portfolio.buy(stock_ticker, position_size, current_price, date)

    portfolio.log_portfolio_state(ticker_data,date)

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

        # look-back period
        n = 14
        # rsi = 100 - (100 / (
        #         1 + stock_history["Open"].diff(1).mask(stock_history["Open"].diff(1) < 0, 0).ewm(alpha=1 / n, adjust=False).mean() /
        #         stock_history["Open"].diff(1).mask(stock_history["Open"].diff(1) > 0, -0.0).abs().ewm(alpha=1 / n,
        #                                                                               adjust=False).mean())).values[-1][0]

        # filter3 = rsi < 70

        return  filter2

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

if (__name__ == "__main__"):
    main()
