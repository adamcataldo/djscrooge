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

def simple_moving_average(end_of_day, window):
  """Calculates a simple moving average of the adjusted close prices.
  
  end_of_day -- The end_of_day object to calculate the average on.
  window -- The window length of the moving average.
  """
  moving_average = []
  for i in range(0, len(end_of_day.dates)):
    if i < window:
      moving_average.append(sum(end_of_day.adj_close_prices[0:(i+1)]) * 1.0 / (i + 1))
    else:
      moving_average.append(sum(end_of_day.adj_close_prices[(i+1-window):(i+1)]) * 1.0 / window)
  return moving_average
