
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import StringIO
import datetime as dt
import numpy as np
def Merge():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "../Data/RawData/s&p_tickers.csv")
    tickers = pd.read_csv(data_file)
    tickers = tickers["TICKERS"].to_list()

    final_df = pd.DataFrame(columns=['date','open','high','low','close','volume','ticker'])
    empty_tickers = []
    for i,ticker in enumerate(tickers):
        data_file = os.path.join(script_directory, f"../Data/scraped/MacroTrends_Data_Download_{ticker}.csv")
        with open(data_file,"r") as f:
            content = f.read()
            content = content[content.index("date"):]
            content = StringIO(content.replace(" ",""))
            df = pd.read_csv(content, sep=",")
            if df.shape[0]<10:
                #following tickers returned no data:
                #['BMC', 'COH', 'CBE', 'CVH', 'HNZ', 'KFT', 'LTD', 'MHP', 'PCS', 'MOLX', 'NYX', 'PCLN', 'TSO', 'TIE', 'TYC', 'WAG', 'WPO', 'WPI', 'WLP', 'YHOO']
                empty_tickers.append(ticker)
                continue
            df["ticker"] = ticker
            final_df = pd.concat([final_df, df], ignore_index=False)
            print(f"Processed {i+1} of {len(tickers)}")

    print(empty_tickers)
    data_location = os.path.join(script_directory, "../Data/macrotrend_historical_data.csv")
    final_df.to_csv(data_location,  index=False)
def Scrape():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    # data_file = os.path.join(script_directory, "../Data/s&p_tickers.csv")
    data_file = os.path.join(script_directory, "../Data/RawData/s&p_tickers.csv")

    tickers = pd.read_csv(data_file)
    tickers = tickers["TICKERS"].to_list()

    # chrome, works locally
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    wait = WebDriverWait(driver, 5)


    for i,ticker in enumerate(tickers):
        url = f"https://www.macrotrends.net/assets/php/stock_price_history.php?t={ticker}"
        # open browser
        driver.get(url)
        #time.sleep(0.5)
        button = "/html/body/div/div[1]/div[4]/div/button/strong"
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, button)))
            driver.find_element(By.XPATH,button).click()
            print(f"Downloaded file {i} of {len(tickers)}")
        except Exception:
            print(f"Url not available: {ticker}")
            continue
def Read_Result():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    # data_file = os.path.join(script_directory, "../Data/s&p_tickers.csv")
    data_file = os.path.join(script_directory, "../Data/RawData/macrotrend_historical_data.csv")
    data = pd.read_csv("/Resources/Data/macrotrend_historical_data.csv")
    print("")

def Clean():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_directory, "../Data/RawData/s&p_tickers.csv")
    tickers = pd.read_csv(data_file)
    tickers = tickers["TICKERS"].tolist()
    data_file = os.path.join(script_directory, "../Data/macrotrend_historical_data.csv")
    df = pd.read_csv(data_file)

    #check for nan
    #No nans found
    #print(df.isnull().values.any())

    ticker_list = []
    #check if any days are missing and rapid changes
    i = 0
    threshold = 0.8
    for ticker in tickers:
        flag = f"{ticker}: "

        # #Not viable
        # dates = df[df["ticker"] == ticker]["date"].tolist()
        # start_date = dates[0].split("-")
        # end_date = dates[-1].split("-")
        # start = dt.date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
        # end = dt.date(int(end_date[0]), int(end_date[1]), int(end_date[2]))
        # market_days = np.busday_count(start, end)
        # if len(market_days) != len(dates):
        #     flag += f"Missing {len(dates)-len(market_days)} days, "

        date_data = df[df["ticker"]==ticker]["date"]
        open_data = df[df["ticker"]==ticker]["open"].pct_change()
        rapid_changes = (abs(open_data) > threshold)
        if sum(rapid_changes) > 0:
            flag+=f" experienced {sum(rapid_changes)} rapid changes in following dates: {[str(x) for x in date_data[rapid_changes]]}"

        if flag != f"{ticker}: ":
            i = i+1
            print(flag)
            ticker_list.append(ticker)
    [print(x) for x in ticker_list]
    print(f"{i} tickers to look at")
    #look at BBBY, CA,CBS
    # BBBY: missing data
    # CA: missing data
    # DNR: need latest data
    # GCI: need older data
    # HCP: missing days
    # HP: large descripancy in values
    # KEY: large descripancy in values
    # LLL: might be missing days
#     PLL: values off
#     PBI: discontinuity at 2021-01-27
# QEP: trend off and need values in both ends
# S: missing days
# TSS: missing date after 2015
# XL: values of
if (__name__ == "__main__"):
    #Scrape()
    #Merge()
    #Read_Result()
    Clean()