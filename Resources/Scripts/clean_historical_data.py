import os
import pandas as pd
import functions
import numpy as np


def merge_alphavantage():
    # Assumes directory of datafiles with format {ticker_name}.csv
    backtest_path = functions.get_absolute_path("Resources/Data/ScrapedAlphaVantageData/")

    # tickers
    tickers = [name.replace(".csv","") for name in os.listdir(backtest_path)]


    # columns in downloaded data
    columns = ["timestamp","ticker", "open", "high", "low", "close", "volume"]
    print_df = pd.DataFrame(columns=columns)
    for ticker in tickers:
        data = pd.read_csv(f"{backtest_path+ticker}.csv", sep=",")

        #Turn data upside down for index purposes
        data = data.reindex(index=data.index[::-1])
        data["ticker"] = ticker
        if print_df.empty:
            print_df = data.copy()
        else:
            print_df = pd.concat([print_df, data])

    print_df=print_df.rename({"timestamp":"Date", "ticker":"Ticker", "open": "Open","close":"Close","volume":"Volume", "high":"High", "low":"Low"}, axis=1)
    path = functions.get_absolute_path("Resources/Data/RawData/alphavantage_historical_data.csv")
    print_df.to_csv(path,sep=",",index=False)
def clean_alphavantage():
    # Path to merged dataframe
    path = functions.get_absolute_path("Resources/Data/RawData/alphavantage_historical_data.csv")
    data = pd.read_csv(path,sep=",")
    end_date = "2024-04-19"
    data = data[data["Date"]<=end_date]
    grouped_data = data.groupby("Ticker", sort=False)

    tickers = data["Ticker"].unique().tolist()
    # columns of cleaned dataframe. Should be same format for all cleaned dataframes in this project
    columns = ["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]

    cleaned_data = pd.DataFrame(columns=columns)

    # Dataframe to hold index. MMM contains all indicies we want in final dataframe
    example_ticker = "MMM"
    example_df = grouped_data.get_group(example_ticker)

    index_df = pd.DataFrame(columns = ["Date"])
    index_df["Date"] = example_df["Date"]
    nan_tickers = []

    for ticker in tickers:
        stock_data = grouped_data.get_group(ticker)

        # Temp df holds data to be merged. That is, the dates of example_df. Merge data and manually inspect nans (missing days)
        temp_df = pd.DataFrame(columns=["Date"])
        temp_df["Date"] = example_df["Date"]
        temp_df = temp_df.merge(stock_data[columns], how="left", left_on='Date', right_on='Date')
        temp_df["Ticker"] = ticker

        # Merge open prices to index. Don't care about nans as we will sum all numeric values row wise
        index_df = index_df.merge(stock_data[["Open", "Date"]], how="left", left_on='Date', right_on='Date').rename({"Open":ticker},axis=1)

        # Nan_df counts nans present before index. Remove first and last index to investigate if there are
        # missing dates within the time on which the stock was present on the exchange
        nan_df = temp_df.Open.isnull().astype(int).groupby(temp_df.Open.notnull().astype(int).cumsum()).sum()[1:-1]


        if nan_df.sum()>0:
            #for debug
            #nan_df[nan_df!=0]
            print(nan_df.sum())
            # we have nans within range of data: interpolate
            nan_tickers.append(ticker)
            # WAG , CERN, DISCA are messed up
            if ticker in ["CERN","CTXS","DISCA"]:
                continue
            temp_df = temp_df.interpolate(limit=5,limit_direction='both', limit_area='inside')
            temp_df["Ticker"] = ticker

        # Concat to cleaned dataframe
        cleaned_data = (temp_df.copy() if cleaned_data.empty else pd.concat([cleaned_data, temp_df]))

    # save index and cleaned dataframe. Index should also have "index" and "date" columns for all index files in this project
    path = functions.get_absolute_path("Resources/Data/BacktestData/alphavantage_index.csv")
    index_df["index"] = index_df.sum(axis=1,numeric_only=True)
    index_df = index_df.rename({"Date":"date"},axis=1)
    index_df[["index","date"]].to_csv(path,sep=",",index=False)

    path = functions.get_absolute_path("Resources/Data/BacktestData/alphavantage_historical_data.csv")
    cleaned_data.to_csv(path,sep=",",index=False)
def merge_tiingo():
    # Assumes directory of datafiles with format {ticker_name}.csv
    path = functions.get_absolute_path("Resources/Data/ScrapedTiingoData/")

    # tickers
    tickers = os.listdir(path)

    # columns in downloaded data

    columns = ["date","close","high","low","open","volume","adjClose","adjHigh","adjLow","adjOpen","adjVolume","divCash","splitFactor"]
    print_df = pd.DataFrame(columns=columns)
    for ticker in tickers:
        data = pd.read_csv(f"{path+ticker}", sep=",")

        #Turn data upside down for index purposes
        data["Ticker"] = ticker.replace(".csv","")
        if print_df.empty:
            print_df = data.copy()
        else:
            print_df = pd.concat([print_df, data])

    print_df = print_df.drop(["adjClose","adjHigh","adjLow","adjOpen","adjVolume","divCash","splitFactor"],axis=1)
    print_df=print_df.rename({"date":"Date", "open": "Open","close":"Close","volume":"Volume", "high":"High", "low":"Low"}, axis=1)
    path = functions.get_absolute_path("Resources/Data/RawData/tiingo_historical_data.csv")
    print_df.to_csv(path,sep=",",index=False)
def clean_tiingo():
    # Path to merged dataframe
    path = functions.get_absolute_path("Resources/Data/RawData/tiingo_historical_data.csv")
    data = pd.read_csv(path,sep=",")
    data["Date"] = data["Date"].apply(lambda x: x.replace("T00:00:00.000Z", ""))
    grouped_data = data.groupby("Ticker", sort=False)

    tickers = data["Ticker"].unique().tolist()
    # columns of cleaned dataframe. Should be same format for all cleaned dataframes in this project
    columns = ["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]

    cleaned_data = pd.DataFrame(columns=columns)

    # Dataframe to hold index. MMM contains all indicies we want in final dataframe
    example_ticker = "MMM"
    example_df = grouped_data.get_group(example_ticker)

    index_df = pd.DataFrame(columns = ["Date"])
    index_df["Date"] = example_df["Date"]
    nan_tickers = []

    for ticker in tickers:
        stock_data = grouped_data.get_group(ticker)

        # Temp df holds data to be merged. That is, the dates of example_df. Merge data and manually inspect nans (missing days)
        temp_df = pd.DataFrame(columns=["Date"])
        temp_df["Date"] = example_df["Date"]
        temp_df = temp_df.merge(stock_data[columns], how="left", left_on='Date', right_on='Date')
        temp_df["Ticker"] = ticker

        # Merge open prices to index. Don't care about nans as we will sum all numeric values row wise
        index_df = index_df.merge(stock_data[["Open", "Date"]], how="left", left_on='Date', right_on='Date').rename({"Open":ticker},axis=1)

        # Nan_df counts nans present before index. Remove first and last index to investigate if there are
        # missing dates within the time on which the stock was present on the exchange
        nan_df = temp_df.Open.isnull().astype(int).groupby(temp_df.Open.notnull().astype(int).cumsum()).sum()[1:-1]


        if nan_df.sum()>0:
            #for debug
            #nan_df[nan_df!=0]
            print(nan_df.sum())
            # we have nans within range of data: interpolate
            nan_tickers.append(ticker)
            # WAG , CERN, DISCA are messed up
            if ticker in ["WAG", "CTXS", "DISCA"]:
                continue
            temp_df = temp_df.interpolate(limit=5,limit_direction='both', limit_area='inside')
            temp_df["Ticker"] = ticker

        # Concat to cleaned dataframe
        cleaned_data = (temp_df.copy() if cleaned_data.empty else pd.concat([cleaned_data, temp_df]))

    # save index and cleaned dataframe. Index should also have "index" and "date" columns for all index files in this project
    path = functions.get_absolute_path("Resources/Data/BacktestData/tiingo_index.csv")
    index_df["index"] = index_df.sum(axis=1,numeric_only=True)
    index_df = index_df.rename({"Date":"date"},axis=1)
    index_df[["index","date"]].to_csv(path,sep=",",index=False)

    path = functions.get_absolute_path("Resources/Data/BacktestData/tiingo_historical_data.csv")
    cleaned_data.to_csv(path,sep=",",index=False)
def merge_macrotrend():
    # Assumes directory of datafiles with format {ticker_name}.csv
    path = functions.get_absolute_path("Resources/Data/ScrapedMacrotrendData/")

    # tickers
    tickers = os.listdir(path)

    # columns in downloaded data
    columns = ["Date","Open", "High", "Low", "Close", "Volume", "Ticker"]
    print_df = pd.DataFrame(columns=columns)

    for ticker in tickers:
        data = pd.read_csv(f"{path}{ticker}", sep=",",skiprows=14)

        #Turn data upside down for index purposes
        data["Ticker"] = ticker.replace(".csv","").replace("MacroTrends_Data_Download_","")
        if print_df.empty:
            print_df = data.copy()
        else:
            print_df = pd.concat([print_df, data])

    print_df = print_df.rename({"date":"Date","open":"Open","high":"High","low":"Low","close":"Close","volume":"Volume"},axis=1)
    path = functions.get_absolute_path("Resources/Data/RawData/macrotrend_historical_data.csv")
    print_df.to_csv(path,sep=",",index=False)
def clean_macrotrend():
    backtest_path = functions.get_absolute_path("Resources/Data/RawData/macrotrend_historical_data.csv")
    data = pd.read_csv(backtest_path, sep=",")

    tickers = data["Ticker"].unique().tolist()
    # columns of cleaned dataframe. Should be same format for all cleaned dataframes in this project
    columns = ["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]

    cleaned_data = pd.DataFrame(columns=columns)
    grouped_data = data.groupby("Ticker", sort=False)

    # Dataframe to hold index. MMM contains all indicies we want in final dataframe
    example_ticker = "MMM"
    example_df = grouped_data.get_group(example_ticker)

    #These dates are well-defined for MMM
    start_date = "1999-01-05"
    end_date = "2024-04-16"

    #isolate data in the selected timeframe
    start_index = example_df.index[example_df['Date'].values==start_date][0]
    end_index = example_df.index[example_df['Date'].values==end_date][0]
    example_df = example_df.loc[start_index:end_index, columns]

    index_df = pd.DataFrame(columns = ["Date"])
    index_df["Date"] = example_df["Date"]
    nan_tickers = []

    for ticker in tickers:
        stock_data = grouped_data.get_group(ticker)

        # Temp df holds data to be merged. That is, the dates of example_df. Merge data and manually inspect nans (missing days)
        temp_df = pd.DataFrame(columns=["Date"])
        temp_df["Date"] = example_df["Date"]
        temp_df = temp_df.merge(stock_data[columns], how="left", left_on='Date', right_on='Date')
        temp_df["Ticker"] = ticker

        # Merge open prices to index. Don't care about nans as we will sum all numeric values row wise
        index_df = index_df.merge(stock_data[["Open", "Date"]], how="left", left_on='Date', right_on='Date').rename({"Open":ticker},axis=1)

        # Nan_df counts nans present before index. Remove first and last index to investigate if there are
        # missing dates within the time on which the stock was present on the exchange
        nan_df = temp_df.Open.isnull().astype(int).groupby(temp_df.Open.notnull().astype(int).cumsum()).sum()[1:-1]


        if nan_df.sum()>0:
            #for debug
            #nan_df[nan_df!=0]
            print(nan_df.sum())
            # we have nans within range of data: interpolate
            nan_tickers.append(ticker)
            # These are messed up
            if ticker in ["CA", "HCP", "DISCA","S"]:
                continue
            temp_df = temp_df.interpolate(limit=5,limit_direction='both', limit_area='inside')
            temp_df["Ticker"] = ticker

        # Concat to cleaned dataframe
        cleaned_data = (temp_df.copy() if cleaned_data.empty else pd.concat([cleaned_data, temp_df]))

    # save index and cleaned dataframe. Index should also have "index" and "date" columns for all index files in this project
    path = functions.get_absolute_path("Resources/Data/BacktestData/macrotrend_index.csv")
    index_df["index"] = index_df.sum(axis=1,numeric_only=True)
    index_df = index_df.rename({"Date":"date"},axis=1)
    index_df[["index","date"]].to_csv(path,sep=",",index=False)

    path = functions.get_absolute_path("Resources/Data/BacktestData/macrotrend_historical_data.csv")
    cleaned_data.to_csv(path,sep=",",index=False)
def clean_simfin():
    path = functions.get_absolute_path("Resources/Data/RawData/simfin_historical_data.csv")
    data = pd.read_csv(path, sep=";")

    ticker_path = functions.get_absolute_path("Resources/Data/RawData/s&p_tickers.csv")
    tickers = pd.read_csv(ticker_path)
    tickers = tickers["TICKERS"].tolist()
    available_tickers = data["Ticker"].tolist()

    columns = ["Date","Open", "High", "Low", "Close", "Adj. Close", "Volume"]

    #df to hold cleaned data
    cleaned_data = pd.DataFrame(columns=columns)
    grouped_data = data.groupby("Ticker", sort=False)

    # Dataframe to hold index. MMM contains all indicies we want in final dataframe
    example_ticker = "MMM"
    example_df = grouped_data.get_group(example_ticker)

    index_df = pd.DataFrame(columns = ["Date"])
    index_df["Date"] = example_df["Date"]
    nan_tickers = []

    for ticker in tickers:
        if ticker in available_tickers:
            stock_data = grouped_data.get_group(ticker)

            # Temp df holds data to be merged. That is, the dates of example_df. Merge data and manually inspect nans (missing days)
            temp_df = pd.DataFrame(columns=["Date"])
            temp_df["Date"] = example_df["Date"]
            temp_df = temp_df.merge(stock_data[columns], how="left", left_on='Date', right_on='Date')
            temp_df["Ticker"] = ticker

            # Merge open prices to index. Don't care about nans as we will sum all numeric values row wise
            index_df = index_df.merge(stock_data[["Open", "Date"]], how="left", left_on='Date', right_on='Date').rename({"Open":ticker},axis=1)

            # Nan_df counts nans present before index. Remove first and last index to investigate if there are
            # missing dates within the time on which the stock was present on the exchange
            nan_df = temp_df.Open.isnull().astype(int).groupby(temp_df.Open.notnull().astype(int).cumsum()).sum()[1:-1]

            if nan_df.sum()>0:
                #for debug
                #nan_df[nan_df!=0]
                print(nan_df.sum())
                # we have nans within range of data: interpolate
                nan_tickers.append(ticker)
                # These are messed up
                if ticker in ["CERN", "CTXS", "DISCA","S"]:
                    continue
                temp_df = temp_df.interpolate(limit=5,limit_direction='both', limit_area='inside')
                temp_df["Ticker"] = ticker

            # Concat to cleaned dataframe
            cleaned_data = (temp_df.copy() if cleaned_data.empty else pd.concat([cleaned_data, temp_df]))


    path = functions.get_absolute_path("Resources/Data/BacktestData/simfin_index.csv")
    index_df["index"] = index_df.sum(axis=1,numeric_only=True)
    index_df = index_df.rename({"Date":"date"},axis=1)
    index_df[["index","date"]].to_csv(path,sep=",",index=False)

    path = functions.get_absolute_path("Resources/Data/BacktestData/simfin_historical_data.csv")
    cleaned_data.to_csv(path, sep=",", index=False)
def clean_excel():
    ################NOT REVISED
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "../Data/RawData/excel_historical_data.csv")
    data = pd.read_csv(data_file, sep=";", decimal=",")

    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "../Data/RawData/Backtestdata.csv")
    oldData = pd.read_csv(data_file, sep=",")

    data["S&P500"] = data.sum(axis=1)
    test = oldData.iloc[1837:]["Date"]
    test = test.drop(7935, axis=0)
    data["Date"] = test.to_list()

    data.to_csv(os.path.join(script_directory, "../Data/s&p500.csv"), sep=";", header=True)


    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "../Data/RawData/excel_historical_data.csv")
    data = pd.read_csv(data_file, sep=";", decimal=",")

    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "../Data/RawData/Backtestdata.csv")
    oldData = pd.read_csv(data_file, sep=",")

    test = oldData.iloc[1837:]["Date"]
    test = test.drop(7935, axis=0)
    data.index = test.to_list()

    brokenTickers = []

    for col in data.columns:
        if data[col].isna().values.any():
            brokenTickers.append(col)
            # multiIndex object
            multiIndex = data[col].index[data[col].apply(np.isnan)]

            df_index = data.index.values.tolist()
            indicies = [df_index.index(i) for i in multiIndex]

            for index in indicies:
                date = data.index.to_list()[index]
                #price = yf.Ticker(col).history(interval="1d", start=date,end = date, keepna=True)["Open"]
                # if price.shape[0] == 0:
                #     print(index)
                #     continue

if __name__ == "__main__":
    clean_simfin()