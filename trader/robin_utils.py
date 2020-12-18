
import collections
import logging 
import robin_stocks as r
import pandas as pd

from getpass import getpass

# Configure the logger
logging.basicConfig(format='[ trader ][ %(levelname)s ]: %(message)s', level=logging.DEBUG)

def login(credentials): 
  
  global logging

  logging.info('Login into Robinhood.')

  # Read the credentials from a file
  f = open(credentials, 'r')
  creds = f.readlines()

  login = r.login(creds[0], creds[1])

def merge_dict(dicts):
  merge_dict = collections.defaultdict(list)
  for d in dicts: 
    for key, value in d.items():
      merge_dict[key].append(value)

  return merge_dict

def follow_security(symbol, interval, cancel_events=False):

  global logging

  latest_price = r.stocks.get_latest_price(symbol)
  logging.info('%s : %s' % (symbol, latest_price))

# Only Bitcoin, Ethereum and Litecoin supported
def is_crypto(symbol):
  if symbol=="BTC" or symbol=="ETH" or symbol=="LTC":
    return True

  return False

def get_historicals(symbol, **kargs):
  interval = 'day'
  if 'interval' in kargs:
    interval = kargs['interval']

  span = 'year'
  if 'span' in kargs:
    span = kargs['span']

  if not is_crypto(symbol):

    rh_historicals = r.stocks.get_stock_historicals(symbol, interval=interval, span=span)

  else:
    rh_historicals = r.crypto.get_crypto_historicals(symbol,interval=interval, span=span)

  historicals_dict = merge_dict(rh_historicals)
  historicals_frame = pd.DataFrame.from_dict(historicals_dict)

  return historicals_frame

def get_macd_intersections(signal : pd.Series, fast : pd.Series): 
  
  intersections = []
  insights : list[str] = []
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


