import pandas as pd
import numpy as np

#Project files
import functions


class Portfolio:
    def __init__(self, start_date: str, end_date: str, funds: float = 100000.0, transaction_fee: float = 0.5, risk_tolerance: float = 0.5):
        self.funds = funds
        self.asset_value = 0
        self.start_date = start_date
        self.end_date = end_date
        self.max_drawdown = 1
        self.portfolio_value_primo = funds
        self.portfolio_value = 0
        self.transaction_fee = transaction_fee
        self.transaction_expenses = 0
        self.winrate = [1]                     # Current winrate. Avoid collapsing the kelly criteria by appending 1
        self.open_trades = {}                  # Currently open positions
        self.all_trades = []                   # List of all completed trades
        self.returns = []                      # List of average, daily returns
        self.state_log = {}                    # Portfolio states, updates every trade day
        self.trade_log = {}                    # Completed trades, aggregated on date
        self.risk_tolerance = risk_tolerance   # Ratio of total equity assigned to trading

    def sell(self, ticker: str, current_price: float, date: str):
        # Complete trade
        trade = self.open_trades[ticker].complete_trade(current_price, date)
        self.all_trades.append(trade)

        # Adjust funds
        self.funds = self.funds + current_price * self.open_trades[ticker].position_size

        # Log trade
        if date in self.trade_log:
            self.trade_log[date].update({ticker: trade})
        else:
            self.trade_log[date]={ticker: trade}

        # Remove asset from holdings
        del self.open_trades[ticker]
    def buy(self, ticker: str, position_size: int, current_price: float, date: str):
        # Opens new trade

        newTrade = _Trade(current_price, position_size, date, ticker, stop_loss=current_price*0.5)

        # Add trade to holdings
        self.open_trades[ticker] = newTrade

        # Adjust funds
        self.funds -= current_price * position_size - self.transaction_fee
        self.transaction_expenses += self.transaction_fee
    def update_and_log(self, data: dict, current_date: str):
        # Updates parameters after each trade day.

        # Sell all open positions on end date for logging purposes
        if current_date == self.end_date:
            # We can't iterate over open_trades since the sell function deletes elements from it
            remaining_tickers = list(self.open_trades.keys())
            for ticker in remaining_tickers:
                stock_data = data[ticker]
                current_price = stock_data.at[current_date, "Open"]
                self.sell(ticker,current_price,current_date)

        self.update_portfolio_value(data, current_date)
        self.update_asset_value()
        self.update_returns(current_date)
        self.update_risk_tolerance()
        self.update_max_drawdown()
        self.log_portfolio_state(current_date)
    def update_portfolio_value(self, data: dict, current_date: str):
        # portfolio value is the sum of current holdings value and funds

        self.portfolio_value = 0
        for key in self.open_trades:
            stock_data = data[key]
            current_price = stock_data.at[current_date, "Open"]
            self.portfolio_value += self.open_trades[key].position_size * current_price

        self.portfolio_value += self.funds
    def update_asset_value(self):
        self.asset_value = max(self.portfolio_value - self.funds, 0)
    def update_returns(self, current_date: str):
        # Logs average return of all trades that occurred that day.

        if len(self.trade_log.keys()) > 0:
            if current_date == list(self.trade_log.keys())[-1]:
                avg_return = np.mean([trade.return_ for _, trade in self.trade_log[current_date].items()])
                self.returns.append(avg_return)

                # update winrate
                win_rate = functions.mean_list([trade.win for _, trade in self.trade_log[current_date].items()])
                self.winrate.append(win_rate)
            else:
                # No trades completed today
                self.returns.append(1)
                win_rate = functions.mean_list(self.winrate[-min(14, len(self.winrate)):])
                self.winrate.append(win_rate)
        else:
            # No trades completed at all
            self.returns.append(1)
            self.winrate.append(0.5)
    def update_risk_tolerance(self):
        # Updates risk_tolerance based on returns in the past "look_back_period" days

        look_back_period = 3
        if len(self.returns) >= look_back_period:
            avg_return = functions.mean_list(self.returns[-look_back_period:])
            if avg_return >= 1:
                self.risk_tolerance = min(self.risk_tolerance + np.log(avg_return)/10,1)
            else:
                self.risk_tolerance = max(self.risk_tolerance + np.log(avg_return)/10, 0.2)
    def update_max_drawdown(self):
        self.max_drawdown = min(self.max_drawdown, self.portfolio_value / self.portfolio_value_primo)
    def log_portfolio_state(self, date: str):
        # Logs portfolio state each timestep

        self.state_log.update({date:{
            "total_portfolio_value": round(self.portfolio_value),
            "asset_value": round(self.asset_value),
            "funds": round(self.funds),
            "risk": round(self.risk_tolerance,4),
            "return": round(self.returns[-1],4),
            "win_rate": round(functions.mean_list(self.winrate[-min(14, len(self.winrate)):]),4),
            "number_of_trades": len(self.all_trades),
            "number_of_open_positions": len(self.open_trades)
        }})
    def log_back_test_results(self):
        # Summarizes backtest and prints to files

        num_trades = len(self.all_trades)
        num_days = np.busday_count(self.start_date, self.end_date)
        risk_free_rate = 1.03**(num_days/252)
        portfolio_return = self.portfolio_value / self.portfolio_value_primo
        win_count = 0
        max_trade_duration = {
            "Duration": 0,
            "Ticker": ""
        }

        list_of_losses = []
        list_of_profits = []

        #aggregate returns on a day-basis for sharpe
        sharpe_dates = []
        sharpe_returns = []
        # Compute trade-based statistics
        for trade in self.all_trades:
            if trade.win:
                win_count += trade.win
                list_of_profits.append(trade.profit)
            else:
                list_of_losses.append(trade.loss)

            if max_trade_duration["Duration"] < trade.duration:
                max_trade_duration = {"Duration": trade.duration, "Ticker": trade.ticker}

            sharpe_dates.append(trade.exit_date)
            sharpe_returns.append(trade.return_)

        average_profit = np.mean(list_of_profits)
        average_loss = np.mean(list_of_losses)

        temp_df = pd.DataFrame(columns=["Dates","Returns"],data=[])
        temp_df["Dates"] = sharpe_dates
        temp_df["Returns"] = sharpe_returns
        temp_df_grouped = temp_df.groupby("Dates")
        daily_returns = temp_df_grouped.mean()["Returns"].to_list()
        average_return = np.mean(daily_returns)
        sharpe_deviation = np.std(daily_returns)
        sharpe_ratio = (average_return - risk_free_rate) / sharpe_deviation

        # Profit factor
        winRate = win_count / num_trades
        lossRate = 1 - winRate
        profitFactor = (winRate * average_profit) / (lossRate * average_loss)

        logString = f"Total portfolio return:            {round((portfolio_return-1)*100,1)}%\n" \
                    f"Average profit:                    ${round(average_profit)}\n" \
                    f"Average loss:                      ${round(average_loss)}\n" \
                    f"Profit factor:                     {round(profitFactor, 1)}\n" \
                    f"Average Profit var. coefficient:   {round(np.std(list_of_profits) / average_profit, 1)}%\n" \
                    f"Average loss var. coefficient:     {round(np.std(list_of_losses)/average_loss,1)}%\n"\
                    f"Max drawdown:                      {round((self.max_drawdown - 1) * 100, 1)}%\n" \
                    f"Win Rate:                          {round(winRate*100,1)}%\n" \
                    f"Sharpe Ratio:                      {round(sharpe_ratio,1)}\n" \
                    f"Longest position held:             {max_trade_duration['Duration']} days ({max_trade_duration['Ticker']})\n" \
                    f"Number of trades:                  {num_trades}\n" \
                    f"Average trades pr day:             {round(num_trades / num_days, 1)}\n" \
                    f"Transaction expenses:              ${self.transaction_expenses} ({round(self.transaction_expenses/self.portfolio_value_primo,2)*100}% of initial funds)"

        data_file = functions.get_absolute_path("Results/backtest_results.txt")
        with open(data_file, "w") as f:
            f.write(logString)

        data_file = functions.get_absolute_path("Results/portfolio_states.csv")
        logString = "total_value,asset_value,funds,risk,return,win_rate,trades,positions,date\n"
        for date,state in self.state_log.items():
            logString += (f'{state["total_portfolio_value"]},{state["asset_value"]},'
                          f'{state["funds"]},{state["risk"]},{state["return"]},'
                          f'{state["win_rate"]},{state["number_of_trades"]},'
                          f'{state["number_of_open_positions"]},{date}\n')
        with open(data_file, "w") as f:
            f.write(logString)

        data_file = functions.get_absolute_path("Results/returns.csv")
        printList = [str(trade.return_) + "\n" for trade in self.all_trades]
        with open(data_file, "w") as f:
            f.writelines(printList)


        data_file = functions.get_absolute_path("Results/trade_log.txt")
        logString = ""
        for date in self.trade_log:
            logString = logString + f"{date}\n"
            for ticker, trade in self.trade_log[date].items():
                logString += f"ticker: {ticker}, Return: {trade.return_}, gain: {round(trade.gain)}, entry date: {trade.entry_date}, duration: {trade.duration}\n"
            logString += "\n"
        with open(data_file, "w") as f:
            f.write(logString)



class _Trade:
    def __init__(self, entry_price: float, position_size: int, entry_date: str, ticker: str, stop_loss: float):
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
        self.stop_loss = stop_loss

    def complete_trade(self, current_price: float, exit_date: str):
        self.exit_price = current_price
        self.exit_date = exit_date
        self.win = self.entry_price < self.exit_price
        if self.win:
            self.profit = (self.exit_price - self.entry_price) * self.position_size
        else:
            self.loss = (self.entry_price - self.exit_price) * self.position_size

        self.gain = (self.exit_price - self.entry_price) * self.position_size
        self.duration = np.busday_count(self.entry_date, self.exit_date)
        self.return_ = self.exit_price / self.entry_price
        return self

