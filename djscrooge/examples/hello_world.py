"""This file contains a Hello World example of the DJ Scrooge Backtesting API.
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
'''
Created on Mar 12, 2012

@author: adam
'''
from djscrooge.backtest import Backtest
from datetime import date
from djscrooge.library.end_of_day.yahoo import Yahoo
from djscrooge.library.strategy.buy_hold_spy import BuyHoldSPY
from djscrooge.library.taxes.california_taxes import CaliforniaTaxes
from djscrooge.library.commissions.wells_pma_commissions import WellsPMACommissions
from djscrooge.charting import chart_backtest



def main():
  start_date = date(2002,1,1)
  end_date = date(2012, 5, 15)
  buy_hold_test = Backtest(start_date, end_date, commissions_class=WellsPMACommissions, 
                      taxes_class=CaliforniaTaxes, strategy_class=BuyHoldSPY, 
                      end_of_day_class=Yahoo)
  chart_backtest(buy_hold_test, title='Buy & Hold S&P 500 Index (SPY)')
        
if __name__ == '__main__':
    main()