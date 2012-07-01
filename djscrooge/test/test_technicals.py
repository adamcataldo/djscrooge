"""This file contains tests for the technicals module of the DJ Scrooge backtesting API.
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
from proboscis import test
from proboscis.asserts import assert_equal
from djscrooge.technicals import simple_moving_average, annulaized_return
from djscrooge.backtest import EndOfDay
from datetime import date, timedelta

@test
def test_simple_moving_average():
  """Test the simple_moving_average function."""
  end_of_day = EndOfDay('FOO', date(2000,1,1), date(2000,1,1) + timedelta(5))
  end_of_day.dates = []
  end_of_day.dates.append(date(2000,1,1))
  end_of_day.adj_close_prices.append(0)
  for i in range(1, 6):
    end_of_day.dates.append(end_of_day.dates[i - 1] + timedelta(1))
    end_of_day.adj_close_prices.append(i)
  expected = [0.0, 0.5, 1.5, 2.5, 3.5, 4.5]
  actual = simple_moving_average(end_of_day, 2)
  assert_equal(actual, expected)
  
@test
def test_annualized_return():
  """Test the annualized_return function."""
  start = date(2001, 1, 1)
  end = date(2005, 1, 1)
  actual = annulaized_return(1, 16, start, end)
  assert_equal(actual, 100.0)
  
if __name__ == "__main__":
  from proboscis import TestProgram
  TestProgram().run_and_exit()