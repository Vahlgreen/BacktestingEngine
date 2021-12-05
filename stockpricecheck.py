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

    cash = pickle.load( open( "cashstack.p", "rb" ) )
    portfolio = pickle.load( open( "portfolio.p", "rb" ) )

    print(f"Current cash stack ${cash}\n")
    print(f"Current portfolio\n {portfolio}\n")

    #input("press any key to continue")

    exchange = pd.read_csv("tickersymbols.csv",nrows=20)["Name"] # 411 stocks
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
    #print(yf.Ticker(stock).history(period="1d")["Open"][0])
    price = float(yf.Ticker(stock).history(period="1d")["Open"][0])
    if(price<=cash):
        print(f"Buying {stock}")
       # PlotStock(yf.Ticker(stock).history(period="120d"))
        portfolio[stock]=datetime.now().strftime("%Y-%m-%d")
        cash = cash-price
        print(f"new portfolio\n {portfolio} \n new cashstack ${cash}")
    
    else:
        print("Not enough cash to complete transaction")

    return cash,portfolio



def DecideBuy(exchange, portfolio, cash):
    cash = cash/2
    candidates = []
    print("\nlooking for stocks to buy...")
    for index,stock in enumerate(exchange):
        if(stock not in portfolio.keys()):
            index = index+1
            print(f"Currently considering stock number {index}: {stock}")
            stockprice_history_short = yf.Ticker(stock).history(period="10d")["Open"]
            if(len(stockprice_history_short)== 0):
                print("skipping...")
                continue

            #pd.to_numeric(stockprice_history_short, errors='coerce') maybe not necessary?
            ma_low = sum(stockprice_history_short)/len(stockprice_history_short)
            stockprice_history_long = yf.Ticker(stock).history(period="70d")["Open"]
            ma_high = sum(stockprice_history_long)/len(stockprice_history_long)

            if(ma_high<ma_low and stockprice_history_short[0]<cash/10 and stock not in portfolio):
                candidates.append((stock,ma_low,ma_high,stockprice_history_short[0]))
                print(f"added {stock} as candidate")

    # Determine best candidates
    sorted_candidates=sorted(candidates,key=lambda x:(x[1]-x[2])/x[3],reverse=True)

    if len(sorted_candidates)>10:
        for stock in sorted_candidates[:10]:
            cash,portfolio = Buy(stock[0],portfolio,cash)
    else:
        for stock in sorted_candidates:
            cash,portfolio = Buy(stock[0],portfolio,cash)

    return cash,portfolio



def DecideSell(portfolio,cash):
    print("\nlooking for stocks to sell...")
    for stock in portfolio.keys():
        history = yf.Ticker(stock).history(period="1y")["Open"]
        #if stock has been held for at least 10 days we consider selling
        if datetime.strptime(portfolio[stock],"%Y-%m-%d") < datetime.today()+timedelta(days=10):
            bought_price = history[pd.Timestamp(portfolio[stock])-pd.Timedelta(days=2)]
            todays_price =history[0]
            if todays_price>bought_price:
                Sell(stock,portfolio,cash)

    return cash, portfolio
    #bought_date = portfolio[stock]

    #bought_price = history[bought_date]




        # ma_low = sum(history_short)/len(history_short)
        # history_long = yf.Ticker(stock).history(period="50d")["Open"]
        # ma_high = sum(history_long)/len(history_long)
        # if(ma_high<ma_low and history_short[0]<cash):
        #     cash,portfolio = Sell(stock,portfolio,cash)




    # An additional strategy is called the opportunity-cost sell method.
    # In this method, the investor owns a portfolio of stocks and sells a stock when a better opportunity presents itself.
    # This requires constant monitoring, research, and analysis of both their portfolio and potential new stock additions.
    # Once a better potential investment has been identified, the investor then reduces or eliminates a position in a current
    # holding that isn't expected to do as well as the new stock on a risk-adjusted return basis.


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