import os
import pandas as pd
import functions

def clean_data():
    backtest_path = functions.get_absolute_path("Resources/Data/RawData/macrotrend_historical_data.csv")
    data = pd.read_csv(backtest_path, sep=",")
    ticker_path = functions.get_absolute_path("Resources/Data/RawData/s&p_tickers.csv")
    tickers = pd.read_csv(ticker_path)
    tickers = tickers["TICKERS"].tolist()

    # tickers not present in macrotrend data:
    missing_ticker_list = ['BMC', 'COH', 'CBE', 'CVH', 'HNZ', 'KFT', 'LTD', 'MHP', 'PCS', 'MOLX', 'NYX', 'PCLN', 'TSO',
                           'TIE', 'TYC', 'WAG', 'WPO', 'WPI', 'WLP', 'YHOO']


    columns = ["Date","Open", "High", "Low", "Close", "Volume", "Ticker"]
    data.columns = columns
    cleaned_data = pd.DataFrame(columns=columns)
    grouped_data = data.groupby("Ticker", sort=False)

    #We got a lot of different ranges for the indicies. By trial and error we try to find a
    #start date that doesn't exclude too many tickers. That is, we'll group all the data
    #into a predefined date range

    #These dates are well-defined for AAPL
    start_date = "2000-01-03"
    end_date = "2024-04-16"
    example_ticker = "AAPL"
    example_df = grouped_data.get_group(example_ticker)

    #isolate data in the selected timeframe
    start_index = example_df.index[example_df['Date'].values==start_date][0]
    end_index = example_df.index[example_df['Date'].values==end_date][0]
    example_df = example_df.loc[start_index:end_index, columns]

    #Dataframe to hold index
    index_df = pd.DataFrame(columns = ["Date"])
    index_df["Date"] = example_df["Date"]

    nan_tickers = []
    for ticker in tickers:
        if ticker not in missing_ticker_list:
            stock_data = grouped_data.get_group(ticker)
            temp_df = pd.DataFrame(columns=["Date"])
            temp_df["Date"] = example_df["Date"]
            temp_df = temp_df.merge(stock_data[columns], how="left", left_on='Date', right_on='Date')

            #skip if any nans. Try to repair some of these
            if temp_df["Open"].isnull().any():
                nan_tickers.append(ticker)
                continue

            #merge open price for index
            index_df = index_df.merge(stock_data[["Open","Date"]], how="left", left_on='Date', right_on='Date').rename({"Open":ticker},axis=1)
            #Concat main dataframe
            cleaned_data = (temp_df.copy() if cleaned_data.empty else pd.concat([cleaned_data, temp_df]))

            #cleaned_data.loc[pd.isna(cleaned_data['Open']), :].index
            #cleaned_data["Date"].to_list()[81]

    path = functions.get_absolute_path("Resources/Data/BacktestData/macrotrend_historical_data.csv")
    cleaned_data.to_csv(path, sep=",", index=False)

    path = functions.get_absolute_path("Resources/Data/BacktestData/macrotrend_index.csv")
    index_df["index"] = index_df.sum(axis=1,numeric_only=True)
    index_df = index_df.rename({"Date":"date"},axis=1)
    index_df[["index","date"]].to_csv(path,sep=",",index=False)

if __name__ == "__main__":
    clean_data()