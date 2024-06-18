import pandas as pd
import numpy as np
import os
import glob

#Project files
import functions
import strategy

class Portfolio:
    def __init__(self, start_date: str, end_date: str,strategies: list, funds: float, transaction_fee: float, risk_tolerance: float = 0.5):
        self.funds = funds
        self.asset_value = 0
        self.start_date = start_date
        self.end_date = end_date
        self.max_drawdown = 1
        self.portfolio_value_primo = funds
        self.portfolio_value = 0
        self.transaction_fee = transaction_fee
        self.transaction_expenses = 0
        self.strategies = [getattr(strategy, name)(funds=funds, name=name, strats=strategies) for name in strategies] # instantiate strategy objects
        self.winrate = [1]                     # Current winrate. Avoid collapsing the kelly criteria by appending 1
        self.returns = []                      # List of average, daily returns
        self.state_log = {}                    # Portfolio states, updates every trade day
        self.risk_tolerance = risk_tolerance   # Ratio of total equity assigned to trading

    def deploy_strategies(self,ticker_data: dict, current_date: str):
        """Deploys all strategies associated with the portfolio"""

        for strat in self.strategies:
            strat.deploy(self,ticker_data,current_date)
    def update_and_log(self, data: dict, current_date: str):
        """Updates parameters after each trade day."""

        # Offload all open positions on end date for logging purposes
        if current_date == self.end_date:
            for strat_object in self.strategies:
                # We can't iterate over open_trades since the sell function deletes elements during iteration
                remaining_trades = list(strat_object.open_trades.keys())
                for ticker in remaining_trades:
                    stock_data = data[ticker]
                    current_price = stock_data.at[current_date, "Open"]

                    strat_object.sell(ticker,current_price,current_date)

        for strat_obj in self.strategies:
            strat_obj.update_parameters(data, current_date)

        # The order of function calls are of importance here
        self.update_portfolio_value(data, current_date)
        self.update_max_drawdown()
        self.update_returns_and_winrate(current_date)
        self.update_risk_tolerance()
        self.log_portfolio_state(current_date)
    def update_portfolio_value(self, data: dict, current_date: str):
        """
        portfolio value is the sum of current holdings value and funds of the underlying strategies
        """
        self.asset_value = 0
        self.funds = 0

        for strat_object in self.strategies:
            self.asset_value += strat_object.asset_value
            self.funds += strat_object.funds

        self.portfolio_value = self.funds + self.asset_value
    def update_max_drawdown(self):
        """Updates max drawdown"""
        self.max_drawdown = min(self.max_drawdown, self.portfolio_value / self.portfolio_value_primo)
    def update_returns_and_winrate(self, current_date):

        avg_return = 0
        avg_winrate = 0
        for strategy_object in self.strategies:
            avg_return += strategy_object.returns[-1]
            avg_winrate += strategy_object.win_rate[-1]

        self.returns.append(avg_return/len(self.strategies))
        self.winrate.append(avg_winrate/len(self.strategies))
    def update_risk_tolerance(self):
        """Updates risk_tolerance based on returns in the past "look_back_period" days"""

        look_back_period = 10
        # We don't update at the risk tolerance for the first "look_back_period" days of the backtest
        if len(self.returns) >= look_back_period:
            avg_return = functions.mean_list(self.returns[-look_back_period:])
            if avg_return >= 1:
                self.risk_tolerance = min(self.risk_tolerance + np.log(avg_return) / 10, 1)
            else:
                self.risk_tolerance = max(self.risk_tolerance + np.log(avg_return) / 10, 0.2)
    def log_portfolio_state(self, date: str):
        """Logs portfolio and strategy state each day"""

        self.state_log.update({date:{
            "total_portfolio_value": round(self.portfolio_value),
            "asset_value": round(self.asset_value),
            "funds": round(self.funds),
            "risk_tolerance": round(self.risk_tolerance,4),
            "return": round(self.returns[-1],4),
            "win_rate": round(functions.mean_list(self.winrate[-min(14, len(self.winrate)):]),4),
            "number_of_trades": sum([len(strat.all_trades) for strat in self.strategies]),
            "number_of_open_positions": sum([len(strat.open_trades) for strat in self.strategies])
        }})

    def log_back_test_results(self):
        """Summarizes backtest and prints to files"""

        # Delete all existing files before proceeding
        files = os.listdir("Results/Strategies/")
        yearly_risk_free_rate = 1.04
        for f in files:
            os.remove(f"Results/Strategies/{f}")

        num_days = np.busday_count(self.start_date, self.end_date)
        for strat in self.strategies:

            num_trades = len(strat.all_trades)


            # All remaining holdings have been sold off
            strat_return = strat.funds/strat.primo_funds


            # Aggregate returns on a day-basis for sharpe
            sharpe_dates = []
            sharpe_returns = []

            win_count = 0
            max_trade_duration = {
                "Duration": 0,
                "Ticker": ""
            }
            list_of_losses = []
            list_of_profits = []

            # Compute trade-based statistics
            for trade in strat.all_trades:
                if trade.win:
                    win_count += trade.win
                    list_of_profits.append(trade.profit)
                    strat.win_count += 1
                else:
                    list_of_losses.append(trade.loss)

                if max_trade_duration["Duration"] < trade.duration:
                    max_trade_duration = {"Duration": trade.duration, "Ticker": trade.ticker}

                sharpe_dates.append(trade.exit_date.split("-")[0])
                sharpe_returns.append(trade.return_)

            average_profit = np.mean(list_of_profits)
            average_loss = np.mean(list_of_losses)

            # Computing sharpe ratio
            temp_df = pd.DataFrame(columns=["Years","Returns"],data=[])
            temp_df["Years"] = sharpe_dates
            temp_df["Returns"] = sharpe_returns
            temp_df_grouped = temp_df.groupby("Years")
            daily_returns = temp_df_grouped.mean()["Returns"].to_list()
            average_return = np.mean(daily_returns)
            sharpe_deviation = np.std(daily_returns)
            sharpe_ratio = (average_return - yearly_risk_free_rate) / sharpe_deviation

            # Profit factor
            win_rate = win_count / num_trades
            lossRate = 1 - win_rate
            profitFactor = (win_rate * average_profit) / (lossRate * average_loss)

            # For plotting purpose: The dataframe in dashhboard

            aggregated_backtest_results = {
                "Total return" : [f"{round((strat_return - 1) * 100, 1)}%"],
                "Average profit": [f"${round(average_profit)}"],
                "Average loss": [f"${round(average_loss)}"],
                "Profit factor": [round(profitFactor, 1)],
                "Average Profit var. coefficient": [f"{round(np.std(list_of_profits) / average_profit, 1)}%"],
                "Average loss var. coefficient": [f"{round(np.std(list_of_losses)/average_loss,1)}%"],
                "Max drawdown": [f"{round((strat.max_drawdown - 1) * 100, 1)}%"],
                "Win Rate": [f"{round(win_rate*100,1)}%"],
                "Sharpe Ratio": [round(sharpe_ratio,1)],
                "Longest position held": [f"{max_trade_duration['Duration']} days ({max_trade_duration['Ticker']})"],
                "Number of trades": [num_trades],
                "Average trades pr day": [round(num_trades / num_days, 1)]
            }

            print_df = pd.DataFrame.from_dict(data=aggregated_backtest_results,columns=["Results"],orient="index")
            print_df.index.name = "Metric"
            print_df.to_csv(functions.get_absolute_path(f"Results/Strategies/{strat.name}_backtest_results_df.csv"))


            data_file = functions.get_absolute_path(f"Results/Strategies/{strat.name}_states.csv")
            logString = "total_value,asset_value,funds,return,win_rate,trades,positions,date\n"
            for date, state in strat.state_log.items():
                logString += (f'{state["total_equity"]},{state["asset_value"]},'
                              f'{state["funds"]},{state["return"]},'
                              f'{state["win_rate"]},{state["number_of_trades"]},'
                              f'{state["number_of_open_positions"]},{date}\n')
            with open(data_file, "w") as f:
                f.write(logString)

            data_file = functions.get_absolute_path(f"Results/Strategies/{strat.name}_returns.csv")
            printList = [str(trade.return_) + "\n" for trade in strat.all_trades]
            with open(data_file, "w") as f:
                f.writelines(printList)

            data_file = functions.get_absolute_path(f"Results/Strategies/{strat.name}_trade_log.txt")
            logString = ""
            for date in strat.trade_log:
                logString = logString + f"{date}\n"
                for ticker, trade in strat.trade_log[date].items():
                    logString += f"ticker: {ticker}, Return: {trade.return_}, gain: {round(trade.gain)}, entry date: {trade.entry_date}, duration: {trade.duration}\n"
                logString += "\n"
            with open(data_file, "w") as f:
                f.write(logString)

        # Finally log results aggregated on entire portfolio



        portfolio_return = self.portfolio_value / self.portfolio_value_primo

        # Aggregate returns on a day-basis for sharpe
        sharpe_dates = []
        sharpe_returns = []

        win_count = 0
        max_trade_duration = {
            "Duration": 0,
            "Ticker": ""
        }

        list_of_losses = []
        list_of_profits = []

        # Compute trade-based statistics
        all_trades = []
        win_count = 0
        for strat in self.strategies:
            all_trades = all_trades+strat.all_trades

        num_trades = len(all_trades)

        for trade in all_trades:
            if trade.win:
                win_count += trade.win
                list_of_profits.append(trade.profit)
            else:
                list_of_losses.append(trade.loss)

            if max_trade_duration["Duration"] < trade.duration:
                max_trade_duration = {"Duration": trade.duration, "Ticker": trade.ticker}

            sharpe_dates.append(trade.exit_date.split("-")[0])
            sharpe_returns.append(trade.return_)

        average_profit = np.mean(list_of_profits)
        average_loss = np.mean(list_of_losses)

        # Computing sharpe ratio
        temp_df = pd.DataFrame(columns=["Years", "Returns"], data=[])
        temp_df["Years"] = sharpe_dates
        temp_df["Returns"] = sharpe_returns
        temp_df_grouped = temp_df.groupby("Years")
        daily_returns = temp_df_grouped.mean()["Returns"].to_list()
        average_return = np.mean(daily_returns)
        sharpe_deviation = np.std(daily_returns)
        sharpe_ratio = (average_return - yearly_risk_free_rate) / sharpe_deviation

        # Profit factor
        win_rate = win_count / num_trades
        lossRate = 1 - win_rate
        profitFactor = (win_rate * average_profit) / (lossRate * average_loss)

        # For plotting purpose: The dataframe in dashhboard

        aggregated_backtest_results = {
            "Total portfolio return": [f"{round((portfolio_return - 1) * 100, 1)}%"],
            "Average profit": [f"${round(average_profit)}"],
            "Average loss": [f"${round(average_loss)}"],
            "Profit factor": [round(profitFactor, 1)],
            "Average Profit var. coefficient": [f"{round(np.std(list_of_profits) / average_profit, 1)}%"],
            "Average loss var. coefficient": [f"{round(np.std(list_of_losses)/average_loss,1)}%"],
            "Max drawdown": [f"{round((self.max_drawdown - 1) * 100, 1)}%"],
            "Win Rate": [f"{round(win_rate*100,1)}%"],
            "Sharpe Ratio": [round(sharpe_ratio,1)],
            "Longest position held": [f"{max_trade_duration['Duration']} days ({max_trade_duration['Ticker']})"],
            "Number of trades": [num_trades],
            "Average trades pr day": [round(num_trades / num_days, 1)],
            "Transaction expenses": [f"${self.transaction_expenses} ({round(self.transaction_expenses/self.portfolio_value_primo,2)*100}% of initial funds)"]
        }

        print_df = pd.DataFrame.from_dict(data=aggregated_backtest_results,columns=["Results"],orient="index")
        print_df.index.name = "Metric"
        print_df.to_csv(functions.get_absolute_path("Results/Portfolio/backtest_results_df.csv"))



        data_file = functions.get_absolute_path("Results/Portfolio/portfolio_states.csv")
        logString = "total_value,asset_value,funds,return,win_rate,risk_tolerance,trades,positions,date\n"
        for date,state in self.state_log.items():
            logString += (f'{state["total_portfolio_value"]},{state["asset_value"]},'
                          f'{state["funds"]},{state["return"]},'
                          f'{state["win_rate"]},{state["risk_tolerance"]},{state["number_of_trades"]},'
                          f'{state["number_of_open_positions"]},{date}\n')
        with open(data_file, "w") as f:
            f.write(logString)


        data_file = functions.get_absolute_path("Results/Portfolio/returns.csv")
        printList = [str(trade.return_) + "\n" for trade in all_trades]
        with open(data_file, "w") as f:
            f.writelines(printList)


        # data_file = functions.get_absolute_path("Results/trade_log.txt")
        # logString = ""
        # for date in self.trade_log:
        #     logString = logString + f"{date}\n"
        #     for ticker, trade in self.trade_log[date].items():
        #         logString += f"ticker: {ticker}, Return: {trade.return_}, gain: {round(trade.gain)}, entry date: {trade.entry_date}, duration: {trade.duration}\n"
        #     logString += "\n"
        # with open(data_file, "w") as f:
        #     f.write(logString)

