import yfinance
import pandas as pd
import ta
from matplotlib import pyplot as plt
from datetime import datetime
import mplfinance as fplt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def makeCSPlot(df) -> go.Figure:

    # Get the time series in candlestick
    candlestick = go.Candlestick(x=df.index,
                                 open=df['Open'],
                                 high=df['High'],
                                 low=df['Low'],
                                 close=df['Close'])
    # Get the volumes as bar chart
    volumes = go.Bar(x=df.index, y=df['Volume'],opacity=0.2)

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y":True}]])

    # Add the candle stick and the volumes to the figure
    fig.add_trace(candlestick,secondary_y=True)
    fig.add_trace(volumes,secondary_y=False)

    fig.layout.yaxis2.showgrid=False

    return fig

def main():
    print("MACD Alg")
    #Get some data
    data: pandas.DataFrame = yfinance.download('AAPL', '2020-1-1', '2020-11-18')
    print(data.columns)
    print(data.index)
    print(data.head())
    fig = plt.figure()
    data['Adj Close'].plot()
    plotly_fig = makeCSPlot(data)
    plotly_fig.show()

if __name__ == "__main__":
    main()
