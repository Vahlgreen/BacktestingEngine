import yfinance as yf
import os
import pandas as pd


script_directory = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(script_directory, "../Data/DeprecatedData/s&pTickers.csv")


tickers= pd.read_csv(data_file)
tickers = tickers["TICKERS"].to_list()

data_file = os.path.join(script_directory, "../Data/TickerData/")
for ticker in tickers:
    # Downloads historical market data from Yahoo Finance for the specified ticker.
    # The period ('prd') and interval ('intv') for the data are specified as string variables.
    data = yf.download(ticker, group_by="Ticker",interval = "1d",start="2000-01-01",end="2024-04-02",actions=True,repair=True,keepna=True)

    # Adds a new column named 'ticker' to the DataFrame. This column is filled with the ticker symbol.
    # This step is helpful for identifying the source ticker when multiple DataFrames are combined or analyzed separately.
    data['ticker'] = ticker

    # Saves the DataFrame to a CSV file. The file name is dynamically generated using the ticker symbol,
    # allowing each ticker's data to be saved in a separate file for easy access and identification.
    # For example, if the ticker symbol is 'AAPL', the file will be named 'ticker_AAPL.csv'.
    data.to_csv(data_file+f'ticker_{ticker}.csv')

from pathlib import Path

# Create a Path object 'p' that represents the directory containing the CSV files
p = Path(data_file)

# Use the .glob method to create an iterator over all files in the 'p' directory that match the pattern 'ticker_*.csv'.
# This pattern will match any files that start with 'ticker_' and end with '.csv', which are presumably files containing ticker data.
files = p.glob('ticker_*.csv')

# Read each CSV file matched by the glob pattern into a separate pandas DataFrame, then concatenate all these DataFrames into one.
# The 'ignore_index=True' parameter is used to reindex the new DataFrame, preventing potential index duplication.
# This results in a single DataFrame 'df' that combines all the individual ticker data files into one comprehensive dataset.
df = pd.concat([pd.read_csv(file) for file in files], ignore_index=True)

print("")









# #YYYY-MM-DD
# data = yf.download(tickers,interval = "1d",start="2000-01-01",end="2024-04-02",actions=True,repair=True,keepna=True,group_by = "ticker")
#
# data_file = os.path.join(script_directory, "../Data/RawBacktestData.csv")
# data.to_csv(data_file,sep=",",header=False)
# print("")