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
from datetime import timedelta, date
import os
from collections import namedtuple
from djscrooge.library.end_of_day.mongodb_cache import warm_cache
from bson.code import Code

DailyReturn = namedtuple('DailyReturn', ['percentage', 'symbol'])

class BiggestLoser(Strategy):
  
  def after_initialization(self):
    pwd = os.path.dirname(__file__)
    symbols = []
    errors = 0.0
    with open(pwd + '/s_p_500_constituents') as f:
      for line in f:
        symbol = line.strip()
        if symbol != '':
          try:
            warm_cache(symbol, self.backtest.end_date)
            symbols.append(symbol)
          except:
            errors = errors + 1.0
    mapper = Code("""
    function () {
      loss = this.open - this.close
      emit(this.date, { "loss" : loss, "symbol" : this.symbol });
    }
    """)
    reducer = Code("""
    function (key, values) {
      result = { "loss" : -Infinity, "symbol" : "NONE" };
      for (var i = 0; i < values.length; i++) {
        if (values[i].loss > result.loss) {
          result.loss = values[i].loss;
          result.symbol = values[i].symbol;
        }
      }
      return result;
    }
    """)
    connection = Config().MONGODB_CONNECTION
    db = connection.djscrooge
    query = { 'symbol' : {'$in' : symbols}, 
             'date': {'$gte' : (self.backtest.start_date - timedelta(14)).toordinal(),
                      '$lte' : self.backtest.end_date.toordinal()}}
    results = db.prices.map_reduce(mapper, reducer, 'biggest_loser', query=query)
    last = None
    self.biggest_losers = {}
    for result in results.find():
      if last is None:
        last = result
      else:
        key = date.fromordinal(int(result['_id']))
        symbol = last['value']['symbol']
        self.biggest_losers[key] = symbol
        last = result
    self.holding = None
  
  def execute(self):
    backtest = self.backtest
    t = backtest.simulation_date
    if self.holding != self.biggest_losers[t]:
      if self.holding is not None:
        open_prices = backtest.end_of_day_class(self.holding, t, t).open_prices
        if len(open_prices) != 0:
          price = open_prices[0]
          for position in backtest.portfolio.get_positions(self.holding):
            shares = position.remaining_shares
            backtest.sell_shares(self.holding, shares, price)
      self.holding = self.biggest_losers[t]
      eod = backtest.end_of_day_class(self.holding, t, t)
      if len(eod.open_prices) > 0:
        price = eod.open_prices[0]
        shares = int(backtest.portfolio.cash / price)
        backtest.buy_shares(self.holding, shares, price)
