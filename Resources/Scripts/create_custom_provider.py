# Libraries
import yfinance as yf
import os
import pandas as pd
import datetime  # import datetime, timedelta
from datetime import timedelta, datetime
import statistics as stat
import matplotlib.pyplot as plt
import functions
import json
import requests
import re
import cloudscraper
import tls_client
from bs4 import BeautifulSoup
import requests
import numpy as np
from investiny import historical_data
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

def compare_stocks():
    data_providers = ["tiingo","alphavantage","macrotrend","simfin"]
    data_paths = [functions.get_absolute_path(f"Resources/Data/BacktestData/{data_providers[i]}_historical_data.csv") for i in range(len(data_providers))]

    data = {data_providers[i]: pd.read_csv(data_paths[i], sep=",") for i in range(len(data_providers))}

    tickers = set(data["alphavantage"]["Ticker"])
    for _, df in data.items():
        tickers = tickers.intersection(df["Ticker"])

    grouped_data = {data_providers[i]: data[data_providers[i]].groupby("Ticker") for i in range(len(data_providers))}

    tickers = list(tickers)


    settings = {
        "tiingo" : dict(color='yellow', width=6,dash='dash'),
        "alphavantage": dict(color='blue', width=2),
        "macrotrend": dict(color='green', width=2),
        "simfin": dict(color='red', width=2)
    }

    average = ["FITB","CB","JWN","DE", "BBY","VLO","GD", "TROW","HSY","D","WFC","EOG","EXC","FE", "FCX","EMN", "AES","AVP","XLNX","STZ","VNO","BBBY","ADI","RF"]
    review = ["TIF", "DPS","NEE","XOM","BEN","VAR","KR","DVN","HAL","CF","VFC","DELL","COP","CSX","PDCO","MMM","EL","TWX","LOW","MO","TAP","RHI", "TIF", "HRB","GME","HPQ","NOC","FLS","EBAY","PHM","DHR","APA","LEN","PEG","PGR","HES","IRM","UNP","SYY","PBCT","KO","MTB","WMT","BWA","M","SYK","MUR","AET","JNJ","FLR","NI","MRO","TXT","NBL","WY","OXY","MS","PG","BAC","WEC","SLM","PPL","CVS","STT","OMC","CSCO","VMT","SWM","ECL","EQT","FIS","XL","F","EMR"]
    alpha =['LMT', 'TSN', 'SJM',"LSI","CNP","TSS","KEY","NEM","IPG","DRI","ADP","CINF","BTU","ATI","AMT","EIX","DTE","BMY","GPC","AON","STX","AXP","HON","HBAN","MCD","ANF","WM","HD","WYNN","HIG","R","PRGO","PFG","DNB","INTC"  ,"HST","K","WPX","TRIP","CCI","VTR","LRCX","NWL","PEP","PAYX","AGN","CTAS","NSC","CMG","SEE","PCG","AVY","HAS","DHI","SUN","COF","BA","RRC","SO","ACN","KMI","TRV","ETR","FHN","PNC","AMP","EQR","LLY","RDC","BDX","AA","T","BEAM","CCL","KLAC","MAT","PRU","KMB","ADSK","ADM","UPS","PM","TGT","ALTR","DIS","GWW","BXP","EFX","CMS","XLNX","SWK","HUM","MAS","NE","MRK","GT","AVB","BK","NTRS","WY","LLL","APD","DFS","AIZ","WU","ROK","GNW","XEL","LEG","TMO","CPB","DOW","DO","TEL","RRD","USB","FDX", "GS",'ETN',"AIG","C","AEE","SCHW","IFF","SPG","ALL","RTN", 'WDC', 'XYL',"SNA","PSX","ED", 'UNM', 'RSG', 'AEP', 'PSA', 'WMB', 'EXPE', 'VZ', 'PBI', 'CAG', 'MET', 'RL', 'CHK', 'CMCSA', 'CLX', 'LNC', 'SE', 'PLL', 'IP', 'WHR', 'MDT', 'PFE', 'FSLR', 'X', 'ETFC', 'BLK', 'JPM', 'AMGN', 'PH', 'BIG', 'MCK', 'COL', 'OI', 'PNW', 'VMC', 'NTAP', 'PXD', 'DOV']
    macrotrend = ['ORLY',"ALXN","MNST","WAT","AAPL","URBN","CLF","CRM","AZO","NBR","ROP","ISRG","CELG","GOOG","MAR","MCO","HOG","PWR","AMAT","DD","QEP","AMD","CAT","FOSL","CTSH","ADBE","BMS","CNX","MSI","LH","APC","FAST","AMZN","NVDA","RHT","THC","NDAQ","XRX","BSX","SHW","SCG","ROST","NFX","MKC","LIFE", 'BIIB',"AN","SWN","APH","CI","MPC","CSV","GCI","FMC","GLW","SBUX","FFIV","BAX","NKE","EXPD","AIV","IVZ","CMCSA","ESRX","V","MU","COST","XRAY","GE","MSFT","MCHP","ORCL","AFL","TDC", 'OKE', 'CMI', 'MOS', 'JNPR', 'IBM', 'A', 'CHRW', 'TJX', 'KMX', 'JCI', 'EA', 'MA', 'CAH', 'ICE', 'PX', 'EW', 'GPS', 'MYL', 'NFLX', 'DUK', 'MMC', 'PPG', 'L', 'GIS', 'FTI', 'NOV', 'SRCL', 'INTU', 'ORLY', 'ITW', 'DV', 'CMCA', 'HRL', 'YUM', 'JBL', 'PLD', 'STZ', 'LUV', 'PCAR', 'SRE', 'KSS', 'CME', 'AVP', 'HP', 'IGT', 'TXN', 'CL', 'DLTR', 'FLIR', 'QCOM', 'ABT', 'GILD', 'UNH', 'MM', 'AKAM', 'TER', 'NUE', 'KIM', 'DGX', 'DVA', 'NRG', 'CVX', 'SLB']


    print(len(macrotrend+alpha+review+average))
    j=0
    for ticker in tickers:
        if ticker not in macrotrend+alpha+review+average:
            j = j + 1
            if j == 20:
                break
            fig = go.Figure()
            i = 0
            for provider, df in grouped_data.items():
                i = i +1
                plot_data = grouped_data[provider].get_group(ticker)

                fig.add_trace(go.Scatter(x=plot_data["Date"],
                                         y=plot_data["Open"],
                                         name=provider,
                                         line=settings[provider]))

            fig.update_layout(title = f"Stock comparison for {ticker}")
            fig.show()
            fig.write_html(functions.get_absolute_path(f"Resources/Data/StockComparisons/{ticker}.html"))

def compare_index():
    data_providers = ["tiingo", "alphavantage", "macrotrend", "simfin"]
    data_paths = [functions.get_absolute_path(f"Resources/Data/BacktestData/{data_providers[i]}_index.csv")
                  for i in range(len(data_providers))]

    data = {data_providers[i]: pd.read_csv(data_paths[i], sep=",") for i in range(len(data_providers))}

    for provider, df in data.items():
        df_temp = pd.DataFrame(columns=["date","index"])
        df_temp["date"] = df["date"]
        df_temp["index"] = df["index"]/df["index"].tolist()[0]
        data.update({provider:df_temp})


    settings = {
        "tiingo": dict(color='yellow', width=2),
        "alphavantage": dict(color='blue', width=2),
        "macrotrend": dict(color='green', width=2),
        "simfin": dict(color='red', width=2)
    }
    fig = go.Figure()
    for provider, df in data.items():
        plot_data = data[provider]
        # if provider == "alphavantage":
        fig.add_trace(go.Scatter(x=plot_data["date"],
                                 y=plot_data["index"],
                                 name=provider,
                                 line=settings[provider]))

    fig.write_html(functions.get_absolute_path(f"Resources/Data/StockComparisons/index.html"))
    fig.show()

def construct_new_stock_provider():
    average = ["FITB", "CB", "JWN", "DE", "BBY", "VLO", "GD", "TROW", "HSY", "D", "WFC", "EOG", "EXC", "FE", "FCX",
               "EMN", "AES", "AVP", "XLNX", "STZ", "VNO", "BBBY", "ADI", "RF"]
    review = ["CMCSA","VRSN","TIF", "DPS", "NEE", "XOM", "BEN", "VAR", "KR", "DVN", "HAL", "CF", "VFC", "DELL", "COP", "CSX", "PDCO",
              "MMM", "EL", "TWX", "LOW", "MO", "TAP", "RHI", "TIF", "HRB", "GME", "HPQ", "NOC", "FLS", "EBAY", "PHM",
              "DHR", "APA", "LEN", "PEG", "PGR", "HES", "IRM", "UNP", "SYY", "PBCT", "KO", "MTB", "WMT", "BWA", "M",
              "SYK", "MUR", "AET", "JNJ", "FLR", "NI", "MRO", "TXT", "NBL", "WY", "OXY", "MS", "PG", "BAC", "WEC",
              "SLM", "PPL", "CVS", "STT", "OMC", "CSCO", "VMT", "SWM", "ECL", "EQT", "FIS", "XL", "F", "EMR"]
    alpha = ['LMT', 'TSN', 'SJM', "LSI", "CNP", "TSS", "KEY", "NEM", "IPG", "DRI", "ADP", "CINF", "BTU", "ATI", "AMT",
             "EIX", "DTE", "BMY", "GPC", "AON", "STX", "AXP", "HON", "HBAN", "MCD", "ANF", "WM", "HD", "WYNN", "HIG",
             "R", "PRGO", "PFG", "DNB", "INTC", "HST", "K", "WPX", "TRIP", "CCI", "VTR", "LRCX", "NWL", "PEP", "PAYX",
             "AGN", "CTAS", "NSC", "CMG", "SEE", "PCG", "AVY", "HAS", "DHI", "SUN", "COF", "BA", "RRC", "SO", "ACN",
             "KMI", "TRV", "ETR", "FHN", "PNC", "AMP", "EQR", "LLY", "RDC", "BDX", "AA", "T", "BEAM", "CCL",
             "KLAC", "MAT", "PRU", "KMB", "ADSK", "ADM", "UPS", "PM", "TGT", "ALTR", "DIS", "GWW", "BXP", "EFX", "CMS",
             "SWK", "HUM", "MAS", "NE", "MRK", "GT", "AVB", "BK", "NTRS", "WY", "LLL", "APD", "DFS",
             "AIZ", "WU", "ROK", "GNW", "XEL", "LEG", "TMO", "CPB", "DOW", "DO", "TEL", "RRD", "USB", "FDX", "GS",
             'ETN', "AIG", "C", "AEE", "SCHW", "IFF", "SPG", "ALL", "RTN", 'WDC', 'XYL', "SNA", "PSX", "ED", 'UNM',
             'RSG', 'AEP', 'PSA', 'WMB', 'EXPE', 'VZ', 'PBI', 'CAG', 'MET', 'RL', 'CHK', 'CLX', 'LNC', 'SE',
             'PLL', 'IP', 'WHR', 'MDT', 'PFE', 'FSLR', 'X', 'ETFC', 'BLK', 'JPM', 'AMGN', 'PH', 'BIG', 'MCK', 'COL',
             'OI', 'PNW', 'VMC', 'NTAP', 'PXD', 'DOV']
    macrotrend = ['ORLY', "ALXN", "MNST", "WAT", "AAPL", "URBN", "CLF", "CRM", "AZO", "NBR", "ROP", "ISRG", "CELG",
                  "GOOG", "MAR", "MCO", "HOG", "PWR", "AMAT", "DD", "QEP", "AMD", "CAT", "FOSL", "CTSH", "ADBE", "BMS",
                  "CNX", "MSI", "LH", "APC", "FAST", "AMZN", "NVDA", "RHT", "THC", "NDAQ", "XRX", "BSX", "SHW", "SCG",
                  "ROST", "NFX", "MKC", "LIFE", 'BIIB', "AN", "SWN", "APH", "CI", "MPC", "GCI", "FMC", "GLW",
                  "SBUX", "FFIV", "BAX", "NKE", "EXPD", "AIV", "IVZ", "ESRX", "V", "MU", "COST", "XRAY", "GE",
                  "MSFT", "MCHP", "ORCL", "AFL", "TDC", 'OKE', 'CMI', 'MOS', 'JNPR', 'IBM', 'A', 'CHRW', 'TJX', 'KMX',
                  'JCI', 'EA', 'MA', 'CAH', 'ICE', 'PX', 'EW', 'GPS', 'MYL', 'NFLX', 'DUK', 'MMC', 'PPG', 'L',
                  'GIS', 'FTI', 'NOV', 'SRCL', 'INTU', 'ORLY', 'ITW', 'DV', 'HRL', 'YUM', 'JBL', 'PLD',
                  'LUV', 'PCAR', 'SRE', 'KSS', 'CME', 'HP', 'IGT', 'TXN', 'CL', 'DLTR', 'FLIR', 'QCOM', 'ABT',
                  'GILD', 'UNH', 'AKAM', 'TER', 'NUE', 'KIM', 'DGX', 'DVA', 'NRG', 'CVX', 'SLB']


    data_providers = ["tiingo","alphavantage","macrotrend","simfin"]
    data_paths = [functions.get_absolute_path(f"Resources/Data/BacktestData/{data_providers[i]}_historical_data.csv") for i in range(len(data_providers))]

    data = {data_providers[i]: pd.read_csv(data_paths[i], sep=",") for i in range(len(data_providers))}

    tickers = set(data["alphavantage"]["Ticker"])
    for _, df in data.items():
        tickers = tickers.intersection(df["Ticker"])

    grouped_data = {data_providers[i]: data[data_providers[i]].groupby("Ticker") for i in range(len(data_providers))}

    columns = ["Date","Open", "High", "Low", "Close", "Volume"]

    #df to hold cleaned data
    cleaned_data = pd.DataFrame(columns=columns)

    # Dataframe to hold index. AAPL contains all indicies we want in final dataframe
    example_ticker = "AAPL"
    start_date = "2001-01-02"
    end_date = "2024-03-28"

    example_df = grouped_data["alphavantage"].get_group(example_ticker)
    example_df = example_df[(example_df.Date > start_date) & (example_df.Date < end_date)]
    index_df = pd.DataFrame(columns = ["Date"])
    index_df["Date"] = example_df["Date"]

    alpha = list(set(alpha))
    macrotrend = list(set(macrotrend))
    average = list(set(average))
    for ticker in alpha+macrotrend+average:
        if ticker =="JWN":
            print("")
        stock_data = pd.DataFrame(columns=columns)
        if ticker in alpha:
            stock_data = grouped_data["alphavantage"].get_group(ticker)

        elif ticker in macrotrend:
            stock_data = grouped_data["macrotrend"].get_group(ticker)

        else:
            stock_data_alpha = grouped_data["alphavantage"].get_group(ticker)
            stock_data_macrotrend = grouped_data["macrotrend"].get_group(ticker)

            stock_data_alpha = stock_data_alpha[(stock_data_alpha.Date > start_date) & (stock_data_alpha.Date < end_date)].reset_index()
            stock_data_macrotrend = stock_data_macrotrend[(stock_data_macrotrend.Date > start_date) & (stock_data_macrotrend.Date < end_date)].reset_index()

            stock_data["Date"] = example_df["Date"]
            for col in ["Open", "High", "Low", "Close", "Volume"]:
                stock_data[col] = (stock_data_alpha[col]+stock_data_macrotrend[col])/2

        stock_data = stock_data[(stock_data.Date > start_date) & (stock_data.Date < end_date)]


        # Temp df holds data to be merged. That is, the dates of example_df. Merge data and manually inspect nans (missing days)
        temp_df = pd.DataFrame(columns=["Date"])
        temp_df["Date"] = example_df["Date"]
        temp_df = temp_df.merge(stock_data[columns], how="left", left_on='Date', right_on='Date')
        temp_df["Ticker"] = ticker

        # Merge open prices to index. Don't care about nans as we will sum all numeric values row wise
        index_df = index_df.merge(stock_data[["Open", "Date"]], how="left", left_on='Date', right_on='Date').rename(
            {"Open": ticker}, axis=1)

        cleaned_data = (temp_df.copy() if cleaned_data.empty else pd.concat([cleaned_data, temp_df]))

    #Moved to repair_stocks()
    # path = functions.get_absolute_path("Resources/Data/BacktestData/custom_index.csv")
    # index_df["index"] = index_df.sum(axis=1, numeric_only=True)
    # index_df = index_df.rename({"Date": "date"}, axis=1)
    # index_df[["index", "date"]].to_csv(path, sep=",", index=False)

    path = functions.get_absolute_path("Resources/Data/RawData/custom_historical_data.csv")
    cleaned_data.to_csv(path, sep=",", index=False)

def identify_repairable_stocks():

    #review the stocks found in compare stock function. Investigate if we can truncate or repair with yf

    data_providers = ["macrotrend","tiingo","alphavantage","simfin"]
    data_paths = [functions.get_absolute_path(f"Resources/Data/BacktestData/{data_providers[i]}_historical_data.csv") for i in range(len(data_providers))]

    provider_data = {data_providers[i]: pd.read_csv(data_paths[i], sep=",") for i in range(len(data_providers))}

    grouped_data = {data_providers[i]: provider_data[data_providers[i]].groupby("Ticker") for i in range(len(data_providers))}


    ##########################################################
    #repairable. found via inspection
    #XOM: alpha from jul 23 2001
    #VAR: alpha from august 9 2004
    #DVN: alpha from jan 2005
    #HAL: alpha from jun 24 2006
    #EMR: dec 18 2006
    #F: jan 8 2001
    #ECL: jun 13 2003
    #CSCO: jan 3 2001
    #STT: jun 8 2001
    #CVS: jun 9 2005
    #PG: jul 2 2004
    #MS: jan 3 2001
    #JNJ: jul 2 2001
    #SYK: may 25 2004
    #MTB: jan 2 2001
    #SYY: jan 2 2001
    #LEN: jan 30 2004
    #APA: jan 16 2004
    #TIF: jan 2 2001
    #RHI: jan 2 2001

    alpha = ["VRSN"]
    rep_with_yahoo = ["CMCSA","OXY"]


    ##########################################################
    review = ["TIF", "DPS","NEE","XOM","BEN","VAR","KR","DVN","HAL","CF","VFC","DELL","COP","CSX","PDCO","MMM","EL","TWX","LOW","MO","TAP","RHI", "TIF", "HRB","GME","HPQ","NOC","FLS","EBAY","PHM","DHR","APA","LEN","PEG","PGR","HES","IRM","UNP","SYY","PBCT","KO","MTB","WMT","BWA","M","SYK","MUR","AET","JNJ","FLR","NI","MRO","TXT","NBL","WY","OXY","MS","PG","BAC","WEC","SLM","PPL","CVS","STT","OMC","CSCO","VMT","SWM","ECL","EQT","FIS","XL","F","EMR"]


    settings = {
        "tiingo" : dict(color='yellow', width=4,dash='dash'),
        "alphavantage": dict(color='blue', width=2),
        "macrotrend": dict(color='green', width=2),
        "simfin": dict(color='red', width=2),
        "yahoo": dict(color='purple', width=2)
    }
    for ticker in review:
        start_date = "2001-01-02"
        end_date = "2024-03-28"
        yf_data = yf.Ticker(ticker).history(interval="1d", start=start_date, end=end_date, actions=True, repair=True,
                                         keepna=True)
        fig = go.Figure()
        i = 0
        for provider, df in grouped_data.items():
            try:
                plot_data = grouped_data[provider].get_group(ticker)
            except KeyError:
                print(f"{ticker}, {provider}")
                continue
            if i==0:
                fig.add_trace(go.Scatter(x=plot_data["Date"],
                                         y=yf_data["Open"],
                                         name="yahoo",
                                         line=settings["yahoo"]))

            fig.add_trace(go.Scatter(x=plot_data["Date"],
                                     y=plot_data["Open"],
                                     name=provider,
                                     line=settings[provider]))
            i=i+1
        fig.update_layout(title=f"Stock comparison for {ticker}")
        fig.show()
        #print("")

def repair_stocks():
    #adds identified repairable stocks to custom data:
    ##########################################################
    # repairable. found via inspection

    rep_with_yahoo = ["CMCSA", "OXY"]
    tickers = {
        "VRSN": "2001-01-02",
        "RHI": "2001-01-02",
        "TIF": "2001-01-02",
        "APA": "2001-01-16",
        "LEN": "20024-01-30",
        "SYY": "2001-01-02",
        "MTB": "2001-01-02",
        "SYK": "2004-05-25",
        "JNJ": "2001-07-02",
        "MS": "2001-01-02",
        "PG": "2004-07-02",
        "CVS": "2005-06-09",
        "STT": "2001-06-08",
        "CSCO": "2001-01-02",
        "ECL": "2003-13-06",
        "F": "2001-01-08",
        "EMR": "2006-12-18",
        "HAL": "2006-06-24",
        "DVN": "2005-01-03",
        "VAR": "2004-08-09",
        "XOM": "2001-07-23",
    }
    data_path = functions.get_absolute_path(f"Resources/Data/BacktestData/alphavantage_historical_data.csv")
    provider_data = pd.read_csv(data_path, sep=",")
    grouped_data = provider_data.groupby("Ticker")

    path = functions.get_absolute_path("Resources/Data/RawData/custom_historical_data.csv")
    custom_data = pd.read_csv(path, sep=",")

    columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
    example_ticker = "AAPL"
    start_date = "2001-01-02"
    end_date = "2024-03-28"
    example_df = grouped_data.get_group(example_ticker)
    example_df = example_df[(example_df.Date > start_date) & (example_df.Date < end_date)]
    index_df = pd.DataFrame(columns = ["Date"])
    index_df["Date"] = example_df["Date"]


    for ticker,date in tickers.items():
        stock_data = grouped_data.get_group(ticker)
        stock_data = stock_data[(stock_data.Date > date) & (stock_data.Date < end_date)]

        # Temp df holds data to be merged. That is, the dates of example_df. Merge data and manually inspect nans (missing days)
        temp_df = pd.DataFrame(columns=["Date"])
        temp_df["Date"] = example_df["Date"]
        temp_df = temp_df.merge(stock_data[columns], how="left", left_on='Date', right_on='Date')
        temp_df["Ticker"] = ticker

        custom_data = pd.concat([custom_data, temp_df])


    #Create index
    tickers = list(set(custom_data["Ticker"]))
    grouped_custom_data = custom_data.groupby("Ticker")
    for ticker in tickers:
        stock_data = grouped_custom_data.get_group(ticker)
        # Merge open prices to index. Don't care about nans as we will sum all numeric values row wise
        index_df = index_df.merge(stock_data[["Open", "Date"]], how="left", left_on='Date', right_on='Date').rename(
            {"Open": ticker}, axis=1)


    path = functions.get_absolute_path("Resources/Data/BacktestData/custom_index.csv")
    index_df["index"] = index_df.sum(axis=1,numeric_only=True)
    index_df = index_df.rename({"Date":"date"},axis=1)
    index_df[["index","date"]].to_csv(path,sep=",",index=False)

    path = functions.get_absolute_path("Resources/Data/BacktestData/custom_historical_data.csv")
    custom_data.to_csv(path, sep=",", index=False)

if __name__ == "__main__":
    #compare_index()
    #compare_stocks()
    #construct_new_stock_provider()
    #identify_repairable_stocks()
    repair_stocks()