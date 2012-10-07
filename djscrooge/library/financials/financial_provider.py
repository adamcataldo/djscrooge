"""This file contains the financial_provider module of the Pengoe Backtesting API.
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

class FinancialProvider(object):
  """This is the base class for objects providing financial data.
  
  Properties/attributes:
    - symbol: The symbol for the stock under analysis.
  
  """
  
  def __init__(self, symbol):
    """Initializes a FinancialProvider for the given stock."""
    self.symbol = symbol
  
  def get_all_before(self, type, simulation_date):
    """Get all data of the given type filed before the simulation_date.
    
    Here type is a string used to identify which type of financial data
    to fetch, like 'cash flow'. Subclasses should implement this method
    with whatever financial data is relevant. For types not recognized,
    this method should return a ValueError.
    
    The simulation_date is a datetime.date object. The return value 
    should be (data, next_available_data). The data is a list of values 
    for all the data known the morning of the simulation date. The 
    next_available_data is the next possbile simulation_date for which
    new data will be available. This will be None if there is no such
    date.
    """
    return None
  
  def get_next_date(self, simulation_date):
    """Get the next date after the simulation for which new data is available.
    
    This will be None if there is no such future date.
    """
    return None
  
  def get_most_recent(self, type, simulation_date):
    """Get the most recent data of the given type filed before the simulation_date.
    
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
    raise ValueError('No data available for type "%s".' % str(type))
  
  def get_first_date(self):
    """Returns the first date data is available for the given symbol, 
    or None if there is no available data."""
    return None
  
class FinancialProviderFactory(object):
  """A factory base class for generating FinancialProvider instances."""
  
  def get_financial_provider(self, symbol):
    """Returns a FinancialProvider for the given symbol.
    
    Subclasses should override this.
    """
    return FinancialProvider(symbol)