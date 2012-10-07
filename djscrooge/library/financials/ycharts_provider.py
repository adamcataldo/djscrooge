"""This file contains the ycharts_provider module of the Pengoe Backtesting API.
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
from djscrooge.library.financials.financial_provider import FinancialProvider
from djscrooge.library.financials.edgar import Edgar
from datetime import datetime, date, timedelta
from djscrooge.util.data_types import glb_index_in_sorted_list

class YchartsProvider(FinancialProvider):
  """Implements a FinancialProvider using CSV data downloaded from ycharts.com."""
  
  def __init__(self, symbol, file_like_object, types):
    """Constructs a YchartsProvider for the given symbol and file_like_object with
    downloaded CSV data. It is assumed the CSV data does not contain price data,
    just quarterly financial data.
    
    The types are a list of names for the columns in the CSV after the period column. 
    """
    FinancialProvider.__init__(self, symbol)
    self.types = types
    edgar = Edgar(symbol)
    rows = file_like_object.read().strip().split("\n")[1:]
    data = []
    for row in rows:
      fields = [x.strip() for x in row.strip().split(",")]      
      data.append(fields)
      for field in fields:
        if field == "":
          data = []
          break
    self.storage = {}
    self.storage['__period_end_date'] = []
    self.storage['__filing_date'] = []
    for type in types:
      self.storage[type] = []
    for row in data:
      self.storage['__period_end_date'].append(datetime.strptime(row[0], '%Y-%m-%d').date())
      for i in range(0,len(types)):
        self.storage[types[i]].append(float(row[i + 1]) * 1e6)
    for row in data:
      period_end_date = datetime.strptime(row[0], '%Y-%m-%d').date()
      try:
        self.storage['__filing_date'].append(edgar.get_filing_date(period_end_date))
      except ValueError:
        if period_end_date < edgar.period_end_dates[0]:
          self.storage['__filing_date'].append(edgar.filing_dates[0])
        else:
          raise
    
  def get_all_before(self, type, simulation_date):
    """Get all data of the given type filed before the simulation_date.
    """
    v = []
    i = 0
    while self.storage['__filing_date'][i] < simulation_date:
      v.append(self.storage[type][i])
      i += 1
    return v    
  
  def get_most_recent(self, type, simulation_date):
    """Get he most recent data of the given type filed before the simulation_date.
    
    Here type is a string used to identify which type of financial data
    to fetch, like 'cash flow'. Subclasses should implement this method
    with whatever financial data is relevant. For types not recognized,
    this method should return a ValueError.
    
    The simulation_date is a datetime.date object. The return value 
    should be (value, next_available_data). The value is the last known
    value the morning of the simulation date. The next_available_data 
    is the next possbile simulation_date for which new data will be 
    available. This will be None if there is no such sdate.
    """
    i = glb_index_in_sorted_list(simulation_date + timedelta(1), self.storage['__filing_date'])
    if i == -1:
      raise ValueError('No data available for type "%s".' % str(type))
    return self.storage[type][i]
  
  def get_next_date(self, simulation_date):
    """Get the next date after the simulation for which new data is available.
    
    This will be None if there is no such future date.
    """
    i = glb_index_in_sorted_list(simulation_date + timedelta(1), self.storage['__filing_date']) + 1
    if i == len(self.storage['__filing_date']):
      return None
    return self.storage['__filing_date'][i] + timedelta(1)
  
  def get_first_date(self):
    """Returns the first date data is available for the given symbol, 
    or None if there is no available data."""
    return self.storage['__filing_date'][0] + timedelta(1)  
  
if __name__ == "__main__":
  with open('/Users/adam/Downloads/goog_data.csv', 'r') as f:
    x = YchartsProvider('GOOG', f, ['free_cash_flow'])
    v1 = x.get_all_before('free_cash_flow', date(2010, 1, 1))
    print '====Before 1-1-2010'
    for v in v1:
      print v