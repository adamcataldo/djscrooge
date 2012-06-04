"""This file contains the BiggestLoser strategy of the DJ Scrooge backtesting API.
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
from djscrooge.backtest import Strategy
from djscrooge.config import Config
from datetime import timedelta, datetime
import os,sys
from collections import namedtuple

DailyReturn = namedtuple('DailyReturn', ['percentage', 'symbol'])

class BiggestLoser(Strategy):
  
  initialized = False
  
  def initialize_tables(self):
    eod_class = self.backtest.end_of_day_class
    start = self.backtest.start_date
    symbol = Config().BACKTEST_SYMBOL_FOR_ALL_DATES
    eod = eod_class(symbol, start - timedelta(21), start - timedelta(1))
    start = eod.dates[len(eod.dates) - 2]
    self.start_date_minus_one = eod.dates[len(eod.dates) - 1]
    end = self.backtest.end_date
    eod = eod_class(symbol, start, end)
    self.biggest_loser = {}
    for i in range(1, len(eod.dates)):
      t = eod.dates[i]
      percentage = ((1.0 * eod.adj_close_prices[i]) / eod.adj_close_prices[i - 1] - 1) * 100
      self.biggest_loser[t] = DailyReturn(percentage, symbol)
    pwd = os.path.dirname(__file__)
    sys.path.append(pwd)
    with open (pwd + '/s_p_500_constituents', 'r') as f:
      for line in f:
        symbol = line.strip()
        if symbol == '':
          continue
        eod = eod_class(symbol, start, end)    
        for i in range(1, len(eod.dates)):
          t = eod.dates[i]
          percentage = ((1.0 * eod.adj_close_prices[i]) / eod.adj_close_prices[i - 1] - 1) * 100
          if percentage < self.biggest_loser[t].percentage:
            self.biggest_loser[t] = DailyReturn(percentage, symbol)
  
  def execute(self):
    if not self.initialized:
      file_name = '/var/tmp/biggest_loser.txt'
      if os.path.exists(file_name):
        self.biggest_loser = {}
        with open(file_name, 'r') as f:
          for line in f:
            parts = line.split(',')
            d = datetime.strptime(parts[0], "%Y-%m-%d").date()
            percentage = float(parts[1])
            symbol = parts[2].strip()
            self.biggest_loser[d] = DailyReturn(percentage, symbol)
        self.start_date_minus_one = min(self.biggest_loser.keys())
      else:
        self.initialize_tables()
        with open(file_name, 'w') as f:
          for key in self.biggest_loser.keys():
            t = self.biggest_loser[key]
            f.write(str(key) + ',' + str(t.percentage) + ',' + t.symbol + '\n')
      self.initialized = True
    backtest = self.backtest
    t = backtest.simulation_date
    if t == self.backtest.dates[0]:
      t_minus_one = self.start_date_minus_one
    else:
      dates = backtest.dates
      eod = backtest.get_end_of_day(Config().BACKTEST_SYMBOL_FOR_ALL_DATES)
      t_minus_one = dates[eod.get_index_from_date(t) - 1]
    for symbol in list(backtest.portfolio.symbols):
      open_prices = backtest.end_of_day_class(symbol, t, t).open_prices
      if len(open_prices) == 0:
        continue
      price = open_prices[0]
      for position in backtest.portfolio.get_positions(symbol):
        shares = position.remaining_shares
        backtest.sell_shares(symbol, shares, price)
    symbol = self.biggest_loser[t_minus_one].symbol
    eod = backtest.end_of_day_class(symbol, t, t)
    if len(eod.open_prices) > 0:
      price = eod.open_prices[0]
      shares = int(backtest.portfolio.cash / price)
      backtest.buy_shares(symbol, shares, price)
