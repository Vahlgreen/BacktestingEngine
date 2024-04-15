import yfinance as yf
import os
import pandas as pd
from pathlib import Path

script_directory = os.path.dirname(os.path.abspath(__file__))
#data_file = os.path.join(script_directory, "../Data/s&pTickers.csv")
data_file = os.path.join(script_directory, "../Data/DeprecatedData/selectedTickers.csv")

tickers = pd.read_csv(data_file)
tickers = tickers["TICKERS"].to_list()

data_file = os.path.join(script_directory, "../Data/TickerData/")

#Uncomment to download
# for ticker in tickers:
#     data = yf.Ticker(ticker).history(interval="1d", start="1950-01-01", end="2024-04-02", actions=True, repair=True,
#                                      keepna=True)
#     data[ticker] = data["Close"]
#     try:
#         data[ticker].to_csv(data_file + f'ticker_{ticker}.csv', header=True)
#     except Exception:
#         continue

dfOut = pd.DataFrame({})
p = Path(data_file)
files = p.glob('ticker_*.csv')

for i, file in enumerate(files):
    temp = pd.read_csv(file, header=0)
    if i == 0:
        dfOut["Date"] = temp["Date"]
    header = temp.columns[1]
    temp = temp[temp.columns[1]]
    dfOut[header] = temp

# The smart way that I totally gave up on
# df = pd.concat([pd.read_csv(file,header=0,index_col=False ) for file in files], ignore_index=True,axis=1)

dfOut.to_csv("../Data/RawBacktestData.csv", header=True)