import os
import pandas as pd
import functions

def create_index():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "../Data/RawData/s&p_tickers.csv")
    tickers = pd.read_csv(data_file)
    tickers = tickers["TICKERS"].tolist()
    data_file = os.path.join(script_directory, "../Data/RawData/simfin_historical_data.csv")
    df = pd.read_csv(data_file,sep=";")

    #df to hold tickers
    simfin_index = pd.DataFrame(columns=["Date"])
    #To avoid dimension issues use MMM. Then we can use left join later
    simfin_index["Date"] = df[df["Ticker"] == "MMM"]["Date"]

    # 98 tickers not present in simfin data:
    missing_ticker_list = ['ACE', 'GAS', 'ARG', 'ANR', 'ABC', 'APOL', 'BHI', 'BLL', 'BCR', 'BBT', 'BRK.B', 'BMC',
                           'BRCM', 'BF.B', 'CA', 'CVC', 'COG', 'CAM', 'CFN', 'CBG', 'CBS', 'CTL', 'COH', 'CSC', 'CBE',
                           'CVH', 'COV', 'DF', 'DNR', 'DTV', 'DISCA', 'DPS', 'EMC', 'ESV', 'FDO', 'FII', 'FISV', 'FRX',
                           'FTR', 'HAR', 'HRS', 'HCN', 'HNZ', 'HSP', 'HCBK', 'IR', 'TEG', 'JEC', 'JDSU', 'JOY', 'KFT',
                           'LM', 'LUK', 'LXK', 'LTD', 'LLTC', 'LO', 'MHP', 'MJN', 'MWV', 'PCS', 'MOLX', 'MON', 'NWSA',
                           'NU', 'NYX', 'POM', 'PCL', 'PCP', 'PCLN', 'RAI', 'SWY', 'SAI', 'SNDK', 'SNI', 'SHLD', 'SIAL',
                           'STJ', 'SPLS', 'HOT', 'STI', 'SYMC', 'TE', 'TSO', 'TWC', 'TIE', 'TMK', 'TYC', 'UTX', 'VIAB',
                           'WAG', 'WPO', 'WPI', 'WLP', 'WFM', 'WYN', 'YHOO', 'ZMH']
    for ticker in tickers:
        if ticker not in missing_ticker_list:
            temp_df = df[df["Ticker"] == ticker][["Date", "Open"]]
            temp_df = temp_df.rename(columns={"Open": ticker})
            simfin_index = simfin_index.merge(temp_df,how="left",left_on='Date', right_on='Date')

    #final df to hold index
    print_df = pd.DataFrame(columns=[["index","date"]])
    print_df["date"] = simfin_index["Date"]
    print_df["index"] = simfin_index.sum(axis=1,numeric_only=True)
    print_df["index"] = print_df["index"]

    #print to csv
    script_directory = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_directory, "../Data/BacktestData/simfin_index.csv")
    print_df.to_csv(path,sep=",",index=False)

def clean_data():
    backtest_path = functions.get_absolute_path("Resources/Data/RawData/simfin_historical_data.csv")
    backtest_data = pd.read_csv(backtest_path, sep=";")
    ticker_path = functions.get_absolute_path("Resources/Data/RawData/s&p_tickers.csv")
    tickers = pd.read_csv(ticker_path)
    tickers = tickers["TICKERS"].tolist()

    # 98 tickers not present in simfin data:
    missing_ticker_list = ['ACE', 'GAS', 'ARG', 'ANR', 'ABC', 'APOL', 'BHI', 'BLL', 'BCR', 'BBT', 'BRK.B', 'BMC',
                           'BRCM', 'BF.B', 'CA', 'CVC', 'COG', 'CAM', 'CFN', 'CBG', 'CBS', 'CTL', 'COH', 'CSC', 'CBE',
                           'CVH', 'COV', 'DF', 'DNR', 'DTV', 'DISCA', 'DPS', 'EMC', 'ESV', 'FDO', 'FII', 'FISV', 'FRX',
                           'FTR', 'HAR', 'HRS', 'HCN', 'HNZ', 'HSP', 'HCBK', 'IR', 'TEG', 'JEC', 'JDSU', 'JOY', 'KFT',
                           'LM', 'LUK', 'LXK', 'LTD', 'LLTC', 'LO', 'MHP', 'MJN', 'MWV', 'PCS', 'MOLX', 'MON', 'NWSA',
                           'NU', 'NYX', 'POM', 'PCL', 'PCP', 'PCLN', 'RAI', 'SWY', 'SAI', 'SNDK', 'SNI', 'SHLD', 'SIAL',
                           'STJ', 'SPLS', 'HOT', 'STI', 'SYMC', 'TE', 'TSO', 'TWC', 'TIE', 'TMK', 'TYC', 'UTX', 'VIAB',
                           'WAG', 'WPO', 'WPI', 'WLP', 'WFM', 'WYN', 'YHOO', 'ZMH']

    nan_tickers = []
    columns = ["Date","Open", "High", "Low", "Close", "Adj. Close", "Volume"]
    #df to hold cleaned data
    cleaned_data = pd.DataFrame(columns=columns)
    for ticker in tickers:
        if ticker not in missing_ticker_list:
            # To avoid dimension issues use MMM. Then we can use left join later
            temp_df= pd.DataFrame(columns=["Date","Ticker"])
            temp_df["Date"] = backtest_data[backtest_data["Ticker"] == "MMM"]["Date"]
            temp_df["Ticker"] = ticker
            temp_df = temp_df.merge(backtest_data[backtest_data["Ticker"] == ticker][columns],how="left",left_on='Date', right_on='Date')
            if temp_df["Open"].isnull().any():
                nan_tickers.append(ticker)
                #Todo: fill out with yfinance if possible
                continue
            cleaned_data = (temp_df.copy() if cleaned_data.empty else pd.concat([cleaned_data,temp_df]))

            #cleaned_data.loc[pd.isna(cleaned_data['Open']), :].index
            #cleaned_data["Date"].to_list()[81]

    path = functions.get_absolute_path("Resources/Data/BacktestData/simfin_historical_data.csv")
    cleaned_data.to_csv(path, sep=",", index=False)
if __name__ == "__main__":
    create_index()
    #clean_data()