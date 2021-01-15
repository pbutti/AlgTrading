
import argparse
import collections
import logging
import pandas as pd
import robin_stocks as r
import time
import yaml

logging.basicConfig(format='[ HODL ][ %(levelname)s ]: %(message)s',
                    level=logging.INFO)

def merge_dict(dicts):
  merge_dict = collections.defaultdict(list)
  for d in dicts: 
    for key, value in d.items():
      merge_dict[key].append(value)

  return merge_dict

def main(): 

  # Parse command line arguments
  parser = argparse.ArgumentParser(description='')
  parser.add_argument("-c", action='store', dest='config',
                      help="Path to the configuration for this bot.")
  args = parser.parse_args()
 
  # If a configuration file was not specified, warn the user and exit.
  if not args.config :
    parser.error('A configuration file needs to be specified.')
 
  # Parse the configuration file.
  logging.info('Parsing configuration located at %s' % args.config.strip()) 
  config = yaml.load(open(args.config.strip(), 'r'), Loader=yaml.FullLoader)

  logging.info('Login into RobinHood.')
  login = r.login(config['user'], config['pass'])

  coin = config['coin'].strip()
  logging.info('Trading %s ... wish me luck!' % coin)

  while True:
    hist = r.get_crypto_historicals(coin, interval='15second', span='hour', 
                                    bounds='24_7')

    hist_dict = merge_dict(hist)
    hist_frame = pd.DataFrame.from_dict(hist_dict)
    logging.info('Current price of %s: %s' % (coin, hist_frame['close_price'].iloc[-1]))

    time.sleep(15)
  
if __name__ == '__main__': 
  main()

  
