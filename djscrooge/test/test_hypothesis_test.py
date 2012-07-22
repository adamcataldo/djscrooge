"""This file contains the test_hypothesis_test of the DJ Scrooge backtesting API.
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
from djscrooge.backtest import Backtest
from datetime import date
from djscrooge.hypothesis_test import get_log_daily_returns, hypothesis_test
from proboscis.asserts import assert_equal, assert_true
from math import exp
from numpy import power

def get_backtest_from_open_values(open_values):
  """Gets a mock Backtest object with the given open_values."""
  backtest = Backtest(date(1900,1,1), date(1900,1,1))
  backtest.open_values = open_values
  return backtest

@test(groups=['log_returns'])
def test_get_log_daily_returns():
  """Test the get_log_daily_returns function."""
  backtest = get_backtest_from_open_values([1, exp(1), exp(2), exp(3)])
  actual = get_log_daily_returns(backtest)
  assert_equal(actual, [1.0, 1.0])

@test(depends_on_groups=['log_returns'])
def test_hypothesis_test():
  """Test the hypthosis_test function."""
  base = power(2.0, 1.0/252.0)
  benchmark_backtest = get_backtest_from_open_values([1, 1*base, 1*base**2, 1*base**3])
  test_backtest = get_backtest_from_open_values([1, 1*base**2, 1*base**4, 1*base**6])
  benchmarkt_returns = get_log_daily_returns(benchmark_backtest)
  test_returns = get_log_daily_returns(test_backtest)
  (actual_mean, actual_p_value) = hypothesis_test(test_returns, benchmarkt_returns)
  assert_true(abs(actual_mean - 100.0) < 0.000001)
  assert_equal(actual_p_value, 0.0)

if __name__ == "__main__":
  from proboscis import TestProgram
  TestProgram().run_and_exit()