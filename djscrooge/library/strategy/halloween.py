"""This file contains the halloween module of the Pengoe Backtesting API.
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
from datetime import date
from djscrooge.backtest import Strategy

class Halloween(Strategy):     
  
  def after_initialization(self):
    self.eod = self.backtest.get_end_of_day('SPY')
        
  def execute(self):
    current_date = self.backtest.simulation_date
    year = current_date.year
    eod = self.eod
    price_per_share = eod.open_prices[eod.get_index_from_date(self.backtest.simulation_date)]
    symbol = 'SPY'
    if current_date >= date(year, 4, 20) and current_date < date(year, 10, 20):
      portfolio = self.backtest.portfolio
      if symbol in portfolio.symbols:
        positions = portfolio.get_positions(symbol)
        for position in positions:
          shares = position.remaining_shares
          if shares > 0:
            self.backtest.sell_shares(symbol, shares, price_per_share, open_position=position)
    else:
      shares = int(self.backtest.portfolio.cash / price_per_share)
      if shares > 0:
        self.backtest.buy_shares(symbol, shares, price_per_share) 