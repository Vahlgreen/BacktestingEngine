import yfinance as yf
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
#ticker.info
#ticker.action
#ticker.sustainability
#ticker.recommendations
#ticker.calendar



#cash = 10000
#grand_exchange = []
#portfolio = [] #["MSFT","AAPL", "PFE", "T", "AMZN", "F", "TSLA"]
#pickle.dump(cash, open("cashstack.p","wb"))
#pickle.dump(portfolio, open("portfolio.p","wb"))


def main():

    end_date = datetime.now().strftime('%Y-%m-%d')

    cash = pickle.load( open( "cashstack.p", "rb" ) )
    portfolio = pickle.load( open( "portfolio.p", "rb" ) )

    print(f"Current cash stack ${cash}\n")
    print(f"Current portfolio\n {portfolio}\n")

    input("press any key to continue")

    exchange = pd.read_csv("tickersymbols.csv",nrows=400)["Name"] # 411 stocks
    cash,portfolio = DecideBuy(exchange, portfolio, cash)
    cash,portfolio= DecideSell(portfolio,cash)

    print(f"Final portolio: {portfolio} which is worth $ {GetPortfolioWorth(portfolio)}")
    print(f"Final cash stack: ${cash}")

    pickle.dump(cash,open("cashstack.p", "wb"))
    pickle.dump(portfolio,open( "portfolio.p","wb"))
    




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
        ticker = yf.Ticker(stock[1])
        stockHistory = ticker.history(period = '1d')
        worth += float(stockHistory["Open"][0])
    
    return worth

def Sell(stock,portfolio,cash):
    price = float(yf.Ticker(stock).history(period="1d")["Open"][0])
    print(f"selling {stock}")
    portfolio.remove(stock)
    cash = cash + price
    print(f"new portfolio\n {portfolio} \n new cashstack ${cash}")

    return cash,portfolio

def Buy(stock,portfolio,cash):
    return



def DecideBuy(ticker:str)->bool:

    return True



def DecideSell():
    return

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