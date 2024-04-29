# Libraries
import os
import pandas as pd
import functions

# Api key
path = functions.get_absolute_path("Resources/APIKEYS/alpha_vantage.txt")
with open(path, "r") as f:
    api_key = f.readlines()[0]
    f.close()

# tickers to download
ticker_path = functions.get_absolute_path("Resources/Data/RawData/s&p_tickers.csv")
tickers = pd.read_csv(ticker_path)
tickers = tickers["TICKERS"].tolist()

#save path
path = "C:/Users/Vahlg/Desktop/data/"
dir_list = os.listdir(path)

used_tickers = [name.replace(".csv","") for name in dir_list]

flag = False
for index, ticker in enumerate(tickers):
    if ticker not in used_tickers:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&datatype=csv&apikey={api_key}'
        data = pd.read_csv(url)

        # Either error or no data
        if data.shape[0] > 2:
            data.to_csv(f"{path}{ticker}.csv", sep=",", index=False)
            print(f"scraped {ticker}")

        else:
            try:
                # Error. Download anyways such that we avoid be stuck
                if "Error" in data["{"].tolist()[0]:
                    data.to_csv(f"{path}{ticker}.csv", sep=",", index=False)
                else:
                    print("Out of api calls")
                    flag = True
            except Exception:
                    flag = True
    if flag == True:
        break