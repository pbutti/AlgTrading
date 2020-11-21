import yfinance
import pandas as pd
import ta
from matplotlib import pyplot as plt
from datetime import datetime
import mplfinance as fplt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

def main():
    print("MACD Alg")
    #Get some data
    data = yfinance.download('AAPL', '2019-11-19', '2020-11-20')

    # Form the candlestick and volume plots
    candlestick,volumes = makeCSPlot(data)

    print(data.columns)
    # Clean nan values
    df = ta.utils.dropna(data)

    print(type(data['Close']))
    #Compute the MACD
    # macd = ta.add_trend_ta(data,'High','Low','Close',True) #The ADX indicator is broken?

    MACD_obj = ta.trend.MACD(data['Close'])

    # Create the macd trace for plotting
    macd_scatter = go.Scatter(x=data.index,y=MACD_obj.macd())

    # Create figure with secondary y-axis
    fig = make_subplots(rows=2,cols=1,specs=[[{"secondary_y": True}],[{"secondary_y" : False}]])

    # Add the candle stick and the volumes to the figure
    fig.add_trace(candlestick,row=1,col=1, secondary_y=True)
    fig.add_trace(volumes,row=1,col=1, secondary_y=False)
    fig.layout.yaxis2.showgrid = False


    fig.add_trace(macd_scatter,row=2,col=1)
    fig.show()

    #plotly_fig.show()

if __name__ == "__main__":
    main()
