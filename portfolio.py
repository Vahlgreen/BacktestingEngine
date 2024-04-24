import os
import pickle
import pandas as pd
from datetime import timedelta, datetime
import numpy as np

#Project files
import functions

#TODO: log top three stocks and associated results. Perhaps plot those equity curves

class Portfolio:
    def __init__(self, start_date: str, end_date: str, funds: float = 100000.0):
        self.funds = funds
        self.start_date = start_date
        self.end_date = end_date
        self.open_trades = {}
        self.trade_history = []
        self.max_drawdown = 1
        self.total_value_primo = funds
        self.total_value = funds
        self.state_log = []
        self.trade_log = {}
        self.transaction_fee = 0.5

    def sell(self, ticker: str, currentPrice: float, date: str) -> None:
        # Complete trade
        trade = self.open_trades[ticker].complete_trade(currentPrice, date)
        self.trade_history.append(trade)

        # adjust funds
        self.funds = self.funds + currentPrice * self.open_trades[ticker].position_size - self.transaction_fee

        # log trade
        if date in self.trade_log:
            self.trade_log[date].update({ticker: (trade.return_, trade.gain, trade.entry_date, trade.duration)})
        else:
            self.trade_log[date]={ticker: (trade.return_, trade.gain, trade.entry_date, trade.duration)}

        # Remove asset from holdings
        del self.open_trades[ticker]

    def buy(self, ticker: str, positionSize: int, currentPrice: float, date: str) -> None:
        # Trade object
        newTrade = _Trade(currentPrice, positionSize, date, ticker)

        # Add trade to holdings
        self.open_trades[ticker] = newTrade

        # adjust funds
        self.funds = self.funds - currentPrice * positionSize - self.transaction_fee

    def get_portfolio_value(self, data: dict, date: str) -> float:
        # portfolio value includes funds (cash)
        # Uses today's price to compute portfolio value.
        self.total_value = 0
        for key in self.open_trades:
            stock_data = data[key]
            currentPrice = stock_data.at[date, "Open"]
            self.total_value += self.open_trades[key].position_size * currentPrice

        return self.total_value + self.funds

    def log_portfolio_state(self, data: dict, date: str) -> None:
        # Logs portfolio state each timestep
        total_portfolio_value = self.get_portfolio_value(data, date)
        asset_value = max(total_portfolio_value - self.funds, 0)

        self.max_drawdown = min(self.max_drawdown, total_portfolio_value / self.total_value_primo)

        # Todo: Consider more appropriate datastructure
        self.state_log.append(
            (round(total_portfolio_value), round(asset_value), round(self.funds), len(self.trade_history), len(self.open_trades), date))

    def log_back_test_results(self) -> None:
        # Summarizes backtest and prints to files

        nTrades = len(self.trade_history)
        nDays = functions.date_difference(self.start_date, self.end_date)
        riske_free_rate = (1.03)**(nDays/365)-1
        portfolioReturn = (self.total_value + self.funds) / self.total_value_primo
        winCount = 0
        maxTradeDuration = (0,"")
        listOfReturns = np.array([])
        listOfLosses = np.array([])
        listOfProfits = np.array([])

        # Loop through trades and compute statistics
        for trade in self.trade_history:
            if trade.win:
                winCount += trade.win
                #maybe use combined average?
                listOfProfits = np.append(listOfProfits, trade.profit)
            else:
                listOfLosses = np.append(listOfLosses, trade.loss)

            # Todo: Consider currently open trades
            if maxTradeDuration[0] < trade.duration:
                maxTradeDuration = (trade.duration,trade.ticker)

            listOfReturns = np.append(listOfReturns, trade.return_-1)

        averageProfit = np.mean(listOfProfits)
        averageLoss = np.mean(listOfLosses)
        averageReturn = np.mean(listOfReturns)
        sharpDeviation = np.std(listOfReturns)
        sortinoDeviation = np.std(listOfReturns, where=listOfReturns < 1)

        sharpeRatio = (averageReturn - riske_free_rate) / sharpDeviation
        sortinoRatio = (averageReturn - riske_free_rate) / sortinoDeviation
        winRate = winCount / nTrades
        lossRate = 1 - winRate
        profitFactor = (winRate * averageProfit) / (lossRate * averageLoss)

        logString = f"Total portfolio return:            {round((portfolioReturn-1)*100,1)}%\n" \
                    f"Average profit:                    ${round(averageProfit)}\n" \
                    f"Average Profit var. coefficient:   {round(np.std(listOfProfits)/averageProfit,1)}%\n"\
                    f"Average loss:                      ${round(averageLoss)}\n" \
                    f"Average loss var. coefficient:     {round(np.std(listOfLosses)/averageLoss,1)}%\n"\
                    f"Profit factor:                     {round(profitFactor,1)}\n" \
                    f"Max drawdown:                      {round((self.max_drawdown - 1) * 100, 1)}%\n" \
                    f"Win Rate:                          {round(winRate*100,1)}%\n" \
                    f"Sharpe Ratio:                      {round(sharpeRatio,1)}\n" \
                    f"Sortino Ratio:                     {round(sortinoRatio,1)}\n" \
                    f"Longest position held ({maxTradeDuration[1]}):      {maxTradeDuration[0]} days\n" \
                    f"Number of trades:                  {len(self.trade_history)}\n" \
                    f"Average trades pr day:             {round(len(self.trade_history) / nDays, 1)}"

        data_file = functions.get_absolute_path("Resources/Results/backtest_results.txt")
        with open(data_file, "w") as f:
            f.write(logString)
            f.close()

        data_file = functions.get_absolute_path("Resources/Results/potfolio_states.csv")
        logString = ""
        for state in self.state_log:
            logString += f"{state[0]},{state[1]},{state[2]},{state[3]},{state[4]},{state[5]}\n"

        with open(data_file, "w") as f:
            f.write(logString)
            f.close()

        data_file = functions.get_absolute_path("Resources/Results/trade_returns.csv")
        printList = [str(trade.return_) + "\n" for trade in self.trade_history]
        with open(data_file, "w") as f:
            f.writelines(printList)
            f.close()

        data_file = functions.get_absolute_path("Resources/Results/trade_log.txt")
        logString = ""
        for date in self.trade_log:
            logString = logString + f"{date}\n"
            for ticker in self.trade_log[date]:
                info = self.trade_log[date][ticker]
                logString += f"ticker: {ticker} Return: {round(info[0],2)}, gain: {round(info[1])}, entry date: {info[2]}, duration: {info[3]}\n"
            logString += "\n"
        with open(data_file, "w") as f:
            f.write(logString)
            f.close()
class _Trade:
    def __init__(self, entry_price: float, position_size: int, entry_date: str, ticker: str):
        self.entry_price = entry_price
        self.position_size = position_size
        self.entry_date = entry_date
        self.ticker = ticker
        self.completed = False
        self.exit_price = 0
        self.exit_date = ""
        self.win = False
        self.duration = 0
        self.profit = 0
        self.loss = 0
        self.return_ = 0
        self.gain = 0

    def complete_trade(self, current_price: float, exit_date: str):
        self.exit_price = current_price
        self.exit_date = exit_date
        self.win = self.entry_price < self.exit_price
        if self.win:
            self.profit = (self.exit_price - self.entry_price) * self.position_size
        else:
            self.loss = (self.entry_price - self.exit_price) * self.position_size

        self.gain = (self.exit_price - self.entry_price) * self.position_size
        self.duration = functions.date_difference(self.entry_date, self.exit_date)
        self.return_ = self.exit_price / self.entry_price
        return self

