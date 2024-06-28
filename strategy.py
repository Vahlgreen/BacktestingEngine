# Libraries
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from trade import Trade

# Project files
import functions
from indicators import rsi, moving_average

class BaseStrategy(ABC):
    """ Parent strategy class. Portfolio object can contain multiple strategies."""

    # Specify which tickers the strategy is implemented for
    tickers: list[str]
    max_drawdown: float
    funds: float
    primo_funds: float
    asset_value: float
    name: str
    num_trades: int
    win_count: int
    win_rate: list  # Current winrate. Avoid collapsing the kelly criteria by appending 1
    open_trades: dict # Currently open positions
    all_trades: list  # List of all completed trades
    returns: list  # List of average, daily returns
    state_log: dict  # Portfolio states, updates every trade day
    trade_log: dict # Completed trades, aggregated on date

    def deploy(self,portfolio, ticker_data: dict, current_date: str):
        """Deploys trading strategy"""

        pool = {}
        for stock_ticker, stock_data in ticker_data.items():

            if stock_ticker in self.tickers or self.tickers[0].lower() == "all":

                current_price = stock_data.at[current_date, "Open"]

                # If price is nan and in holding it means the stock is delisted. sell at entry price
                if pd.isna(current_price):
                    if stock_ticker in self.open_trades:
                        self.sell(stock_ticker, self.open_trades[stock_ticker].entry_price, current_date)
                    continue

                # Check stop-loss tricker
                if stock_ticker in self.open_trades:
                    if self.open_trades[stock_ticker].stop_loss > current_price:
                        self.sell(stock_ticker, current_price, current_date)

                    elif self.get_sell_signal(current_date,stock_data,stock_ticker):
                        self.sell(stock_ticker, current_price, current_date)
                else:
                    # If buy signal is true we add the ticker to the pool of candidates
                    if self.get_buy_signal(current_date, stock_data,stock_ticker):
                        pool = self.compute_order_key(pool, stock_data, current_date, current_price, stock_ticker)

        # Evaluate pool of candidates
        if len(pool) > 0:
            sorted_candidates = self.sort_candidates(current_date, pool)
            num_tickers = min(3, len(pool))

            # Assign equal equity to all candidates. Final assigned equity is funds*winrate*risk_tolerance
            p = functions.mean_list(self.win_rate[-min(14, len(self.win_rate)):])
            assigned_equity = (p * self.funds * portfolio.risk_tolerance) / num_tickers

            for i in range(num_tickers):
                stock_ticker = sorted_candidates[i]
                current_price = pool[stock_ticker]["current_price"]
                position_size = int(assigned_equity / current_price)

                if position_size > 0 and self.funds >= current_price * position_size:
                    self.buy(portfolio,stock_ticker, position_size, current_price, current_date)
    def sell(self, stock_ticker: str, current_price: float, date: str):
        """Sells trade object and updates parameters"""
        # Complete trade
        trade = self.open_trades[stock_ticker].complete_trade(current_price, date)
        self.all_trades.append(trade)

        # Adjust funds
        self.funds = self.funds + current_price * self.open_trades[stock_ticker].position_size

        # Log trade
        if date in self.trade_log:
            self.trade_log[date].update({stock_ticker: trade})
        else:
            self.trade_log[date] = {stock_ticker: trade}

        # Remove asset from holdings
        del self.open_trades[stock_ticker]
    def buy(self, portfolio, stock_ticker: str, position_size: int, current_price: float, date: str):
        """Opens new trade and updates parameters"""

        trade_object = Trade(current_price, position_size, date, stock_ticker, stop_loss=current_price*0.5, strategy=self.name)

        self.open_trades[stock_ticker] = trade_object

        # Adjust funds
        self.funds -= current_price * position_size - portfolio.transaction_fee
        portfolio.transaction_expenses += portfolio.transaction_fee
    def update_parameters(self, data: dict, current_date: str):
        """Updates parameters each trade day. The order of function calls are of importance here"""

        self.update_asset_value(data, current_date)
        self.update_returns_and_winrate(current_date)
        self.update_max_drawdown()
        self.log_strategy_state(current_date)
    def log_strategy_state(self, date: str):
        """Logs parameters each trade day"""
        self.state_log.update({date:{
            "total_equity": round(self.asset_value+self.funds),
            "asset_value": round(self.asset_value),
            "funds": round(self.funds),
            "return": round(self.returns[-1],4),
            "win_rate": round(functions.mean_list(self.win_rate[-min(14, len(self.win_rate)):]),4),
            "number_of_trades": len(self.all_trades),
            "number_of_open_positions": len(self.open_trades)
        }})
    def update_asset_value(self, data: dict, current_date: str):
        """Computes asset value at 'current_date' price"""

        self.asset_value = 0
        for ticker in self.open_trades:
            stock_data = data[ticker]
            current_price = stock_data.at[current_date, "Open"]

            position_value = self.open_trades[ticker].position_size * current_price
            self.asset_value += position_value
    def update_returns_and_winrate(self, current_date):
        """Updates winrate and returns each trade day"""

        if len(self.trade_log.keys()) > 0:
            if current_date == list(self.trade_log.keys())[-1]:

                avg_return = np.mean([trade.return_ for _, trade in self.trade_log[current_date].items()])
                self.returns.append(avg_return)

                # Update winrate
                win_rate = functions.mean_list([trade.win for _, trade in self.trade_log[current_date].items()])
                self.win_rate.append(win_rate)
            else:
                # No trades completed that day
                self.returns.append(1)
                win_rate = functions.mean_list(self.win_rate[-min(14, len(self.win_rate)):])
                self.win_rate.append(win_rate)
        else:
            # No trades completed at all
            self.returns.append(1)
            self.win_rate.append(0.5)
    def update_max_drawdown(self):
        """Updates max drawdown"""

        self.max_drawdown = min(self.max_drawdown, (self.asset_value + self.funds) / self.primo_funds)

    @staticmethod
    @abstractmethod
    def compute_order_key(pool: dict, stock_data: pd.DataFrame, current_date: str, current_price: float, stock_ticker: str)-> dict:
        """
        Defines the key by which the pool of candidates are sorted by.
        The key should thus reflect the goodness of the candidate, e.g. by momentum or something else.
        """
        pass

    @abstractmethod
    def get_buy_signal(self,current_date: str, stock_data: pd.DataFrame,ticker: str) -> bool:
        """Logic that computes the buy signal"""
        pass

    @abstractmethod
    def get_sell_signal(self,current_date: str, stock_data: pd.DataFrame,ticker: str) -> bool:
        """Logic that computes the sell signal"""
        pass
    @staticmethod
    @abstractmethod
    def sort_candidates(current_date: str, pool: dict) -> dict:
        """Sorts the candidates based on key defined in 'compute_order_key'"""
        pass
class SimpleMomentum(BaseStrategy):
    """Basic momentum strategy used for testing"""
    def __init__(self, funds: float, name: str, strats: list[str]):
        self.tickers = ["all"]
        self.max_drawdown = 1
        self.funds = funds/len(strats)
        self.primo_funds = self.funds
        self.asset_value = 0
        self.returns = []
        self.state_log = {}
        self.name = name
        self.num_trades = 0
        self.win_count = 0
        self.win_rate = [1]
        self.open_trades = {}
        self.all_trades = []
        self.trade_log = {}


    def get_buy_signal(self,current_date: str, stock_data: pd.DataFrame, ticker: str) -> bool:
        signal = False
        if moving_average(stock_data, current_date):
            if rsi(stock_data, current_date):
                signal = True
        return signal

    def get_sell_signal(self,current_date: str, stock_data: pd.DataFrame, ticker: str) -> bool:
        signal = False

        if not moving_average(stock_data, current_date):
            if not rsi(stock_data, current_date):
                signal = True
        return signal
    @staticmethod
    def compute_order_key(pool: dict, stock_data: pd.DataFrame, current_date: str, current_price: float,
                          stock_ticker: str) -> dict:
        dmi = functions.directional_movement_index(stock_data, 14, current_date)
        pool.update({stock_ticker: {"current_price": current_price, "dmi": dmi[-1]}})
        return pool
    @staticmethod
    def sort_candidates(current_date: str, pool: dict) -> dict:
        return sorted(pool, key=lambda x: pool[x]['dmi'], reverse=True)
class StrategyAAPL(BaseStrategy):
    """Strategy applied to APPL ticker"""
    def __init__(self, funds: float, name: str, strats: list[str]):
        self.tickers = ["AAPL"]
        self.max_drawdown = 1
        self.funds = funds/len(strats)
        self.primo_funds = self.funds
        self.asset_value = 0
        self.returns = []
        self.state_log = {}
        self.name = name
        self.num_trades = 0
        self.win_count = 0
        self.win_rate = [1]
        self.open_trades = {}
        self.all_trades = []
        self.trade_log = {}

    def get_buy_signal(self,current_date: str, stock_data: pd.DataFrame, ticker: str) -> bool:
        signal = False

        current_date_index = np.where(stock_data["Date"].values == current_date)[0][0]
        data_open = functions.trim_stock_data(stock_data["Open"].values, current_date_index)

        if data_open[-7] < data_open[-1]:
            signal = True

        return signal

    def get_sell_signal(self,current_date: str, stock_data: pd.DataFrame, ticker: str) -> bool:
        signal = False

        current_date_index = np.where(stock_data["Date"].values == current_date)[0][0]

        data_open = functions.trim_stock_data(stock_data["Open"].values, current_date_index)
        data_close = functions.trim_stock_data(stock_data["Close"].values, current_date_index)
        data_high= functions.trim_stock_data(stock_data["High"].values, current_date_index)

        if data_close[-2] > data_open[-1] or data_high[-10]>data_high[-1]:
            signal = True

        return signal
    @staticmethod
    def compute_order_key(pool: dict, stock_data: pd.DataFrame, current_date: str, current_price: float,
                          stock_ticker: str) -> dict:
        dmi = functions.directional_movement_index(stock_data, 14, current_date)
        pool.update({stock_ticker: {"current_price": current_price, "dmi": dmi[-1]}})
        return pool
    @staticmethod
    def sort_candidates(current_date: str, pool: dict) -> dict:
        return sorted(pool, key=lambda x: pool[x]['dmi'], reverse=True)
class ImpliedVolatilityStrategy(BaseStrategy):
    """Trades only on implied volatility"""
    def __init__(self, funds: float, name: str, strats: list[str]):
        self.tickers = ["all"]
        self.max_drawdown = 1
        self.funds = funds/len(strats)
        self.primo_funds = self.funds
        self.asset_value = 0
        self.returns = []
        self.state_log = {}
        self.name = name
        self.num_trades = 0
        self.win_count = 0
        self.win_rate = [1]
        self.open_trades = {}
        self.all_trades = []
        self.trade_log = {}

    def get_buy_signal(self,current_date: str, stock_data: pd.DataFrame, ticker: str) -> bool:
        signal = False
        if moving_average(stock_data, current_date):
            if rsi(stock_data, current_date):
                signal = True
        return signal

    def get_sell_signal(self,current_date: str, stock_data: pd.DataFrame, ticker: str) -> bool:
        days_in_holding = np.busday_count(begindates=self.open_trades[ticker].entry_date,enddates=current_date)
        return days_in_holding>=30
    @staticmethod
    def compute_order_key(pool: dict, stock_data: pd.DataFrame, current_date: str, current_price: float,
                          stock_ticker: str) -> dict:

        vol = functions.volatility_coefficient(stock_data,current_date,look_back_period=100)

        pool.update({stock_ticker: {"current_price": current_price, "var_coef": vol}})

        return pool

    @staticmethod
    def sort_candidates(current_date: str, pool: dict) -> dict:
        return sorted(pool, key=lambda x: pool[x]['var_coef'], reverse=True)