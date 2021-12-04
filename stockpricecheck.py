import yfinance as yf
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
#ticker.info
#ticker.action
#ticker.sustainability
#ticker.recommendations
#ticker.calendar

#sklajfsdlæfjslækfjlsdkfjlsdf

cash_stack = None
grand_exchange = []
portfolio = [""] #["MSFT","AAPL", "PFE", "T", "AMZN", "F", "TSLA"]
#pickle.dump( cash_stack, open( "cashstack.p", "wb" ) )
#pickle.dump( portfolio, open( "portfolio.p", "wb" ) )
def main():
    
    global cash_stack,grand_exchange,portfolio
    cash_stack = pickle.load( open( "cashstack.p", "rb" ) )
    portfolio = pickle.load( open( "portfolio.p", "rb" ) )

    print("Starting cash stack; $",cash_stack)
    print("Starting portfolio",portfolio)
    
    grand_exchange = pd.read_csv("tickersymbols.csv",nrows=40)["Name"] # 411 stocks
    candidates = DecideBuy()
    print(candidates)
    DecideSell()

    print("Final portolio: ", portfolio, "Which is worth $", GetPortfolioWorth(portfolio))
    print("Final cash stack: $", cash_stack)

    pickle.dump( cash_stack, open( "cashstack.p", "wb" ) )
    pickle.dump( portfolio, open( "portfolio.p", "wb" ) )
    




def PlotStock(tickerHistory):
    price = []
    date = []
    for i in tickerHistory["Open"]:
        price.append(i)
        
    for i in tickerHistory["Open"].index:
        date.append(i)

    plt.plot(date, price)
    plt.show()

def GetPortfolioWorth(portfolio):
    worth = 0
    for stock in portfolio:
        ticker = yf.Ticker(stock)
        stockHistory = ticker.history(period = '1d')
        worth += float(stockHistory["Open"][0])
    
    return worth


def Sell(stock):
    global cash_stack
    price = float(yf.Ticker(stock).history(period="1d")["Open"][0])
    print("Selling ", stock)
    portfolio.remove(stock)
    cash_stack = cash_stack + price
    print("new portfolio ;", portfolio, "new cashstack; $", cash_stack)


def Buy(stock):
    global cash_stack
    #print(yf.Ticker(stock).history(period="1d")["Open"][0])
    price = float(yf.Ticker(stock).history(period="1d")["Open"][0])
    if(price<=cash_stack):
        print("Buying ", stock)
        PlotStock(yf.Ticker(stock).history(period="120d"))
        portfolio.append(stock)
        cash_stack = cash_stack-price
        print("New Portfolio; ", portfolio, "new cashstack $", cash_stack)
        return True
    
    else:
        print("Not enough cash to complete transaction")
        return False
    
def DecideBuy():
    candidates = []
    print("looking for stocks to buy...")
    index = 0
    global cash_stack
    for stock in grand_exchange:
        #try:
        if(stock not in portfolio):
            index = index+1
            print(index, stock)
            history = yf.Ticker(stock).history(period="10d")["Open"]
            if(len(history)== 0):
                print("skipping...")
                continue

            pd.to_numeric(history, errors='coerce')
            ma_low = sum(history)/len(history)
            history = yf.Ticker(stock).history(period="70")["Open"]
            ma_high = sum(history)/len(history)

            if(ma_high<ma_low and history[0]<cash_stack and stock not in portfolio):
                candidates.append(stock)
                print("added",stock)
    
        #except:
            #print("Something went wrong... Continue")



def DecideSell():
    print("looking for stocks to sell...")
    for stock in grand_exchange:
        if(stock in portfolio):
            history = yf.Ticker(stock).history(period="20d")["Open"]
            pd.to_numeric(history, errors='coerce')
            ma_low = sum(history)/len(history)
            history = yf.Ticker(stock).history(period="50d")["Open"]
            ma_high = sum(history)/len(history)
 
            if(ma_high<ma_low and history[0]<cash_stack):
                Sell(stock)


        

    """
    An additional strategy is called the opportunity-cost sell method.
    In this method, the investor owns a portfolio of stocks and sells a stock when a better opportunity presents itself. 
    This requires constant monitoring, research, and analysis of both their portfolio and potential new stock additions. 
    Once a better potential investment has been identified, the investor then reduces or eliminates a position in a current 
    holding that isn't expected to do as well as the new stock on a risk-adjusted return basis.
    """
    
    pass

def ComputeSharpRatio():
    
    """
    sharp_ratio = (R_p-R_f)/s_p
    where
    R_p: return of portfolio
    R_f: risk-free rate
    s_p: standard deviation of the portfolios excess returns

    Subtract the risk-free rate from the return of the portfolio. The risk-free rate could be a U.S. Treasury rate or yield, such as the 
    one-year or two-year Treasury yield.
    Divide the result by the standard deviation of the portfolio’s excess return. 
    The standard deviation helps to show how much the portfolio's return deviates from the expected return. 
    The standard deviation also sheds light on the portfolio's volatility.


    """
    
    pass





if(__name__ ==  "__main__"):
    main()