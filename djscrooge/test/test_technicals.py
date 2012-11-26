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
from djscrooge.technicals import simple_moving_average, accumulate, \
  channel_breakout, channel_normalization, on_balance_volume, \
  accumulation_distribution_volume, money_flow, negative_volume_index, \
  advance_decline_ratio, net_volume_ratio, high_low_ratio, capm
from proboscis import test
from proboscis.asserts import assert_equal, assert_true

@test
def test_simple_moving_average():
  """Test the simple_moving_average function."""
  
  expected = [0.0, 0.5, 1.5, 2.5, 3.5, 4.5]
  actual = simple_moving_average(range(0, 6), 2)
  assert_equal(actual, expected)
  
@test
def test_accumulate():
  """Test the accumulate function."""
  values = [1, 2, 3, 4]
  actual = accumulate(values)
  expected = [1, 3, 6, 10]
  assert_equal(actual, expected)
    
@test
def test_channel_breakout():
  """Test the channel_breakout function."""
  values = [0, 1, 4, 2, 3, 1, 6, 0]
  window = 2
  actual = channel_breakout(values, window)
  expected = [0, 0, 1, 0, 0, -1, 1, -1]
  assert_equal(actual, expected)
  
@test
def test_channel_normalization():
  """Test the channel_normalization function."""
  values = [0, 1, 4, 2, 3, 1, 6, 0]
  window = 3
  actual = channel_normalization(values, window)
  expected = [50.0, 100.0, 100.0, 100.0/3.0, 50.0, 0.0, 100.0, 0.0]
  assert_equal(actual, expected)
  
@test
def test_on_balance_volume():
  """Tets the on_balance_volume function."""
  prices = [1, 2, 2, 1]
  volumes = [1, 2, 3, 4]
  actual = on_balance_volume(prices, volumes)
  expected = [0, 2, 0, -4]
  assert_equal(actual, expected)
  
@test
def test_accumulation_distribution_volume():
  """Test the accumulation_distribution_volume function."""
  high_prices = [4, 4, 4, 4, 4]
  low_prices = [0, 0, 0, 0, 0]
  close_prices = [2, 1, 3, 0, 4]
  volumes = [1, 1, 1, 1, 1]
  actual = accumulation_distribution_volume(high_prices, low_prices, close_prices, volumes)
  expected = [0.0, -0.5, 0.5, -1.0, 1.0]
  assert_equal(actual, expected)  

@test
def test_money_flow():
  """Test the money_flow function."""
  high_prices = [4, 4, 4, 4, 4]
  low_prices = [0, 0, 0, 0, 0]
  close_prices = [2, 1, 3, 0, 4]
  volumes = [1, 1, 1, 1, 1]
  actual = money_flow(high_prices, low_prices, close_prices, volumes)
  expected = [0.0, -0.5 * (5.0/3.0), 0.5 * (7.0/3.0), -1.0 * (4.0/3.0), 1.0 * (8.0/3.0)]
  assert_equal(actual, expected)
  
@test
def test_negative_volume_index():
  """Test the negative_volume_index function."""
  prices = [1, 2, 4, 8]
  volumes = [1, 2, 1, 2]
  actual = negative_volume_index(prices, volumes)
  expected = [0.0, 0.0, 100.0, 0.0]  
  assert_equal(actual, expected)
  
@test
def test_advance_decline_ratio():
  """Test the advance_decline_ratio function."""
  advancing_issues = [1, 2, 3]
  declining_issues = [3, 2, 1]
  unchanged_issues = [1, 0, 2]
  actual = advance_decline_ratio(advancing_issues, declining_issues, unchanged_issues)
  expected = [-0.4, 0.0, 1.0 / 3.0]
  assert_equal(actual, expected)

@test
def test_net_volume_ratio():
  """Test the net_volume_ratio function."""
  up_volume = [1, 2, 3]
  down_volume = [3, 2, 1]
  unchanged_volume = [1, 0, 2]
  actual = net_volume_ratio(up_volume, down_volume, unchanged_volume)
  expected = [-0.4, 0.0, 1.0 / 3.0]
  assert_equal(actual, expected)

@test
def test_high_low_ratio():
  """Test the high_low_ratio function."""
  advancing_issues = [1, 2, 3]
  declining_issues = [3, 2, 1]
  unchanged_issues = [1, 0, 2]
  new_highs = [1, 2, 3]
  new_lows = [3, 2, 1]
  actual = high_low_ratio(advancing_issues, declining_issues, unchanged_issues, new_highs, new_lows)
  expected = [-0.4, 0.0, 1.0 / 3.0]
  assert_equal(actual, expected)

@test
def test_capm():
  """Test the camp function."""
  investment = [1.0, 1.21, 4.84]
  market = [1.0, 1.1, 2.2]
  (alpha, beta, r) = capm(investment, market)
  assert_true(abs(alpha) < 1.0e-8)
  assert_true(abs(beta - 2.0) < 1.0e-8)
  assert_true(abs(r - 1.0) < 1.0e-8)

if __name__ == "__main__":
  from proboscis import TestProgram
  TestProgram().run_and_exit()
