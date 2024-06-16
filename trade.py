import numpy as np



class Trade:
    def __init__(self, entry_price: float, position_size: int, entry_date: str, ticker: str, stop_loss: float, strategy: str):
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
        self.strategy = strategy
        self.id = f"{ticker}-{strategy}"
    def complete_trade(self, current_price: float, exit_date: str):
        """Completes trade and returns trade object"""

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

