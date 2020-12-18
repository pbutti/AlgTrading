# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import argparse
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import robin_stocks as r
import robin_utils as ru
import ta

from dash.dependencies import Input, Output
from plotly.subplots import make_subplots

app = dash.Dash(__name__)

def main(): 
  # Parse command line arguments
  parser = argparse.ArgumentParser(description='')
  parser.add_argument("-c", action='store', dest='cred',
                      help="Path to credentials used to login to Robinhood.")
  args = parser.parse_args()
  
  # Login to robinhood
  ru.login(args.cred)

  app.layout = html.Div([
        html.Div(
          className="box", 
          children=[
            html.Div(id='current-info'),
            dcc.Interval(id='interval-component', interval=20000, n_intervals=0),
            html.Div(
              [
                "Security: ",
                dcc.Input(id='symbol-input', value='BABA', type='text', debounce=True),
              ]
            )
          ]
        ),
        html.Br(),
        html.Div([ 
          html.Button('1D', id='1d-button', n_clicks=0), 
          html.Button('1W', id='1w-button', n_clicks=0), 
          html.Button('1M', id='1m-button', n_clicks=0), 
          html.Button('3M', id='3m-button', n_clicks=0), 
          html.Button('1Y', id='1y-button', n_clicks=0), 
          html.Button('5Y', id='5y-button', n_clicks=0), 
          ]),
        dcc.Graph(id='candlestick-output'),
     ]
  )

  app.run_server(debug=True, host='localhost')

@app.callback(
  Output(component_id='current-info', component_property='children'),
  Input(component_id='symbol-input', component_property='value'),
  Input(component_id='interval-component', component_property='n_intervals')
)
def get_security_info(symbol, n):
  if 'BTC' not in symbol and 'ETH' not in symbol:
    latest_price = r.stocks.get_latest_price(symbol)
    historical   = r.stocks.get_stock_historicals(symbol, interval='day')

  else:
    crypto_price = r.crypto.get_crypto_quote(symbol)
    latest_price = [crypto_price["mark_price"]]
    historical   = r.crypto.get_crypto_historicals(symbol)

  price_diff = float(latest_price[0]) - float(historical[-1]['close_price'])
  price_diff_str = ''
  if price_diff > 0: price_diff_str = '( +$%s )' % round(price_diff, 2)
  else: price_diff = '( -$%s )' % price_diff
  return ('%s $%s %s ' % (symbol, 
    round(float(latest_price[0]), 2), price_diff_str))

@app.callback(
  Output(component_id='candlestick-output', component_property='figure'),
  Input(component_id='symbol-input', component_property='value'),
  Input(component_id='1d-button', component_property='n_clicks'),
  Input(component_id='1w-button', component_property='n_clicks'),
  Input(component_id='1m-button', component_property='n_clicks'),
  Input(component_id='3m-button', component_property='n_clicks'),
  Input(component_id='1y-button', component_property='n_clicks'),
  Input(component_id='5y-button', component_property='n_clicks')
)
def display_candlestick(symbol, 
    btn_1d, btn_1w, btn_1m, btn_3m, btn_1y, btn_5y):

  changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

  span = 'day'
  interval = '5minute'
  if '1d-button' in changed_id:
    span ='day'
    interval = '5minute'
  elif '1w-button' in changed_id:
    span ='week'
    interval = '10minute'
  elif '1m-button' in changed_id:
    span ='month'
    interval = 'hour'
  elif '3m-button' in changed_id:
    span ='3month'
    interval = 'day'
  elif '1y-button' in changed_id:
    span ='year'
    interval = 'day'
  elif '5y-button' in changed_id:
    span ='5year'
    interval = 'day'

  historicals_frame = ru.get_historicals(symbol, interval=interval, span=span)
  historicals_frame_day = ru.get_historicals(symbol, interval='5minute', span='day')
  historicals_frame = historicals_frame.append(historicals_frame_day.tail(1), ignore_index=True)
  macd_obj = ta.trend.MACD(historicals_frame['close_price'])

  fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.01)

  fig.add_trace( go.Candlestick(
      x=historicals_frame['begins_at'],
      open=historicals_frame['open_price'],
      high=historicals_frame['high_price'],
      low=historicals_frame['low_price'],
      close=historicals_frame['close_price'],
      decreasing_line_color='#ff5a87',
      decreasing_line_width=.5,
      decreasing_fillcolor='#ff5a87',
      increasing_line_color='#c3f53c',
      increasing_line_width=.5,
      increasing_fillcolor='#c3f53c',
    ), row=1, col=1
  )

  fig.add_trace( go.Scatter(x=historicals_frame['begins_at'],
                            y=macd_obj.macd()), row=2, col=1
               )
  fig.add_trace( go.Scatter(x=historicals_frame['begins_at'],
                            y=macd_obj.macd_signal()), row=2, col=1
               )

  fig.add_trace( go.Bar(x=historicals_frame['begins_at'],
                        y=macd_obj.macd_diff()), row=2, col=1
                )

  intersections, insights = ru.get_macd_intersections(macd_obj.macd_signal(),
                                                      macd_obj.macd())

  color = lambda n: '#c3f53c' if n == "buy" else '#ff5a87'
  for intersection, insight in zip(intersections, insights):
    fig.add_vline(
          x=historicals_frame['begins_at'][intersection],
          line_width=1,
          line_dash='dash',
          line_color=color(insight))

  fig.update_layout(xaxis_rangeslider_visible=False,
      margin=dict(l=20, r=20, t=0, b=20),
      height=750,
      plot_bgcolor='#100a20',
      paper_bgcolor='#100a20',
      font={'color': 'white', 'size': 12},
  )

  fig.update_xaxes(showgrid=True, gridwidth=2, gridcolor='#1e1733',
                   rangebreaks=[
                     dict(bounds=["sat", "mon"])
                   ]
  )
  fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#1e1733')

  return fig

if __name__ == '__main__':
  main() 
