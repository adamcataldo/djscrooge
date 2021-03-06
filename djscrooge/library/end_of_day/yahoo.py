"""This file contains the Yahoo EndOfDay subclass of the DJ Scrooge Backtesting API.
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

from djscrooge.backtest import EndOfDay
from djscrooge.backtest import Split
from urllib2 import urlopen
from datetime import date
from time import sleep

def robust_urlopen(url):
  for i in [0, 1, 2]:
    try:
      data = urlopen(url)
      return data
    except Exception, e:
      i = i + 1
      if i < 3:
        sleep(i)
      else:
        raise e
  
class HeadingCsv(object):
  """A class for parsing Csv files with headings.
  
  When iterating over this class, each item is a dictionary, where the keys
  are headings and the values are 
  """
  
  def __init__(self, file_handle):
    """Initialize the Object from the given file handle."""
    self.file_handle = file_handle
    line = file_handle.readline()
    if line == '':
      raise IOError('No heading column found.')
    self.headings = line.rstrip().split(',')
   
  def __iter__(self):
    """Return self as the iterator."""
    return self
  
  def next(self):
    """Return the next non-column row and return the corresponding dictionary."""
    line = self.file_handle.readline()
    if line == '':
      raise StopIteration
    data = line.rstrip().split(',')
    result = {}
    for i in range(0, len(data)):
      result[self.headings[i]] = data[i]
    return result

class Yahoo(EndOfDay):
  """An EndOfDay object using Yahoo's REST API."""
  
  def __init__(self, symbol, start_date, end_date):
    """Construct a new Yahoo EndOfDay object."""
    self.symbol = symbol
    super(Yahoo, self).__init__(symbol, start_date, end_date)
    url = 'http://ichart.yahoo.com/table.csv?s=' + symbol
    url += '&a={0}&b={1}&c={2}'.format(start_date.month - 1, start_date.day, start_date.year)
    url += '&d={0}&e={1}&f={2}'.format(end_date.month - 1, end_date.day, end_date.year)
    data = robust_urlopen(url)
    csv = HeadingCsv(data)
    for line in csv:
      dateparts = line['Date'].split('-')
      self.dates.append(date(int(dateparts[0]), int(dateparts[1]), int(dateparts[2])))
      self.open_prices.append(int(line['Open'].replace('.', '')))
      self.high_prices.append(int(line['High'].replace('.', '')))
      self.low_prices.append(int(line['Low'].replace('.', '')))
      self.close_prices.append(int(line['Close'].replace('.', '')))
      self.adj_close_prices.append(int(line['Adj Close'].replace('.', '')))
      self.volumes.append(int(line['Volume']))
    self.open_prices.reverse()
    self.high_prices.reverse()
    self.low_prices.reverse()
    self.close_prices.reverse()
    self.adj_close_prices.reverse()
    self.dates.reverse()
    self.volumes.reverse()
    url = url.replace('table.csv', 'x')
    url += '&g=v&y=0'
    data = robust_urlopen(url)
    self.dividends = [None] * len(self.dates)
    self.splits = [None] * len(self.dates)
    for line in data:
      parts = line.split(',')
      if parts[0] == 'DIVIDEND':
        datestr = parts[1].strip()
        dateobj = date(int(datestr[0:4]), int(datestr[4:6]), int(datestr[6:]))
        dividend = float(parts[2].strip()) * 100
        self.dividends[self.get_index_from_date(dateobj)] = dividend
      elif parts[0] == 'SPLIT':
        datestr = parts[1].strip()
        dateobj = date(int(datestr[0:4]), int(datestr[4:6]), int(datestr[6:]))
        split = parts[2].strip().split(':')
        try:
          self.splits[self.get_index_from_date(dateobj)] = Split(int(split[0]), int(split[1]))
        except TypeError:
          if len(self.dates) > 0 and self.dates[0] < dateobj:
            array_index = 1
            while array_index < len(self.dates):
              if self.dates[array_index] > dateobj:
                break
              else:
                array_index += 1
            ratio = int(split[1]) * 1.0 / int(split[0])
            synthetic_price = int(self.close_prices[array_index - 1] * ratio)
            self.dates.insert(array_index, dateobj)
            self.open_prices.insert(array_index, synthetic_price)
            self.high_prices.insert(array_index, synthetic_price)
            self.low_prices.insert(array_index, synthetic_price)
            self.close_prices.insert(array_index, synthetic_price)
            self.adj_close_prices.insert(array_index, synthetic_price)
            self.volumes.insert(array_index, 0)
            self.dividends.insert(array_index, None)
            self.splits.insert(array_index, Split(int(split[0]), int(split[1])))
            self.initialize_date_index()
          else:
            raise
          
  def get_current_price_and_market_cap(self):
    """Return the latest (price, market_cap) from Yahoo. Both are reported 
    in dollar amounts, given as floats.
    """
    url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=l1j1' % self.symbol
    f = robust_urlopen(url)
    data = f.read()
    parts = data.split(',')
    price = float(parts[0].replace('.', ''))
    parts[1] = parts[1].strip()
    if parts[1].endswith('M'):
      market_cap = float(parts[1][0:-1]) * 1.0e6
    elif parts[1].endswith('B'):
      market_cap = float(parts[1][0:-1]) * 1.0e9
    else:
      market_cap = float(parts[1])
    return (price, market_cap)