# Libraries
import time
import pandas as pd
import numpy as np

# project files
import functions
from portfolio import Portfolio
from parameters import data_provider, ticker_list, start_date, initial_funds, transaction_fee
from indicators import rsi, moving_average, bollinger_bands, dmi_, chaikin_volatility

def main():
    main_timer = time.time()

    # Initiate backtest parameters
    backtest_data = get_backtest_data()
    end_date = str(backtest_data.last_valid_index())
    portfolio = Portfolio(start_date, end_date, funds=initial_funds, transaction_fee=transaction_fee)

    # Structure data
    ticker_data, market_days = structure_input_data(backtest_data, start_date, ticker_list)

    # Run backtest
    for i, date in enumerate(market_days, start=1):
        timer = time.time()
        run_backtest(portfolio,date,ticker_data)
        if i % 100 == 0:
            print(f"Backtesting.. Simulation {i} of {len(market_days)}")
        #print(time.time()-timer)

    # Log comparable index in the backtest time frame
    log_index(start_date, end_date)

    # Log results
    portfolio.log_back_test_results()

    print(f"backtest duration: {round((time.time() - main_timer)/60,2)} minutes")


def run_backtest(portfolio: Portfolio, current_date: str, ticker_data: dict):
    pool = {}
    # loop through symbols
    for stock_ticker,stock_data in ticker_data.items():

        current_price = stock_data.at[current_date, "Open"]
        # if price is nan and in holding it means the stock is delisted. sell at entry price
        if pd.isna(current_price):
            if stock_ticker in portfolio.open_trades:
                portfolio.sell(stock_ticker, portfolio.open_trades[stock_ticker].entry_price, current_date)
            continue

        # Deploy strategy
        strategy(stock_data, stock_ticker, current_date, portfolio, current_price, pool)

    if len(pool)>0:
        sorted_pool_tickers = sorted(pool, key=lambda x: pool[x]['dmi'], reverse=True)
        num_tickers = min(3,len(pool))
        # Assign equal equity to all candidates. Use kelly criteria to decide final assigned equity

        p = functions.mean_list(portfolio.winrate[-min(14,len(portfolio.winrate)):])
        assigned_equity = (p*portfolio.funds*portfolio.risk_tolerance) / num_tickers
        for i in range(num_tickers):
            ticker = sorted_pool_tickers[i]
            current_price = pool[ticker]["current_price"]
            position_size = int(assigned_equity/ current_price)
            if position_size > 0 and portfolio.funds >= current_price * position_size:
                portfolio.buy(ticker, position_size, current_price, current_date)

    portfolio.update_and_log(ticker_data, current_date)
def strategy(stock_history: pd.DataFrame, stock_ticker: str, current_date: str, portfolio: Portfolio, current_price: float, pool: dict):
    # implements the trading strategy.

    buy_signal = False
    if moving_average(stock_history, current_date):
        if rsi(stock_history, current_date):
            buy_signal = True

        # if bollinger_bands(stock_history,current_date):
        #     if chaikin_volatility(stock_history,current_date):
        #         if rsi(stock_history,current_date):
        #             if dmi_(stock_history,current_date):
        #

    # if ticker is in holdings check sell condition, otherwise check buy condition
    if stock_ticker in portfolio.open_trades:
        if portfolio.open_trades[stock_ticker].stop_loss > current_price:
            portfolio.sell(stock_ticker, current_price, current_date)
        elif not buy_signal:
            portfolio.sell(stock_ticker, current_price, current_date)
    else:
        if buy_signal:
            dmi = functions.directional_movement_index(stock_history,14,current_date)
            pool.update({stock_ticker: {"current_price":current_price, "dmi": dmi[-1]}})
            #pool.update({stock_ticker:current_price})
def structure_input_data(data: pd.DataFrame, s_date: str, input_tickers: list) -> tuple:
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
    # All tickers has well-defined index for the entire period. pick the first one
    temp_tick = list(ticker_data.keys())[0]
    market_days = data[data["Ticker"].values == "AAPL"].index
    try:
        market_days.get_loc(s_date)
    except Exception:
        print("Start date is not an open market day")

    market_days = market_days[market_days.get_loc(s_date):].tolist()

    return ticker_data, market_days
def log_index(s_date: str, end_date: str):
    path = functions.get_absolute_path(f"Resources/Data/BacktestData/{data_provider}_index.csv")
    data = pd.read_csv(path, sep=",", index_col="date")
    log_path = functions.get_absolute_path(f"Results/index/{path.split('/')[-1]}")
    (data.loc[s_date:end_date, "index"] / data.loc[s_date, "index"]).to_csv(log_path, sep=",", header=False)
def get_backtest_data() -> pd.DataFrame:
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
