"""This module contains tests for DJ Scrooge.backtest
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
    
Dependencies: 
    proboscis: <https://github.com/rackspace/python-proboscis>
"""
from proboscis import test
from proboscis.asserts import assert_equal
from proboscis.asserts import assert_not_equal
from proboscis.asserts import assert_true
from proboscis.asserts import assert_false
from proboscis.asserts import assert_raises
from backtest import *
from datetime import date
from datetime import timedelta
from proboscis.decorators import before_class

@test(groups=['portfolio'])
class TestPortfolio(object):
  """Tests the Portfolio class."""
  
  @test(groups=['initializers'])
  def test_modify_item(self):
    """Test modifying an OpenPosition within a Portfolio."""
    self.portfolio = Portfolio(100)
    self.start_date = date(2000,1,1)
    self.p1 = OpenPosition('FOO', self.start_date, 100, 100)
    self.p2 = OpenPosition('FOO', self.start_date + timedelta(1), 200, 150)
    self.p3 = OpenPosition('FOO', self.start_date + timedelta(2), 300, 200)
    self.portfolio.add_position(self.p1)
    self.portfolio.add_position(self.p2)
    self.portfolio.add_position(self.p3)
    positions = self.portfolio.get_positions('FOO')
    assert_equal(positions, [self.p1, self.p2, self.p3])
    positions[0].cost_basis = 50
    positions[0].remaining_shares = 200
    assert_equal(self.p1, positions[0])
    positions = self.portfolio.get_positions('FOO')
    assert_equal(positions, [self.p1, self.p2, self.p3])
    self.portfolio.add_position(OpenPosition('BAR', self.start_date, 100, 100))
    positions = self.portfolio.get_positions('FOO')
    assert_equal(positions, [self.p1, self.p2, self.p3])
    
  @test(depends_on_groups=['initializers'])
  def test_remove_item(self):
    """Test the remove_item method of Portfolio."""
    self.portfolio.remove_position(self.p2)
    assert_equal(self.portfolio.get_positions('FOO'), [self.p1, self.p3])
    p4 = OpenPosition('FOO', self.start_date + timedelta(2), 300, 200)
    self.portfolio.add_position(p4)
    self.portfolio.remove_position(self.p3)
    assert_equal(self.portfolio.get_positions('FOO'), [self.p1, p4])
    assert_not_equal(self.portfolio.get_positions('FOO'), [self.p1, self.p3])

  @test
  def test_symbol_deleted_when_last_position_removed(self):
    """Test that the remove_item method of Portfolio removes unused sybmols."""
    portfolio = Portfolio(100)
    start_date = date(2000,1,1)
    p1 = OpenPosition('FOO', start_date, 100, 100)
    portfolio.add_position(p1)
    portfolio.remove_position(p1)
    assert_false(p1.symbol in portfolio.symbols)

def get_mock_end_of_day_class(open_prices, high_prices=None, low_prices=None, close_prices=None,
                              dividends=None, splits=None, volumes=None):
  """Create an EndOfDay subclass from the given data.
  
  If any defaults are not given "smart" values will be used. This means high_prices, low_prices,
  and close_prices will equal open_prices. Also, dividends and splits will be a list of None.
  
  When the number of days given to the EndOfDay constructor is different than the data size given,
  the data will be either truncated or repeated to fill in the corresponding data in the EndOfDay
  class. All non-None values should be lists of the same length.
  """
  if high_prices is None:
    high_prices = open_prices
  if low_prices is None:
    low_prices = open_prices
  if close_prices is None:
    close_prices = open_prices
  if dividends is None:
    dividends = [None] * len(open_prices)
  if splits is None:
    splits = [None] * len(open_prices)
  if volumes is None:
    volumes = [1] * len(open_prices)    
  class MockEndOfDay(EndOfDay):
        
    def __init__(self, symbol, start_date, end_date):
      super(MockEndOfDay, self).__init__(symbol, start_date, end_date)
      x = start_date
      i = 0
      n = len(open_prices)
      while x <= end_date:
        self.dates.append(x)
        self.open_prices.append(open_prices[i % n])
        self.high_prices.append(high_prices[i % n])
        self.low_prices.append(low_prices[i % n])
        self.close_prices.append(close_prices[i % n])
        self.dividends.append(dividends[i % n])
        self.splits.append(splits[i % n])
        self.volumes.append(volumes[i % n])
        x += timedelta(1)
        i += 1 
        
  return MockEndOfDay

@test(groups=['end_of_day'], depends_on_groups=['portfolio'])
class TestEndOfDay(object):
  """Tests the EndOfDay class"""
  
  @test
  def basic_test(self):
    """Test the Backtest class against a single EndOfDay object, with no dividends or splits."""
    end_of_day_class = get_mock_end_of_day_class([1, 2, 3, 4])
    start = date(2000,1,1)
    portfolio = Portfolio(0)
    portfolio.add_position(OpenPosition('FOO', start - timedelta(1), 1, 1))
    backtest = Backtest(start, start + timedelta(3), end_of_day_class=end_of_day_class, portfolio=portfolio)
    expected_dates = [start, start + timedelta(1), start + timedelta(2), start + timedelta(3)]
    expected_values = [1, 2, 3, 4]
    assert_equal(backtest.dates, expected_dates)
    assert_equal(backtest.values, expected_values)
    
  @test
  def test_dividends(self):
    """Test the Backtest class's dividend handling."""
    end_of_day_class = get_mock_end_of_day_class([1, 1, 1, 1], dividends=[None, 1, None, None])
    start = date(2000,1,1)
    portfolio = Portfolio(0)
    portfolio.add_position(OpenPosition('FOO', start - timedelta(1), 1, 1))
    backtest = Backtest(start, start + timedelta(3), end_of_day_class=end_of_day_class, portfolio=portfolio)
    expected_values = [1, 2, 2, 2]
    assert_equal(backtest.values, expected_values)
    
  @test
  def test_splits(self):
    """Test the Backtest class's split handling."""
    end_of_day_class = get_mock_end_of_day_class([1, 1, 1, 1], splits=[None, Split(2,1), None, None])
    start = date(2000,1,1)
    portfolio = Portfolio(0)
    portfolio.add_position(OpenPosition('FOO', start - timedelta(1), 1, 1))
    backtest = Backtest(start, start + timedelta(3), end_of_day_class=end_of_day_class, portfolio=portfolio)
    expected_values = [1, 2, 2, 2]
    assert_equal(backtest.values, expected_values)
    
@test(groups=['backtest'], depends_on_groups=['portfolio', 'end_of_day'])
class TestBacktest(object):
  """Tests the Backtest class."""
  
  @test
  def test_simulation_date(self):
    """Test that the simulation date proceeds correctly."""
    start = date(2000,1,1)
    end = start + timedelta(3)
    backtest = Backtest(start, end, end_of_day_class=get_mock_end_of_day_class([1,2,3,4]))
    assert_equal(backtest.simulation_date, end)
        
def get_mock_strategy_class(execute_method):
  """Returns a strategy subclass which tracks the current execution day in the variable day.
  
  execute_method -- The details of what to do when execute is called.
  
  Incrementing the day variable is handled automatically."""
  class MockStrategy(Strategy):
    def __init__(self, backtest):
      super(MockStrategy, self).__init__(backtest)
      self.day = 0
    
    def execute(self):
      execute_method(self)
      self.day += 1
  
  return MockStrategy

def get_simple_strategy_class():
  """Gets a Strategy class that buys 100 shares on day zero and sells them on day two."""
  def execute_method(self):
    eod = self.backtest.get_end_of_day('FOO')
    if self.day == 0:
      self.backtest.buy_shares('FOO', 100, eod.open_prices[self.day])
    elif self.day == 1:
      self.backtest.sell_shares('FOO', 100, eod.open_prices[self.day])
  return get_mock_strategy_class(execute_method)

@test(groups=['strategy'], depends_on_groups=['portfolio', 'end_of_day'])
class TestStrategy(object):
  """Tests for the Strategy subclasses against the Backest class."""
  
  @before_class
  def set_up(self):
    """Sets up an end_of_day_class for all Strategy tests."""
    self.end_of_day_class = get_mock_end_of_day_class([1, 2, 3, 4])
  
  @test
  def test_basic(self):
    """A simple test for the Backtest class."""
    start = date(2000,1,1)
    strategy = get_simple_strategy_class()
    portfolio = Portfolio(100)
    backtest = Backtest(start, start + timedelta(3), strategy_class=strategy, 
                        end_of_day_class=self.end_of_day_class, portfolio=portfolio)
    expected_values = [100, 200, 200, 200]
    assert_equal(backtest.values, expected_values)
    
  @test
  def test_sell_order(self):
    """Test that the Backtest class respects selling order correctly."""
    def execute(self):
      eod = self.backtest.get_end_of_day('FOO')
      if (self.day == 0):
        self.backtest.buy_shares('FOO', 1, eod.open_prices[self.day])
      elif (self.day == 1):
        self.backtest.buy_shares('FOO', 2, eod.open_prices[self.day])
      elif (self.day == 2):
        self.backtest.sell_shares('FOO', 1, eod.open_prices[self.day], 
                                  self.backtest.portfolio.get_positions('FOO')[1])
      elif (self.day == 3):
        self.backtest.sell_shares('FOO', 1, eod.open_prices[self.day])
    start = date(2000,1,1)
    portfolio = Portfolio(100)
    strategy = get_mock_strategy_class(execute)
    Backtest(start, start + timedelta(3), strategy_class=strategy, 
             end_of_day_class=self.end_of_day_class, portfolio=portfolio)
    positions = portfolio.get_positions('FOO')
    assert_equal(len(positions), 1)
    assert_equal(positions[0].purchase_date, start + timedelta(1))
    
@test(depends_on_groups=['portfolio', 'end_of_day', 'strategy'])
class TestCommissions(object):
  """Tests the Commissions class."""
  
  @test
  def test_commissions(self):
    """Test that Commissions are applied correctly."""
    end_of_day_class = get_mock_end_of_day_class([1, 2, 3, 4])
    strategy = get_simple_strategy_class()
    portfolio = Portfolio(105)
    class MockCommissions(Commissions):
      
      def buy_commissions(self, symbol, shares, price_per_share):
        return 1
      
      def sell_commissions(self, symbol, shares, price_per_share):
        return 1
      
      def fees(self):
        return 1
    start = date(2000,1,1)
    backtest = Backtest(start, start + timedelta(3), commissions_class=MockCommissions, 
                        strategy_class=strategy, end_of_day_class=end_of_day_class, 
                        portfolio=portfolio)
    expected = [103, 201, 200, 199]
    assert_equal(backtest.values, expected)

@test(depends_on_groups=['portfolio', 'end_of_day', 'strategy', 'backtest'])
class TestTaxes(object):
  """Tests the Taxes class."""
  
  @test
  def test_buy_sell(self):
    """Test that Taxes are applied correctly on buy/sell orders."""
    end_of_day_class = get_mock_end_of_day_class([1, 2, 3, 4])
    strategy = get_simple_strategy_class()
    portfolio = Portfolio(101)
    class MockTaxes(Taxes):
      
      def buy_tax(self, symbol, shares, price_per_share):
        return 1
      
      def sell_tax(self, symbol, shares, gain_per_share, purchase_date):
        return gain_per_share * shares / 2         
    start = date(2000,1,1)
    backtest = Backtest(start, start + timedelta(3), taxes_class=MockTaxes, 
                        strategy_class=strategy, end_of_day_class=end_of_day_class, 
                        portfolio=portfolio)
    expected = [100, 150, 150, 150]
    assert_equal(backtest.values, expected)
    
  @test
  def test_dividends(self):
    """Test that dividend taxes are handled correctly"""
    end_of_day_class = get_mock_end_of_day_class([1, 1, 1, 1], dividends=[None, 2, None, None])
    portfolio = Portfolio(0)
    start = date(2000,1,1)
    portfolio.add_position(OpenPosition('Foo', start - timedelta(1), 1, 1))
    class MockTaxes(Taxes):
      def dividend_tax(self, symbol, amount, purchase_date):
        return 1
    backtest = Backtest(start, start + timedelta(3), taxes_class=MockTaxes, 
                        end_of_day_class=end_of_day_class, portfolio=portfolio)
    expected = [1, 2, 2, 2]
    assert_equal(backtest.values, expected)
    
  @test
  def test_purchase_date(self):
    """Test that purchase dates are correctly handled with respect to Taxes."""
    end_of_day_class = get_mock_end_of_day_class([1, 3, 3, 3])
    def execute(self):
      if (self.day == 1):
        self.backtest.sell_shares('FOO', 2, 3)
    strategy = get_mock_strategy_class(execute)
    portfolio = Portfolio(0)
    start = date(2000,1,1)
    portfolio.add_position(OpenPosition('FOO', start - timedelta(2), 1, 1))
    portfolio.add_position(OpenPosition('FOO', start - timedelta(1), 1, 1))
    class MockTaxes(Taxes):
      def sell_tax(self, symbol, shares, gain_per_share, purchase_date):
        if self.backtest.simulation_date - purchase_date <= timedelta(2):
          return 1
        else:
          return 0         
    backtest = Backtest(start, start + timedelta(3), taxes_class=MockTaxes, 
                        strategy_class=strategy, end_of_day_class=end_of_day_class, 
                        portfolio=portfolio)
    expected = [2, 5, 5, 5]
    assert_equal(backtest.values, expected)
  
  @test
  def test_splits(self):
    """Test that the cost basis is correctly adjusted when stocks are split."""
    end_of_day_class = get_mock_end_of_day_class([2, 2, 2, 2], splits=[None, Split(2,1), None, None])
    portfolio = Portfolio(2)
    start = date(2000,1,1)
    def execute(self):
      if (self.day == 0):
        self.backtest.buy_shares('FOO', 1, 2)
      elif (self.day == 2):
        self.backtest.sell_shares('FOO', 2, 2)
    strategy = get_mock_strategy_class(execute)
    class MockTaxes(Taxes):
      def sell_tax(self, symbol, shares, gain_per_share, purchase_date):
        return gain_per_share * shares / 2
    backtest = Backtest(start, start + timedelta(3), taxes_class=MockTaxes, 
                        strategy_class=strategy, end_of_day_class=end_of_day_class, 
                        portfolio=portfolio)
    expected = [2, 4, 3, 3]
    assert_equal(backtest.values, expected)    
    
if __name__ == '__main__':
  from proboscis import TestProgram
  TestProgram().run_and_exit()
