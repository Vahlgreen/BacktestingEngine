import os
import pandas as pd
import matplotlib.pyplot as plt
script_directory = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(script_directory, "../Data/DeprecatedData/RawBacktestData.csv")

data = pd.read_csv(data_file, sep = ",")

data.index = data["Date"].apply(lambda x: x.split(" ")[0])
data = data.drop(["Date","Unnamed: 0"], axis=1)
data["S&P500"] = data.sum(axis=1,skipna=True)


data.to_csv("../Data/BacktestData.csv", header=True)
#data["S&P500"].to_csv("../Data/S&PIndex.csv", header=True)

# data["Date"]=data.index
# data.plot(x="Date",y="CombinedIndex")
# plt.show(block=True)
# print("")