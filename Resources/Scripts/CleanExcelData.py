import os
import pandas as pd
import yfinance as yf
import numpy as np
def LoadAndClean():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "../Data/s&p500ExcelData.csv")
    data = pd.read_csv(data_file, sep=";",decimal=",")

    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "../Data/backtestData.csv")
    oldData = pd.read_csv(data_file, sep=",")

    data["S&P500"] = data.sum(axis=1)
    test = oldData.iloc[1837:]["Date"]
    test = test.drop(7935,axis=0)
    data["Date"] = test.to_list()

    data.to_csv(os.path.join(script_directory, "../Data/s&p500.csv"),sep=";",header=True)

def Repair():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "../Data/s&p500ExcelData.csv")
    data = pd.read_csv(data_file, sep=";", decimal=",")

    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "../Data/backtestData.csv")
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
                price = yf.Ticker(col).history(interval="1d", start=date,end = date, keepna=True)["Open"]
                if price.shape[0] == 0:
                    print(index)
                    continue

def concept():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "../Data/s&p500ExcelData.csv")
    data = pd.read_csv(data_file, sep=";",decimal=",")

    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "../Data/backtestData.csv")
    oldData = pd.read_csv(data_file, sep=",")

    test = oldData.iloc[1837:]["Date"]
    test = test.drop(7935,axis=0)
    data.index = test.to_list()
    hist = yf.Ticker("GOOGL").history(interval="1d", start="2019-07-23", end="2019-08-16", actions=True, repair=True,keepna=True)

    test = data.loc["2019-07-23":"2019-08-16"]["GOOGL"]
    factor = hist["Open"].tolist()[0]/test.tolist()[0]

    transformedTest = test*factor


Repair()