"""This file contains the MongodbCache class of the Pengoe Backtesting API.
Copyright (C) 2012  James Adam Cataldo

    This file is part of Pengoe.

    Pengoe is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Pengoe.  If not, see <http://www.gnu.org/licenses/>.
"""
from djscrooge.backtest import EndOfDay, Split
from djscrooge.config import Config
from datetime import date
from pymongo import ASCENDING

class MongodbCache(EndOfDay):
  """An EndOfDay object which uses MongoDB as a backing store.
  
  When the cache does not have up-to-date end-of-day data for a symbol,
  it uses the underlying EndOfDay class specified in:
    djscrooge.config.Config.CACHE_END_OF_DAY_SOURCE_CLASS
    
  When the class is created, it retrieves a new pymongo.Connection from:
    djscrooge.config.MONGODB_CONNECTION
  """
  
  def __init__(self, symbol, start_date, end_date):
    """Creates the MongodbCache object."""
    super(MongodbCache, self).__init__(symbol, start_date, end_date)
    self.symbol = symbol
    self.start_date = start_date
    self.end_date = end_date
    connection = Config().MONGODB_CONNECTION  
    db = connection.djscrooge
    self.db = db
    symbols = db.symbols
    data = symbols.find_one({'symbol' : symbol})
    if data is None:
      self.add_symbol()
    elif end_date.toordinal() > data['updated_to']:
      self.remove_symbol()
      self.add_symbol()
    prices = db.prices.find({'symbol' : symbol, 
                             'date' : {'$gte': start_date.toordinal(), 
                                       '$lte': end_date.toordinal()}})
    for price in prices:
      self.dates.append(date.fromordinal(price['date']))
      self.open_prices.append(price['open'])
      self.high_prices.append(price['high'])
      self.low_prices.append(price['low'])
      self.close_prices.append(price['close'])
      self.adj_close_prices.append(price['adj_close'])
      self.volumes.append(price['volume'])
      if price.has_key('dividend'):
        self.dividends.append(price['dividend'])
      else:
        self.dividends.append(None)
      if price.has_key('split_numerator'):
        self.splits.append(Split(price['split_numerator'], price['split_denominator']))
      else:
        self.splits.append(None)
    
  def add_symbol(self):
    """Adds the symbol to the cache."""
    data = {'symbol' : self.symbol,
            'updated_to' : self.end_date.toordinal()}
    self.db.symbols.insert(data)
    self.db.symbols.ensure_index('symbol')
    eod = Config().CACHE_END_OF_DAY_SOURCE_CLASS(self.symbol, date(1900,1,1), self.end_date)
    for i in range(0, len(eod.dates)):
      price = {'symbol' : self.symbol,
               'date' : eod.dates[i].toordinal(),
               'open' : eod.open_prices[i],
               'high' : eod.high_prices[i],
               'low' : eod.low_prices[i],
               'close' : eod.close_prices[i], 
               'adj_close' : eod.adj_close_prices[i],
               'volume' : eod.volumes[i]}
      if eod.dividends[i] is not None:
        price['dividend'] = eod.dividends[i]
      if eod.splits[i] is not None:
        price['split_numerator'] = eod.splits[i].numerator
        price['split_denominator'] = eod.splits[i].denominator
      self.db.prices.insert(price)
      self.db.prices.ensure_index([('symbol', ASCENDING), ('date', ASCENDING)])
      
  def remove_symbol(self):
    """Removes stale data from the cache."""
    self.db.prices.remove({'symbol' : self.symbol})
    self.db.symbols.remove({'symbol' : self.symbol})
    
    
def warm_cache(symbol, end_date):
  """Warm the cache with the given symbol, up to the given end date."""
  MongodbCache(symbol, date(1900,1,1), end_date)