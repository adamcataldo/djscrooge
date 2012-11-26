"""This file contains the CaliforniaTaxes class of the DJ Scrooge backtesting API.
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
from djscrooge.backtest import Taxes
from datetime import timedelta

class CaliforniaTaxes(Taxes):
  """Computes state and federal taxes in California, assuming the top income bracket.
  
  This would be best for high-earners in California, who have some other source of income.
  This means all stock transactions will be taxed at the highest rate.
  """
  current_year = 1900
  long_term_gain = 0
  short_term_gain = 0
  long_term_paid = 0
  short_term_paid = 0
  
  def is_long_term(self, purchase_date):
    if purchase_date.year % 4 == 0:
      delta = timedelta(366)
    else:
      delta = timedelta(365)
    if (self.backtest.simulation_date >= purchase_date + delta):
      return True
    return False
  
  def get_tax(self, new_gain, tax_rate, total_gain, total_paid):
    total_gain += new_gain
    total_tax = tax_rate * total_gain
    tax_owed = int(total_tax - total_paid)
    if tax_owed < 0 and -tax_owed > total_paid:
      tax_owed = -total_paid
    total_paid += tax_owed
    return (tax_owed, total_gain, total_paid)
      
  def sell_tax(self, symbol, shares, gain_per_share, purchase_date):
    if purchase_date.year != self.current_year:
      self.current_year = purchase_date.year
      self.long_term_gain = 0
      self.short_term_gain = 0
      self.long_term_paid = 0
      self.short_term_paid = 0
    gain = shares * gain_per_share
    if self.is_long_term(purchase_date):
      tax_rate = 0.15 + 0.093
      (tax, self.long_term_gain, self.long_term_paid) = self.get_tax(gain, tax_rate, self.long_term_gain, self.long_term_paid)
      return tax
    else:
      tax_rate = 0.35 + 0.093
      (tax, self.short_term_gain, self.short_term_paid) = self.get_tax(gain, tax_rate, self.short_term_gain, self.short_term_paid)
      return tax

  def dividend_tax(self, symbol, amount, purchase_date):
    tax = 0.35 + 0.093
    if self.is_long_term(purchase_date):
      tax = 0.15 + 0.093
    return int(round(tax * amount))
  