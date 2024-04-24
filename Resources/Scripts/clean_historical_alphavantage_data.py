import os
import pandas as pd
import functions

def merge():
    backtest_path = functions.get_absolute_path("Resources/Data/ScrapedAlphaVantageData/")

    ticker_path = functions.get_absolute_path("Resources/Data/RawData/s&p_tickers.csv")
    tickers = pd.read_csv(ticker_path)
    tickers = tickers["TICKERS"].tolist()

    # tickers not present in data:
    missing_ticker_list = ['ESV', 'KFT', 'LTD', 'MHP', 'MOLX', 'NYX', 'JCP', 'PKI', 'TE', 'TSO', 'TMK', 'TYC', 'WPO', 'WPI', 'WIN']

    columns = ["timestamp","ticker", "open", "high", "low", "close", "volume"]
    print_df = pd.DataFrame(columns=columns)
    for ticker in tickers:
        if ticker not in missing_ticker_list:
            data = pd.read_csv(f"{backtest_path+ticker}.csv", sep=",")
            data = data.reindex(index=data.index[::-1])
            data["ticker"] = ticker
            if print_df.empty:
                print_df = data.copy()
            else:
                print_df = pd.concat([print_df, data])

    print_df=print_df.rename({"timestamp":"Date", "ticker":"Ticker", "open": "Open","close":"Close","volume":"Volume", "high":"High", "low":"Low"}, axis=1)
    path = functions.get_absolute_path("Resources/Data/RawData/alphavantage_historical_data.csv")
    print_df.to_csv(path,sep=",",index=False)

def clean():
    path = functions.get_absolute_path("Resources/Data/RawData/alphavantage_historical_data.csv")
    data = pd.read_csv(path,sep=",")
    grouped_data = data.groupby("Ticker", sort=False)

    tickers = data["Ticker"].unique().tolist()
    columns = ["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]

    cleaned_data = pd.DataFrame(columns=columns)

    #Dataframe to hold index
    example_ticker = "MMM"
    example_df = grouped_data.get_group(example_ticker)

    index_df = pd.DataFrame(columns = ["Date"])
    index_df["Date"] = example_df["Date"]
    nan_tickers = []

    for ticker in tickers:
        stock_data = grouped_data.get_group(ticker)
        temp_df = pd.DataFrame(columns=["Date"])
        temp_df["Date"] = example_df["Date"]
        temp_df = temp_df.merge(stock_data[columns], how="left", left_on='Date', right_on='Date')
        temp_df["Ticker"] = ticker

        index_df = index_df.merge(stock_data[["Open", "Date"]], how="left", left_on='Date', right_on='Date').rename({"Open":ticker},axis=1)
        nan_df = temp_df.Open.isnull().astype(int).groupby(temp_df.Open.notnull().astype(int).cumsum()).sum()[1:-1]

        if nan_df.sum()>0:
            # we have nans within range of data: interpolate
            nan_tickers.append(ticker)
            #WAG skal fikses
            if ticker == "WAG":
                continue
            temp_df = temp_df.interpolate(limit=5,limit_direction='both', limit_area='inside')
            temp_df["Ticker"] = ticker
        # Concat main dataframe
        cleaned_data = (temp_df.copy() if cleaned_data.empty else pd.concat([cleaned_data, temp_df]))
    path = functions.get_absolute_path("Resources/Data/BacktestData/alphavantage_index.csv")
    index_df["index"] = index_df.sum(axis=1,numeric_only=True)
    index_df = index_df.rename({"Date":"date"},axis=1)
    index_df[["index","date"]].to_csv(path,sep=",",index=False)

    path = functions.get_absolute_path("Resources/Data/BacktestData/alphavantage_historical_data.csv")
    #cleaned_data = cleaned_data.rename({"timestamp":"Date", "ticker":"Ticker", "open": "Open","close":"Close","volume":"Volume", "high":"High", "low":"Low"}, axis=1)
    cleaned_data.to_csv(path,sep=",",index=False)
if __name__ == "__main__":
    #merge()
    clean()