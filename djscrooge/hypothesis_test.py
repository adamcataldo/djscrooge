"""This file contains the hypothesis_test module of the Pengoe Backtesting API.
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

from numpy import mean, log, exp
from random import randint

def hypothesis_test(test_backtest, benchmark_backtest):
  """
  Tests the hypothesis that the test_backetst will NOT have a greater return than the benchmark_backtest.
  
  Parameters:
    test_backtest -- The backtest of the strategy under test.
    benchmark_backtest -- The backtest of the benchmark strategy, which must be computed over the same
                          range of days as the test_backtest.
    
  Returns: (excess_return, p_value):
    excess_return -- The average daily return of the strategy under test, after subtracting out the
                     benchmark returns. The excess returns are given as an annualized percantage,
                     assuming 252 trading days per year. During computation log of returns are used.
    p_value -- the probability the excess return was a fluke, given as a percentage.
  
  If the excess_return is positive, and the p_value is less than 5.0%, it is reasonable to infer that
  the strategy under test will outperform the benchmark in the near future. 
  """
  benchmark_returns = get_log_daily_returns(benchmark_backtest)
  benchmark_mean = mean(benchmark_returns)
  test_returns = get_log_daily_returns(test_backtest)
  n = len(test_returns)
  for i in range(0, n):
    test_returns[i] -= benchmark_mean
  test_mean = mean(test_returns)
  for i in range(0, n):
    test_returns[i] -= test_mean
  k = 5000
  samples = [0.0] * n
  test_means = [0.0] * k
  for i in range(0, k):
    for j in range(0, n):
      x = randint(0, n - 1)
      samples[j] = test_returns[x]
    test_means[i] = mean(samples)
  p_value = 0.0
  for i in range(0, k):
    if test_mean <= test_means[i]:
      p_value += 1.0
  p_value /= k
  test_mean *= 252
  test_mean = (exp(test_mean) - 1) * 100
  return (test_mean, p_value * 100.0)
    
def get_log_daily_returns(backtest):
  """Gets the log daily returns of the given test.
  
  The log-daily return of day i is computed as ln(open_price[i+2] / open_price[i+1])
  """
  returns = [0.0] * (len(backtest.open_values) - 2)
  for i in range(0, len(returns)):
    returns[i] = log(backtest.open_values[i+2] * 1.0 / backtest.open_values[i+1])
  return returns
    