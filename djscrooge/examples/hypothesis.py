"""This file contains the hypothesis module of the Pengoe Backtesting API.
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
from djscrooge.backtest import Backtest, Portfolio, Taxes
from djscrooge.library.commissions.wells_pma_commissions import WellsPMACommissions
from djscrooge.library.strategy.buy_hold_spy import BuyHoldSPY
from djscrooge.hypothesis_test import hypothesis_test, get_log_daily_returns
from djscrooge.library.strategy.halloween import Halloween
from djscrooge.library.end_of_day.yahoo import Yahoo

def main():
  start_date = date(2002,1,1)
  end_date = date(2012, 7, 7)
  buy_hold = Backtest(start_date, end_date, commissions_class=WellsPMACommissions, 
                      strategy_class=BuyHoldSPY, taxes_class=Taxes,
                      end_of_day_class=Yahoo, portfolio=Portfolio(1e7))
  halloween = Backtest(start_date, end_date, commissions_class=WellsPMACommissions, 
                                 strategy_class=Halloween, taxes_class=Taxes,
                                 end_of_day_class=Yahoo, portfolio=Portfolio(1e7))
  buy_hold_returns = get_log_daily_returns(buy_hold)
  halloween_returns = get_log_daily_returns(halloween)
  (excess_return, p_value) = hypothesis_test(halloween_returns, buy_hold_returns)
  print "Excess return of Halloween: " + str(excess_return) + "%"
  print "p-value of Halloween: " + str(p_value) + "%"
  
if __name__ == '__main__':
    main()
