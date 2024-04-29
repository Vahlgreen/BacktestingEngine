import json
import pandas as pd
import requests
import functions
import os
# path = functions.get_absolute_path("Resources/APIKEYS/tiingo.txt")
# with open(path, "r") as f:
#     api_key = f.readlines()[0]
#     f.close()
#
# api_key = api_key.replace("\n","")

api_keys = ["f56850758b47d8ff9da70ce7b6cfeeb9672694aa",
"764125b974e327bc7475292b69e31055452e3bf2",
"ae586ca86e1964d64ebfe85ff2ec912eaa3839e0",
"750ad56b1a32f01067a09b688b7e2ed0dddfac5e",
"8294560906baf3d716497eafcacf6b94a763ca29",
"d3bfe24bfa54eb3ecaaa5aab786b0b7d856ec5d2",
"acb230353e401ca5bb38d0909c7ccb153cb51e35",
"8dcd491d1aee93ee584118880630533abb763f89",
"5d24f93a56bd6bb5ce962e98865710c091b56d27",
"7fe75a582538219d7496d7177487ec1448babd6f",
"e9fde8e614cf3b928eee0e6dd63a885c38a06e34"]


api_key = "f56850758b47d8ff9da70ce7b6cfeeb9672694aa"


ticker_path = functions.get_absolute_path("Resources/Data/RawData/s&p_tickers.csv")
tickers = pd.read_csv(ticker_path)
tickers = tickers["TICKERS"].tolist()
path = "C:/Users/Vahlg/Desktop/data_tiingo/"

dir_list = os.listdir(path)
scraped_tickers = [name.replace(".csv","") for name in dir_list]

headers={
'Content-Type': 'application/json',
'Authorization': 'Token ' + api_key
}

# List of tickers to be downloaded

# create dictionary of DataFrames
tiingo_data = {}
count = 0
response_string =""
api_index = 0
for ticker in tickers:
    if ticker not in scraped_tickers:
        if count == 25:
            print("")
        tk_string = f'https://api.tiingo.com/tiingo/daily/{ticker.lower()}/prices?startDate=1999-01-02&endDate=2024-04-25/'
        try:
            response = requests.get(tk_string, headers=headers).json()
            try:
                if "Error" in response["detail"]:
                    if "Error: Ticker" in response["detail"]:
                        continue
                    count = 0
                    api_index +=1
                    api_key = api_keys[api_index]
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': 'Token ' + api_key
                    }
                    response = requests.get(tk_string, headers=headers).json()
                    if response == []:
                        pd.DataFrame().to_csv(f"{path}{ticker}.csv", sep=",", index=False)
                    else:
                        data = pd.DataFrame.from_dict(response)
                        if data.shape[0] > 2:
                            data.to_csv(f"{path}{ticker}.csv", sep=",", index=False)
                            print(f"scraped {ticker}")

                    continue

            except Exception:
                pass
        except requests.exceptions.ConnectionError:
            continue

        if response == []:
            pd.DataFrame().to_csv(f"{path}{ticker}.csv", sep=",", index=False)
        data = pd.DataFrame.from_dict(response)
        if data.shape[0] > 2:
            data.to_csv(f"{path}{ticker}.csv", sep=",", index=False)
            print(f"scraped {ticker}")
        else:
            print("")

print("")