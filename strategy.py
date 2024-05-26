# Libraries
import pandas as pd
from abc import ABC, abstractmethod

# Project files
import functions
from indicators import rsi, moving_average, bollinger_bands, dmi_, chaikin_volatility

class BaseStrategy(ABC):
    """ Parent strategy class. Portfolio object can contain multiple strategies."""

    # Specify which tickers the strategy is implemented for
    tickers: list[str]
    def deploy(self,portfolio, ticker_data: dict, current_date: str):
        pool = {}
        for stock_ticker, stock_data in ticker_data.items():

            if stock_ticker in self.tickers or self.tickers[0].lower() == "all":

                current_price = stock_data.at[current_date, "Open"]

                # If price is nan and in holding it means the stock is delisted. sell at entry price
                if pd.isna(current_price):
                    if stock_ticker in portfolio.open_trades:
                        portfolio.sell(stock_ticker, portfolio.open_trades[stock_ticker].entry_price, current_date)
                    continue

                # Check stop-loss tricker
                if stock_ticker in portfolio.open_trades:
                    if portfolio.open_trades[stock_ticker].stop_loss > current_price:
                        portfolio.sell(stock_ticker, current_price, current_date)

                    elif self.get_sell_signal(current_date,stock_data):
                        portfolio.sell(stock_ticker, current_price, current_date)
                else:
                    # If buy signal is true we add the ticker to the pool of candidates
                    if self.get_buy_signal(current_date, stock_data):
                        pool = self.compute_order_key(pool, stock_data, current_date, current_price, stock_ticker)

        if len(pool) > 0:
            sorted_candidates = self.order_candidates(portfolio, current_date, pool)
            num_tickers = min(3, len(pool))

            # Assign equal equity to all candidates. Use kelly criteria to decide final assigned equity
            p = functions.mean_list(portfolio.winrate[-min(14, len(portfolio.winrate)):])
            assigned_equity = (p * portfolio.funds * portfolio.risk_tolerance) / num_tickers

            for i in range(num_tickers):
                ticker = sorted_candidates[i]
                current_price = pool[ticker]["current_price"]
                position_size = int(assigned_equity / current_price)

                if position_size > 0 and portfolio.funds >= current_price * position_size:
                    portfolio.buy(ticker, position_size, current_price, current_date)

    @staticmethod
    @abstractmethod
    def compute_order_key(pool: dict, stock_data: pd.DataFrame, current_date: str, current_price: float, stock_ticker):
        pass
    @staticmethod
    @abstractmethod
    def get_buy_signal(current_date: str, stock_data: pd.DataFrame) -> bool:
        pass
    @staticmethod
    @abstractmethod
    def get_sell_signal(current_date: str, stock_data: pd.DataFrame) -> bool:
        pass
    @staticmethod
    @abstractmethod
    def order_candidates(portfolio, current_date: str, pool: dict) -> dict:
        pass

class SimpleMomentum(BaseStrategy):

    tickers = ["all"]
    @staticmethod
    def get_buy_signal(current_date: str, stock_data: pd.DataFrame) -> bool:
        signal = False
        if moving_average(stock_data, current_date):
            if rsi(stock_data, current_date):
                signal = True
        return signal
    @staticmethod
    def get_sell_signal(current_date: str, stock_data: pd.DataFrame) -> bool:
        signal = False
        if not moving_average(stock_data, current_date):
            if not rsi(stock_data, current_date):
                signal = True
        return signal
    @staticmethod
    def compute_order_key(pool: dict, stock_data: pd.DataFrame, current_date: str, current_price: float,
                          stock_ticker) -> dict:
        dmi = functions.directional_movement_index(stock_data, 14, current_date)
        pool.update({stock_ticker: {"current_price": current_price, "dmi": dmi[-1]}})
        return pool
    @staticmethod
    def order_candidates(portfolio, current_date: str, pool: dict) -> dict:
        return sorted(pool, key=lambda x: pool[x]['dmi'], reverse=True)



