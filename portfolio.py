import pandas as pd
import numpy as np

#Project files
import functions

class Portfolio:
    def __init__(self, start_date: str, end_date: str, funds: float = 100000.0):
        self.funds = funds
        self.start_date = start_date
        self.end_date = end_date
        self.open_trades = {}
        self.trade_history = []
        self.max_drawdown = 1
        self.portfolio_value_primo = funds
        self.portfolio_value = 0
        self.state_log = {}
        self.trade_log = {}
        self.transaction_fee = 0

    def sell(self, ticker: str, currentPrice: float, date: str) -> None:
        # Complete trade
        trade = self.open_trades[ticker].complete_trade(currentPrice, date)
        self.trade_history.append(trade)

        # Adjust funds
        self.funds = self.funds + currentPrice * self.open_trades[ticker].position_size - self.transaction_fee

        # Log trade
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

        # Adjust funds
        self.funds = self.funds - currentPrice * positionSize - self.transaction_fee

    def compute_portfolio_value(self, data: dict, date: str) -> None:
        # portfolio value includes funds (cash)
        # Uses today's price to compute portfolio value.
        self.portfolio_value = 0
        for key in self.open_trades:
            stock_data = data[key]
            currentPrice = stock_data.at[date, "Open"]
            self.portfolio_value += self.open_trades[key].position_size * currentPrice

        self.portfolio_value += self.funds


    def log_portfolio_state(self, data: dict, date: str) -> None:
        # Logs portfolio state each timestep
        #self.portfolio_value = self.compute_portfolio_value(data, date)
        self.compute_portfolio_value(data,date)
        asset_value = max(self.portfolio_value - self.funds, 0)

        self.max_drawdown = min(self.max_drawdown, self.portfolio_value / self.portfolio_value_primo)

        self.state_log.update({date:{
            "total_portfolio_value": round(self.portfolio_value),
            "asset_value": round(asset_value),
            "funds": round(self.funds),
            "number_of_trades": len(self.trade_history),
            "number_of_open_positions": len(self.open_trades)
        }})

    def log_back_test_results(self, stock_data: dict, date: str) -> None:
        # Summarizes backtest and prints to files
        nTrades = len(self.trade_history)
        nDays = functions.date_difference(self.start_date, self.end_date)
        risk_free_rate = 1.03**(nDays/252)-1
        portfolio_return = self.portfolio_value / self.portfolio_value_primo
        win_count = 0
        max_trade_duration = (0,"")
        list_of_returns = np.array([])
        list_of_losses = np.array([])
        list_of_profits = np.array([])

        # Compute tade-based statistics
        for trade in self.trade_history:
            if trade.win:
                win_count += trade.win
                list_of_profits = np.append(list_of_profits, trade.profit)
            else:
                list_of_losses = np.append(list_of_losses, trade.loss)

            if max_trade_duration[0] < trade.duration:
                max_trade_duration = (trade.duration,trade.ticker)
            list_of_returns = np.append(list_of_returns,trade.return_)




        average_profit = np.mean(list_of_profits)
        average_loss = np.mean(list_of_losses)

        # Sharpe and sortino ratios
        temp_df = pd.DataFrame(columns=["returns"],data=list_of_returns).pct_change()

        average_return= temp_df["returns"].mean()
        sharp_deviation = temp_df["returns"].std()

        temp_df_down = temp_df[temp_df["returns"]>0]
        sortino_deviation = temp_df_down["returns"].std()

        sharpeRatio = (average_return - risk_free_rate) / sharp_deviation
        sortinoRatio = (average_return - risk_free_rate) / sortino_deviation

        # Profit factor
        winRate = win_count / nTrades
        lossRate = 1 - winRate
        profitFactor = (winRate * average_profit) / (lossRate * average_loss)

        logString = f"Total portfolio return:            {round((portfolio_return-1)*100,1)}%\n" \
                    f"Average profit:                    ${round(average_profit)}\n" \
                    f"Average Profit var. coefficient:   {round(np.std(list_of_profits)/average_profit,1)}%\n"\
                    f"Average loss:                      ${round(average_loss)}\n" \
                    f"Average loss var. coefficient:     {round(np.std(list_of_losses)/average_loss,1)}%\n"\
                    f"Profit factor:                     {round(profitFactor,1)}\n" \
                    f"Max drawdown:                      {round((self.max_drawdown - 1) * 100, 1)}%\n" \
                    f"Win Rate:                          {round(winRate*100,1)}%\n" \
                    f"Sharpe Ratio:                      {round(sharpeRatio,1)}\n" \
                    f"Sortino Ratio:                     {round(sortinoRatio,1)}\n" \
                    f"Longest position held ({max_trade_duration[1]}):      {max_trade_duration[0]} days\n" \
                    f"Number of trades:                  {len(self.trade_history)}\n" \
                    f"Average trades pr day:             {round(len(self.trade_history) / nDays, 1)}"

        data_file = functions.get_absolute_path("Resources/Results/backtest_results.txt")
        with open(data_file, "w") as f:
            f.write(logString)
            f.close()

        data_file = functions.get_absolute_path("Resources/Results/portfolio_states.csv")
        logString = ""
        for date,state in self.state_log.items():
            logString += (f'{state["total_portfolio_value"]},{state["asset_value"]},{state["funds"]},{state["number_of_trades"]},'
                          f'{state["number_of_open_positions"]},{date}\n')
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

