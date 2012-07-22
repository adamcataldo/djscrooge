"""This file contains the BuyHoldSPY of the DJ Scrooge backtesting API.
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

class BuyHoldSPY(Strategy):
  """This stratetegy tries to buy as much of the S&P 500 index as possible.
  
  It never sells shares. When, through dividend payouts or price drops, there
  is enough cash available to buy more shares it does. It always buys shares
  at the begninning of the day, so it uses the opening price for purchases.
  """
  
  def after_initialization(self):
    self.symbol = 'SPY'
  
  def execute(self):
    backtest = self.backtest
    cash = backtest.portfolio.cash
    data = backtest.get_end_of_day(self.symbol)
    index = data.get_index_from_date(backtest.simulation_date)
    open_price = data.open_prices[index]
    if cash > open_price:
      backtest.buy_shares(self.symbol, cash / open_price, open_price)
    