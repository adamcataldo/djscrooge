"""This file contains the XXX of the DJ Scrooge backtesting API.
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
from djscrooge.backtest import Commissions

class WellsPMACommissions(Commissions):
  """Computes the commissions on a Wellstrade PMA account."""
  
  year = 1900
  trades_this_year = 0
  
  def buy_commissions(self, symbol, shares, price_per_share):
    if self.year != self.backtest.simulation_date.year:
      self.year = self.backtest.simulation_date.year
      self.trades_this_year = 0
    self.trades_this_year += 1
    if self.trades_this_year >= 100:
      return 495
    return 0
  
  def sell_commissions(self, symbol, shares, price_per_share):
    return self.buy_commissions(symbol, shares, price_per_share)

