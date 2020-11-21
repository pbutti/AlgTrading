import yfinance
import pandas as pd
import ta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# This returns the intersections between fast and signal MACD  (lst_1 =
# From https://towardsdatascience.com/algorithmic-trading-with-macd-and-python-fef3d013e9f3
def getMACD_intersections(lst_1 : pd.Series, lst_2 : pd.Series) :
    #TODO: check this algorithm!
    intersections = []
    insights = []
    if len(lst_1) > len(lst_2):
        settle = len(lst_2)
    else:
        settle = len(lst_1)
    for i in range(settle - 1):
        if (lst_1[i + 1] < lst_2[i + 1]) != (lst_1[i] < lst_2[i]):
            if ((lst_1[i + 1] < lst_2[i + 1]), (lst_1[i] < lst_2[i])) == (True, False):
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

    #
    # Create the macd trace for plotting and the macd histogram
    macd_fast = go.Scatter(x=data.index,y=MACD_obj.macd())
    macd_histo   = go.Bar(x=data.index,y=MACD_obj.macd_diff())
    macd_signal  = go.Scatter(x=data.index,y=MACD_obj.macd_signal())

    # Create figure with secondary y-axis
    fig = make_subplots(rows=2,cols=1,specs=[[{"secondary_y": True}],[{"secondary_y" : True}]])

    # Add the candle stick and the volumes to the figure
    fig.add_trace(candlestick,row=1,col=1, secondary_y=False)
    fig.add_trace(volumes,row=1,col=1, secondary_y=True)
    fig.layout.yaxis2.showgrid = False

    # Add the MACD and the MACD histogram
    fig.add_trace(macd_fast,row=2,col=1,secondary_y=True)
    fig.add_trace(macd_signal,row=2,col=1,secondary_y=True)
    fig.add_shape(type='line',
                  yref="y",
                  xref="x",
                  x0=data.index[0],  #x-axis min
                  y0=0,
                  x1=data.index[-1], #x-axis max
                  y1=0,
                  line=dict(color='black', width=2,dash="dash"),
                  row=2,
                  col=1)
    fig.add_trace(macd_histo,row=2,col=1,secondary_y=True)
    fig.update_yaxes(range=[-10,10],row=2,col=1)
    intersections,insights = getMACD_intersections(MACD_obj.macd_signal(), MACD_obj.macd())
    print(intersections)
    print(insights)
    actions = [data.index[t] for t in intersections]
    print(actions)
    for action in actions:
        fig.add_shape(type='line',
                      yref='y',
                      xref='x',
                      x0=action,
                      y0=-10,
                      x1=action,
                      y1=10,
                      line=dict(color='green',width=2,dash='dot'),
                      row=2,
                      col=1)

    fig.show()

if __name__ == "__main__":
    main()
