"""This file contains the chartin module of the DJ Scrooge backtesting API.
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
    
Dependencies: 
    matplotlib: <http://matplotlib.sourceforge.net/>
"""

import matplotlib.pyplot as plt

def chart_backtest(*backtests, **keywords):
  """Given a list of Backtest objects, this creates a value chart.
  
  *backtests -- The list of Backtest objects
  **keywords -- A dictionary of charting keywords, all of which are optional.
  
  Allowed keywords:
    colors -- A list of color formats for the Backtest objects provided.
              See http://matplotlib.sourceforge.net/api/colors_api.html for
              the allowed formats.
    file_name -- Save the chart to the given file name, instead of plotting to screen.
                 The file extension should be one of png, pdf, ps, eps, or svg.
    labels -- A list of labels for the Backtest objects provided.
              When this keyword is provided, a legend will be drawn on the upper left
              corner of the plot.
    title -- The title of the chart.
  """
  plot_list = []
  i = 0
  for backtest in backtests:
    plot_list.append(backtest.dates)
    plot_list.append(map(lambda x: x / 100.0, backtest.values))
    if keywords.has_key('colors'):
      plot_list.append(keywords['colors'][i])
    i += 1
  apply(plt.plot, plot_list)
  plt.xlabel('Date')
  plt.ylabel('Value ($)')
  if keywords.has_key('title'):
    plt.title(keywords['title'])
  if keywords.has_key('labels'):
    legend_list = [tuple(keywords['labels'])]
    legend_dict = {'loc' : 2 }
    apply(plt.legend, legend_list, legend_dict)
  if keywords.has_key('file_name'):
    plt.savefig(keywords['file_name'])
  else:
    plt.show()
  plt.close()