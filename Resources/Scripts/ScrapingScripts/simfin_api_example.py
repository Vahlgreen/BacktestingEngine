import simfin as sf
from simfin.names import *

import functions

path = functions.get_absolute_path("Resources/APIKEYS/simfin.txt")
with open(path, "r") as f:
    key = f.read()
    f.close()
sf.set_api_key(key)

# Set the local directory where data-files are stored.
# The dir will be created if it does not already exist.
sf.set_data_dir('~/simfin_data/')

# Load daily share-prices for all companies in USA.
# The data is automatically downloaded if you don't have it already.
df_prices = sf.load_shareprices(market='us', variant='daily')

# Plot the closing share-prices for ticker MSFT.
df_prices.loc['MSFT', CLOSE].plot(grid=True, figsize=(20,10), title='MSFT Close')
print("")

# df = pd.read_csv("C:/Users/Vahlg\PycharmProjects\TradingBot\Resources\Data\RawData\simfin_historical_data.csv", sep=";")
# tickers = pd.read_csv("C:/Users\Vahlg\PycharmProjects\TradingBot\Resources\Data\RawData\s&p_tickers.csv")
# test = df[df["Ticker"]=="AAPL"]