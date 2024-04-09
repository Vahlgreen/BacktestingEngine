import os
import pandas as pd


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

#Create index
# df_index = pd.DataFrame(columns=["S&P500","Date"])
# df_index["S&P500"] = data["S&P500"]
# df_index["Date"] = data["Date"]
# df_index.to_csv(os.path.join(script_directory, "../Data/s&pIndex.csv"),sep=",",header=True)
data.to_csv(os.path.join(script_directory, "../Data/s&p500.csv"),sep=";",header=True)
print("")