"""This module contains the base classes of the DJ Scrooge backtesting API.
Copyright (C) 2012  James Adam Cataldo

    This file is part of DJ Scrooge.

    DJ Scrooge is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with DJ Scrooge.  If not, see <http://www.gnu.org/licenses/>.
    
    Module constants:
    
    SYMBOL_FOR_ALL_DATES -- The stock symbol used to retrieve all possible
                            simulation dates
"""
from djscrooge.data_types import OrderedSet, iterator_to_list, index_of_sorted_list
import math    
from djscrooge.config import Config
from collections import namedtuple
  
class OpenPosition(object):
  """A class representing previously purchased shares.
  
  This class is used to represent a stock which has been purchased, with
  some shares still not sold.
  
  Available properties/attributes:

  symbol -- The ticker symbol of the purchased shares.
  purchase_date -- The datetime.date object representing the date the shares were purchased.
  cost_basis -- The cost basis, in cents, of the position.
  remaining_shares -- The shares still owned from this purchase.
  
  Note that
  """
  
  def __init__(self, symbol, purchase_date, cost_basis, remaining_shares):
    """Constructs a OpenPosition object.
    
    symbol -- The ticker symbol of the purchased shares.
    purchase_date -- The datetime.date object representing the date the shares were purchased.
    cost_basis -- The cost basis, in cents, of the position.
    remaining_shares -- The shares still owned from this purchase.
    """
    self.symbol = symbol
    self.purchase_date = purchase_date
    self.cost_basis = cost_basis
    self.remaining_shares = remaining_shares

class Portfolio(object):
  """A class representing a portfolio of cash and open positions.
  
  Available attributes/properties:
  cash -- The current cash, in cents, of the portfolio. This number will be an integer.
  symbols -- The ticker symbols of all shares owned.  
  """
  
  def __init__(self, cash):
    """Construct a portfolio with the specified amount of cash"""
    self.cash = cash
    self.symbols = set([])
    self.__positions = {}
    
  def add_position(self, open_position):
    """Adds the given OpenPosition object to the set of open positions in this Portfolio
    
    When calling this method, don't forget to decrement the cash used for the purchase.
    """
    symbol = open_position.symbol
    if not symbol in self.symbols:
      self.symbols.add(symbol)
      self.__positions[symbol] = OrderedSet()
    self.__positions[symbol].append(open_position)
    
  def get_positions(self, symbol):
    """Gets the open positions for the given symbol.
    
    The returned object is a list of OpenPosition objects. Do not modify this list directly. 
    Instead call add_position or remove_position. The returned object is not the same as
    the internally stored values. This is done for efficiency reasons. You can modify 
    elements of the list, however, to update the cost basis or remaining shares of the 
    underlying OpenPosition.
    """
    return iterator_to_list(self.__positions[symbol])
  
  def remove_position(self, open_position):
    """Remove the given OpenPostion object from this portfolio.
    
    When calling this method, don't forget to increment the cash gained in the sale.
    """
    positions = self.__positions[open_position.symbol]
    positions.remove(open_position)
    if len(positions) == 0:
      del self.__positions[open_position.symbol]
      self.symbols.remove(open_position.symbol)
  
class Split(object):
  """A class representing stock splits.
  
  Available properties/attributes:
  
  numerator -- The numerator of the split.
  denominator -- The denominator of the split.    
  """
  
  def __init__(self, numerator, denominator):
    """Create a new Split object.
    
    numerator -- The numerator of the split.
    denominator -- The denominator of the split.
    
    For a 2-1 split, the corresponding object would be created with Split(2,1).
    For a 1-10 reverse split, the object would be Split(1,10).
    """
    self.numerator = numerator
    self.denominator = denominator
    
  def __eq__(self, other):
    """Returns True if this equals the other object."""
    if type(other) == Split:
      return self.numerator == other.numerator and self.denominator == other.denominator
    return False
  
  def _ne__(self, other):
    """Returns False if this equals the other object."""
    return not self.__eq__(other)
  
  def __hash__(self):
    """Returns a hash code for this object."""
    return hash(self.numerator) ^ hash(self.denominator)
  
  def __str__(self):
    """Returns a string representation of this object."""
    return str(self.numerator) + ':' + str(self.denominator)
  
  def __repr__(self):
    """Returns the official representation of this object."""
    return 'Split(' + str(self.numerator) + ',' + str(self.denominator) + ')'

class EndOfDay(object):
  """The base class for data sources providing end-of-day data for stocks
  
  Subclasses of this should override the constructor, setting the following attributes:
    self.dates -- An ordered list of datatime.date objects reprenting the days for 
                  which stock data is available.
    self.open_prices -- The ordered list of opening prices for each day.
    self.high_prices -- The ordered list of daily-high prices.
    self.low_prices -- The ordered list of daily-low prices.
    self.close_prices -- The ordered list of closing prices for each day.
    self.adj_close_prices -- The ordered list of closing prices for each day, adjusted for dividends & splits.
    self.dividends -- The ordered list of dividends for each day, if any.
    self.splits -- The ordered list of Split objects representing each day's split,
                  if any.
    self.volumes -- The ordered list of trading volumes for each day.
                  
    All of these lists should be the same size. On most days, there is no dividend
    and no split. For such days, the corresponding entry in the self.dividends and
    self.splits objects should be None. All prices should be in cents. Only
    dividends and adjusted close prices can be in fractions of a cent.
  """
  
  def __init__(self, symbol, start_date, end_date):
    """Construct the EndOfDay object for the given symbol.
    
    symbol--The ticker symbol.
    start_date -- The datatime.date object corresponding to the first date to observe.
    end_date -- The datetime.date object corresponding to the last date to observe.
    
    Note that it's possible for no data to be available on the gievn start_date, say
    for a new company. Similarly, it's possible for no data to be available on the
    given end_date, say for a defunct company. The self.dates object should record the
    actual dates the stock data is available.
    """
    self.dates = []
    self.open_prices = []
    self.high_prices = []
    self.low_prices = []
    self.close_prices = []
    self.adj_close_prices = []
    self.dividends = []
    self.splits = []
    self.volumes = []
    
  def get_index_from_date(self, dateobj):
    """Gets the index into the dates array for the given date Object.
    
    This has O(1) amortized cost, assuming this is called once for
    each date during a simulation.
    """
    if not hasattr(self, '_EndOfDay__date_index'):
      self.__date_index = {}
      for i in range(0, len(self.dates)):
        self.__date_index[self.dates[i]] = i
    if self.__date_index.has_key(dateobj):
      return self.__date_index[dateobj]
    return None

class BacktestComponent(object):
  """A class used in a backtest.
      
  Availble properties/attributes:
  
  backtest -- The Backtest object using this instance (which may be none).
  """
  
  def __init__(self, backtest):
    """Construct a backtest component with the given Backtest object."""
    self.backtest = backtest
    
  def after_initialization(self):
    """Subclasses can override this to perform initialization."""
    pass

class Strategy(BacktestComponent):
  """The base class for objects making investment decisions.
  
  Subclasses should override the execute method, which makes all purchases.
  They can use the get_backtest method, which will return the Backtest object
  executing a test using the Taxes. This is useful for getting data 
  about the simulation, such as the current simulation date and information
  about the current portfolio. It is also used for the execute to make buy
  and sell decisions.
  
  Subclasses should have a one-argument constructor, if any. This argument is the 
  backtest.
  """
  
  def execute(self):
    """Execute a single day of the strategy."""
    pass
        
class Commissions(BacktestComponent):
  """The base class for objects computing the commissions of transactions.
  
  Subclasses should override the buy_commissions and sell_commisions methods.
  They can use the get_backtest method, which will return the Backtest object
  executing a test using the CommissionsCompiler. This is usesful for getting
  data about the simulation, such as the current simulation date.
  
  Subclasses should have a one-argument constructor, if any. This argument is the 
  backtest.
  """
  
  def buy_commissions(self, symbol, shares, price_per_share):
    """Returns the commisions for buying the specified number of shares.
    
    symbol -- The ticker symbol for the stock to be bought.
    shares -- The number of shares to be bought.
    price_per_share -- The pricer per share, in cents.
    
    returns -- The price, in cents, of the commissions.
    
    When overriding this in a subclass, return the amount 
    """
    return 0
  
  def sell_commissions(self, symbol, shares, price_per_share):
    """Returns the commisions for selling the specified number of shares.
    
    symbol -- The ticker symbol for the stock to be sold.
    shares -- The number of shares to be sold.
    price_per_share -- The pricer per share, in cents.
    
    returns -- The price, in cents, of the commissions.
    """
    return 0
  
  def fees(self):
    """Returns any fee on the account for the simulation day this method gets called.
    
    returns -- The price, in cents, of the fees.
    """
    return 0
  
class Taxes(BacktestComponent):
  """The base class for objects computing the taxes of transactions.
  
  Subclasses should override the buy_tax, sell_tax, and dividend_tax methods.
  They can use the get_backtest method, which will return the Backtest object
  executing a test using the Taxes. This is usesful for getting data 
  about the simulation, such as the current simulation date. It may also be 
  used to get the underlying Commissions object, in case commissions affect 
  taxes.
  
  Subclasses should have a one-argument constructor, if any. This argument is the 
  backtest.
  """
  
  def buy_tax(self, symbol, shares, price_per_share):
    """Returns the commisions for buying the specified number of shares.
    
    symbol -- The ticker symbol for the stock to be bought.
    shares -- The number of shares to be bought.
    price_per_share -- The pricer per share, in cents.
    
    returns -- The price, in cents, of the taxes.
    
    While there are typically no taxes on buy shares, this method can be
    useful for bookeeping. 
    """
    return 0
  
  def sell_tax(self, symbol, shares, gain_per_share, purchase_date):
    """Returns the taxes for selling the specified number of shares.
    
    symbol -- The ticker symbol for the stock to be sold.
    shares -- The number of shares to be sold.
    gain_per_share -- The gain (loss) per share, in cents.
    purchase_date -- The purchase date of the stock being sold.
    
    returns -- The price, in cents, of the taxes.
    """
    return 0
  
  def dividend_tax(self, symbol, amount, purchase_date):
    """Returns the taxes for receivng dividends on the specified shares.
    
    symbol -- The ticker symbol for the stock paying out dividends.
    amount -- The payout of the dividend, in cents.
    purchase_date -- The purchase date of the stock paying a dividend.
    
    returns -- The price, in cents, of the taxes.
    """
    return 0
  
class Backtest(object):
  """The controller of a Backtest.
  
  To run a backtest, create subclasses of Commissions, Taxes,
  and Strategy. Pass these classes to the constructor of this
  class, and run the simulate method.
  
  Available properties/attributes:
  
  simulation_date -- The simulation date, as a datetime.date object.
  portfolio -- The Portfolio object representing the current holdings during the simulation.
  commissions -- The Commissions object used to compute commissions for the simulation.
  taxes -- The Taxes object used to compute taxes for the simulation.
  strategy -- The Strategy object being tested.
  dates -- The dates tested
  values -- The daily closing values of the portfolio.
  open_values -- The daily opening values of the portfolio. This is useful for statistical signifigance tests.
  start_date -- The start date of the simulation.
  end_date -- The end date of the simulation.
  end_of_day_class -- The class used to generate EndOfDay data.
  """
    
  def __init__(self, start_date, end_date, 
               commissions_class=Commissions, 
               taxes_class=Taxes, 
               strategy_class=Strategy, 
               end_of_day_class=EndOfDay,
               portfolio=None,
               cache=True):
    """Construct a Backtest object and run the simulation.
    
    commissions_class -- The class of the Commissions class.
    tax_class -- The class of the Taxes class.
    strategy_class -- The class of the Stragey class.
    end_of_day_class -- The EndOfDay class.
    start_date -- The datetime.date object representing the first date to simulate.
    end_date -- The datetime.date object representing the last date to simulate.
    portfolio -- The Portfolio object representing the current holdings during the simulation.
    cache -- True if EndOfDay ojbects should be cached.
    
    Note that if the portfolio is unspecified, it will be defaulted to a portfolio with
    $100,000 in cash.
    """
    self.start_date = start_date
    self.end_date = end_date
    self.commissions = commissions_class(self)
    self.taxes = taxes_class(self)
    self.strategy = strategy_class(self)
    self.end_of_day_class = end_of_day_class
    self.portfolio = portfolio
    if portfolio is None:
      self.portfolio = Portfolio(int(1e7))
    self.__end_of_day_items = {}
    symbol_for_all_dates = Config().BACKTEST_SYMBOL_FOR_ALL_DATES
    self.__date_offsets = { symbol_for_all_dates : 0 }
    ge = self.get_end_of_day(symbol_for_all_dates)
    self.dates = ge.dates 
    self.values = []
    self.open_values = []
    self.cache = cache
    self.commissions.after_initialization()
    self.taxes.after_initialization()
    self.strategy.after_initialization()
    for i in range(0,len(self.dates)):
      self.simulation_date = self.dates[i]
      total_stock_value = 0
      total_stock_open_value = 0
      symbols = self.portfolio.symbols
      for symbol in symbols:
        positions = self.portfolio.get_positions(symbol)
        symbol_data = self.get_close_data(symbol, self.dates[i])
        if symbol_data is None:
          continue
        for position in positions:
          total_stock_open_value += symbol_data.open_price * position.remaining_shares
      self.open_values.append(total_stock_open_value + self.portfolio.cash)
      for symbol in symbols:
        positions = self.portfolio.get_positions(symbol)
        symbol_data = self.get_close_data(symbol, self.dates[i])
        if symbol_data is None:
          continue
        dividend = symbol_data.dividend
        split = symbol_data.split
        if dividend is not None:
          for position in positions:
            amount = int(dividend * position.remaining_shares)
            tax = self.taxes.dividend_tax(symbol, amount, position.purchase_date)
            self.portfolio.cash += (amount - tax)
        if split is not None:
          multiplier = (1.0 * split.numerator) / split.denominator
          for position in positions:
            old_shares = position.remaining_shares
            position.remaining_shares = int(math.ceil(multiplier * old_shares))
            if position.remaining_shares == 0:
              continue
            else:
              position.cost_basis = int(round((1.0 * old_shares) * position.cost_basis / position.remaining_shares))
      self.strategy.execute()
      for symbol in symbols:
        positions = self.portfolio.get_positions(symbol)
        symbol_data = self.get_close_data(symbol, self.dates[i])
        if symbol_data is None:
          continue
        for position in positions:
          total_stock_value += symbol_data.close_price * position.remaining_shares
      self.portfolio.cash -= self.commissions.fees()
      self.values.append(total_stock_value + self.portfolio.cash)
            
  def buy_shares(self, symbol, shares, price_per_share):
    """Buy the specified number of shares of the given stock.
    
    symbol -- The ticker symbol.
    shares -- The number of shares.
    price_per_share -- The number of shares, in cents.
    """
    commissions = self.commissions.buy_commissions(symbol, shares, price_per_share)
    taxes = self.taxes.buy_tax(symbol, shares, price_per_share)
    cost = shares * price_per_share
    position = OpenPosition(symbol, self.simulation_date, price_per_share, shares)
    self.portfolio.add_position(position)
    self.portfolio.cash -= (commissions + taxes + cost)
  
  def sell_shares(self, symbol, shares, price_per_share, open_position=None):
    """Sell the specified number of shares of the given stock.

    symbol -- The ticker symbol.
    shares -- The number of shares.
    price_per_share -- The number of shares, in cents.
    open_position -- The OpenPosition object to sell teh shares from.
    
    If open_position is not specified, the oldest shares for a symbol will be sold first.
    """
    def sell_helper(symbol, shares, price_per_share, open_position):
      if open_position.remaining_shares  < shares:
        shares = open_position.remaining_shares
      if open_position.remaining_shares == shares:
        self.portfolio.remove_position(open_position)
      gain_per_share = price_per_share - open_position.cost_basis
      commissions = self.commissions.sell_commissions(symbol, shares, price_per_share)
      taxes = self.taxes.sell_tax(symbol, shares, gain_per_share, open_position.purchase_date)
      revenue = price_per_share * shares
      open_position.remaining_shares -= shares
      self.portfolio.cash += (revenue - commissions - taxes)
    if open_position is None:
      positions = self.portfolio.get_positions(symbol)
      for position in positions:
        if shares <= 0:
          return
        position_shares = min(position.remaining_shares, shares)
        shares = shares - position_shares
        sell_helper(symbol, position_shares, price_per_share, position)
    else:
      sell_helper(symbol, shares, price_per_share, open_position)
      
  def get_close_data(self, symbol, date):
    """Returns a named tuple with close_price, dividend, split, and open_price data."""
    CloseData = namedtuple('CloseData', ['close_price', 'dividend', 'split', 'open_price'])
    if self.cache:
      symbol_data = self.get_end_of_day(symbol)
      i = self.__end_of_day_items[Config().BACKTEST_SYMBOL_FOR_ALL_DATES].get_index_from_date(date)
      if i == None:
        return None
      k = i - self.__date_offsets[symbol]
      dividend = symbol_data.dividends[k]
      split = symbol_data.splits[k]
      close_price = symbol_data.close_prices[k]
      open_price = symbol_data.open_prices[k]
      return CloseData(close_price, dividend, split, open_price)
    else:
      eod = self.end_of_day_class(symbol, date, date)
      if len(eod.close_prices) == 0:
        return None
      return CloseData(eod.close_prices[0], eod.dividends[0], eod.splits[0], eod.open_prices[0])

    
  def get_end_of_day(self, symbol):
    """Gets the EndOfDay object associated with the given stock.
    
    symbol -- The ticker symbol of the stock to get.
    
    The start_date and end_date of the returned object will match the start_date and
    end_date of the simulation.
    """
    if not self.__end_of_day_items.has_key(symbol):
      self.__end_of_day_items[symbol] = self.end_of_day_class(symbol, self.start_date, self.end_date)
    if not self.__date_offsets.has_key(symbol):
      dates = self.__end_of_day_items[Config().BACKTEST_SYMBOL_FOR_ALL_DATES].dates
      self.__date_offsets[symbol] = index_of_sorted_list(self.__end_of_day_items[symbol].dates[0], dates)
    return self.__end_of_day_items[symbol]
