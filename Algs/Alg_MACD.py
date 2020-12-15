from typing import List, Any, Union

import yfinance
import pandas as pd
import ta
import plotly.graph_objects as go
from pandas import DataFrame, Series
from plotly.graph_objs import Scatter
from plotly.subplots import make_subplots
from datetime import date


# This returns the intersections between fast and signal MACD
# From https://towardsdatascience.com/algorithmic-trading-with-macd-and-python-fef3d013e9f3
def getMACD_intersections(signal : pd.Series, fast : pd.Series) :
    intersections = []
    insights: list[str] = []
    if len(signal) > len(fast):
        settle = len(fast)
    else:
        settle = len(signal)
    for i in range(settle - 1):
        if (signal[i + 1] < fast[i + 1]) != (signal[i] < fast[i]):
            if ((signal[i + 1] < fast[i + 1]), (signal[i] < fast[i])) == (True, False):
                insights.append('buy')
            else:
                insights.append('sell')
            intersections.append(i)
    return intersections, insights

# This returns the candlestic and the volume bar.
def makeCSPlot(df) -> [go.Candlestick,go.Bar]:

    # Get the time series in candlestick
    candlestick = go.Candlestick(x=df.index,
                                 open=df['Open'],
                                 high=df['High'],
                                 low=df['Low'],
                                 close=df['Close'])
    # Get the volumes as bar chart
    volumes = go.Bar(x=df.index, y=df['Volume'],opacity=0.2)

    return [candlestick,volumes]

# This returns a "green" or "red" color depending if the insight is "buy" or "sell"
# In the case the insight in not buy/sell, return blue
def LineColorFromInsight(insight):
    if insight == "buy":
        return "green"
    elif insight == "sell":
        return "red"
    else:
        return "blue"

# This function test the trades gain/loss based on the MACD algorithm
# df: Time series data
# intersections = The MACD_fast vs MACD_signal intersections
# insights =  The list containing the actions
# pat = Patience parameter: how long after the intersection was made, the trade is made.
# nsec = How many securities are traded

def TestTrades(df,intersections,insights,pat=1,nsec=1) :
    if len(intersections)<1:
        return 0
    profit=0
    #TODO check this algorithm! I'm not convinced this is the right metric
    for i in range(len(intersections) - pat):
        index = intersections[i]
        print(index)
        true_trade = None
        if df['Close'][index] <= df['Close'][index + pat]:
            print("Data Close at index",index,df['Close'][index],df.index[index])
            print("Data Close at index",index+pat,df['Close'][index+pat],df.index[index+pat])
            true_trade = 'buy'
        else:
            true_trade = 'sell'
    if true_trade != None:
        if insights[i] == true_trade:
            print(index,index+pat)
            profit += nsec*abs(df['Close'][index] - df['Close'][index + pat])
            print(df['Close'][index])
            print(df['Close'][index+pat])
        else:
            profit += -nsec*abs(df['Close'][index] - df['Close'][index + pat])
            print(df['Close'][index])
            print(df['Close'][index+pat])

    return profit

def testtrades_2(df,intersections, insights,pat=0,nsec=1,tax=0.2):
    #TODO Crosscheck this computation
    if len(intersections) < 1:
        return 0
    profit = 0
    buy_amount = 0
    sell_amount = 0
    offset = 0

    # Check if the last action was buying a security. If so then only compute up to n-1 actions.
    # Last profit will be computed differently.
    if (insights[-1] == "buy"):
        offset=1

    for i in range(len(intersections) - offset):
        index=intersections[i] + pat
        action_close_price = df['Close'][index]
        print("Action price:", df['Close'][index], insights[i])
        if insights[i] == "buy":
            buy_amount+=action_close_price
        else:
            sell_amount+=action_close_price

    profit = nsec*(sell_amount - buy_amount)
    if profit > 0:
        profit *= (1-tax)

    # Compute the profit for the last buy we made: check the price we bought with the current price.
    # Since that are unrealized gains we don't have to tax them.

    last_buy_close_price = df['Close'][intersections[-1]]
    current_price = df['Close'][-1]
    unrealized_profit = nsec*(current_price - last_buy_close_price)

    print(last_buy_close_price,current_price,unrealized_profit)

    return profit + unrealized_profit

def makefullplot(df,MACD_obj, intersections=[],insights=[]):

    # Form the candlestick and volume plots
    candlestick, volumes = makeCSPlot(df)

    # Create the macd trace for plotting and the macd histogram
    macd_fast: Scatter = go.Scatter(x=df.index, y=MACD_obj.macd())
    macd_histo = go.Bar(x=df.index, y=MACD_obj.macd_diff())
    macd_signal = go.Scatter(x=df.index, y=MACD_obj.macd_signal())

    # Create figure with secondary y-axis
    fig = make_subplots(rows=2, cols=1, specs=[[{"secondary_y": True}], [{"secondary_y": True}]])

    # Add the candle stick and the volumes to the figure
    fig.add_trace(candlestick, row=1, col=1, secondary_y=False)
    fig.add_trace(volumes, row=1, col=1, secondary_y=True)
    fig.layout.yaxis2.showgrid = False
    fig.update_layout(xaxis_rangeslider_visible=False)

    # Add the MACD and the MACD histogram
    fig.add_trace(macd_fast, row=2, col=1, secondary_y=True)
    fig.add_trace(macd_signal, row=2, col=1, secondary_y=True)
    fig.add_shape(type='line',
                  yref="y",
                  xref="x",
                  x0=df.index[0],  # x-axis min
                  y0=0,
                  x1=df.index[-1],  # x-axis max
                  y1=0,
                  line=dict(color='black', width=2, dash="dash"),
                  row=2,
                  col=1)
    fig.add_trace(macd_histo, row=2, col=1, secondary_y=True)
    ymax = MACD_obj.macd().max()
    ymin = MACD_obj.macd().min()
    fig.update_yaxes(range=[ymin * 1.2, ymax * 1.2], row=2, col=1)

    actions = [df.index[t] for t in intersections]

    for iaction in range(len(actions)):
        fig.add_shape(type='line',
                      yref='y',
                      xref='x',
                      x0=actions[iaction],
                      y0=ymin,
                      x1=actions[iaction],
                      y1=ymax,
                      line=dict(color=LineColorFromInsight(insights[iaction]), width=2, dash='dot'),
                      row=2,
                      col=1)

    fig.show()
    return fig



def main():
    print("MACD Alg")
    #Config:
    ticker="BTC-USD"
    StartDate = '2020-08-23'
    #Get some data
    today = date.today().strftime("%Y-%m-%d")
    #data: Union[Union[DataFrame, Series], Any] = yfinance.download(ticker, StartDate, today,interval='1h')
    data: Union[Union[DataFrame, Series], Any] = yfinance.download(ticker, period='6mo', interval='1d')
    print(data.head)
    print(data.columns)

    # Clean nan values
    data = ta.utils.dropna(data)

    print(type(data['Close']))
    #Compute the MACD
    #trends = ta.add_trend_ta(data,'High','Low','Close',True) #The ADX indicator is broken?

    #For longer trading slow = 26, fast = 12, signal = 9
    #For weekly trading slow = 35, fast = 5 , signal = 5
    #MACD_obj = ta.trend.MACD(data['Close'],n_slow=35,n_fast=5,n_sign=5)
    #MACD_obj = ta.trend.MACD(data['Close'], n_slow=26, n_fast=12, n_sign=9)
    MACD_obj = ta.trend.MACD(data['Close'])
    print(MACD_obj)

    intersections,insights = getMACD_intersections(MACD_obj.macd_signal(), MACD_obj.macd())
    print(intersections)
    print(insights)


    profit = TestTrades(data,intersections,insights,0,1)
    print("profit=",profit)
    profit_2 = testtrades_2(data,intersections,insights,0,0.1,tax=0.35)
    print("profit_2",profit_2)

    makefullplot(data,MACD_obj,intersections,insights)

if __name__ == "__main__":
    main()
