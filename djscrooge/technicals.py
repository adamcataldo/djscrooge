"""This file contains the technicals module of the DJ Scrooge backtesting API.
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
from copy import copy
from numpy import mean
from math import log
from scipy.stats.stats import linregress

def simple_moving_average(values, window):
  """Calculates a simple moving average of the values.
  
  values -- The list of values to calculate the average on.
  window -- The window length of the moving average.
  """
  moving_average = []
  for i in range(0, len(values)):
    if i < window:
      moving_average.append(sum(values[0:(i+1)]) * 1.0 / (i + 1))
    else:
      moving_average.append(sum(values[(i+1-window):(i+1)]) * 1.0 / window)
  return moving_average

def accumulate(values):
  """Accumulates values in the series.
  
  result[i] = sum(values[0:i])
  """
  result = copy(values)
  for i in range(1, len(result)):
    result[i] += result[i-1]
  return result

def channel_breakout(values, window):
  """Calculates channel breakouts.
  
  Returns: 0, when there was no breakout, or when the index is less than the window size
           1, when there was a postive breakout
          -1, when there was a negative breakout
  
  values -- The list of values to calculate the average on.
  window -- The window length of the moving average.
  """
  n = len(values)
  results = [0] * n
  for i in range(window, n):
    value = values[i]
    sub_array = values[i-window:i]
    if value > max(sub_array):
      results[i] = 1
    elif value < min(sub_array):
      results[i] = -1
  return results

def channel_normalization(values, window):
  """Calculates channel-normalized values.
  Returns: 50.0, when the value is in the middle of the channel, or for the first index
           100.0, when at the top of the channel
           0.0, when at the bottom of the channel
  
  values -- The list of values to calculate the average on.
  window -- The window length of the moving average.  
  """
  n = len(values)
  results = [50.0] * n
  for i in range(1, window):
    sub = values[0:i+1]
    s_min = min(sub)
    s_max = max(sub)
    s = values[i]
    if s_min < s_max:
      results[i] = 100.0 * (s - s_min) / (s_max - s_min)
  for i in range(window, n):
    sub = values[i+1-window:i+1]
    s_min = min(sub)
    s_max = max(sub)
    s = values[i]
    if s_min < s_max:
      results[i] = 100.0 * (s - s_min) / (s_max - s_min)
  return results

def on_balance_volume(prices, volumes):
  """Returns the on-balance volume for each day.
  
  The prices and volumes must be the same length. The on-balance volume
  is volume times:
    1 if the price went up from the previous day
    0 if it staid the same
    -1 if it went down.
  """
  n = len(prices)
  result = [0] * n
  for i in range(1, n):
    if prices[i] > prices[i-1]:
      result[i] = volumes[i]
    elif prices[i] < prices[i-1]:
      result[i] = -volumes[i]
  return result 

def accumulation_distribution_volume(high_prices, low_prices, close_prices, volumes):
  """Returns the accumulation/distribution volume (ADV) for each day.
  
  The daily range factor is defined as:
    [(close - low) - (high - close)]/(high - low)
    
  The ADV is then the volume times the range factor.
  """
  n = len(high_prices)
  result = [0.0] * n
  for i in range(0, n):
    if high_prices[i] > low_prices[i]:
      range_factor = ((close_prices[i] - low_prices[i]) - (high_prices[i] - close_prices[i])) * 1.0 / (high_prices[i] - low_prices[i])
    else:
      range_factor = 0.0
    result[i] = range_factor * volumes[i]
  return result

def money_flow(high_prices, low_prices, close_prices, volumes):
  """Returns the money flow for each day. 
  
  This is the ADV multiplied by the average of high, low, and close prices.
  """
  result = accumulation_distribution_volume(high_prices, low_prices, close_prices, volumes)
  n = len(result)
  for i in range(0, n):
    result[i] *= mean([high_prices[i], low_prices[i], close_prices[i]])
  return result

def negative_volume_index(prices, volumes):
  """Returns the negative volume index for each day.
  
  This is the daily return (as a percentage) when the volume is declining, and zero otherwise.
  """
  n = len(prices)
  result = [0.0] * n
  for i in range(1, n):
    if volumes[i] < volumes[i-1]:
      result[i] = (prices[i] * 1.0 / prices[i-1] - 1.0) * 100.0
  return result

def advance_decline_ratio(advancing_issues, declining_issues, unchanged_issues):
  """Computes the daily advance/decline ratio.
  
  advancing_issues -- The number of issues in the index that advanced since the last day, as a list.
  declineing_issues -- The number of issues in the index that declined since the last day, as a list.
  unchanged_issues -- The number of issues in the index that stayed put since the last day, as a list.
  """
  n = len(advancing_issues)
  result = [0.0] * n
  for i in range(0, n):
    result[i] = (advancing_issues[i] - declining_issues[i]) * 1.0 / (advancing_issues[i] + declining_issues[i] + unchanged_issues[i])
  return result

def net_volume_ratio(up_volume, down_volume, unchanged_volume):
  """Computes the net-volume ratio.
  
  up_volume -- The volume advancing issues since the last day, as a list.
  down_volume -- The volume of declining issues, as a list.
  unchanged_volume -- The volume of unchanged issues, as a list.
  """
  n = len(up_volume)
  result = [0.0] * n
  for i in range(0, n):
    result[i] = (up_volume[i] - down_volume[i]) * 1.0 / (up_volume[i] + down_volume[i] + unchanged_volume[i])
  return result

def high_low_ratio(advancing_issues, declining_issues, unchanged_issues, new_highs, new_lows):
  """Computes the daily high/low ratio.
  
  advancing_issues -- The number of issues in the index that advanced since the last day, as a list.
  declineing_issues -- The number of issues in the index that declined since the last day, as a list.
  unchanged_issues -- The number of issues in the index that stayed put since the last day, as a list.
  new_highs -- The number of new highs of each day, over some interval (often 52 weeks)
  new_lows -- The number of new lows of each day, over the same interval
  """
  n = len(advancing_issues)
  result = [0.0] * n
  for i in range(0, n):
    result[i] = (new_highs[i] - new_lows[i]) * 1.0 / (advancing_issues[i] + declining_issues[i] + unchanged_issues[i])
  return result

def capm(investment, market, risk_free_return=0):
  """Computes historical CAPM paramaters, using log returns, of the investment over the market.
  
  investment -- The daily prices of the investment under analysis.
  market -- The daily prices of the market investment.
  risk_free_return -- The risk-free return over the period of consideration, given as a fraction.
  
  Returns (alpha, beta, r), where r is the r-value.""" 
  alr = log(1.0 + risk_free_return)
  investment_returns = [log(1.0 * b / a) - alr for (a,b) in zip(investment[0:-1], investment[1:])]
  market_returns = [log(1.0 * b / a) - alr for (a,b) in zip(market[0:-1], market[1:])]
  x = linregress(market_returns, investment_returns)
  beta = x[0]
  alpha = x[1]
  r = x[2]
  return (alpha, beta, r)
  
  