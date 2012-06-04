"""This file contains the test_end_of_day of the DJ Scrooge backtesting API.
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
from proboscis.asserts import assert_equal
from datetime import date
from djscrooge.backtest import Split

class TestEndOfDay(object):
  """Tests an arbitrary EndOfDay sublclass."""
  def __init__(self, end_of_day_subclass):
    self.__eod_class = end_of_day_subclass
  
  @test
  def test_prices(self):
    """Test the retrieved prices."""
    eod = self.__eod_class('GE', date(2012, 4, 27), date(2012, 5, 1))
    assert_equal(eod.open_prices, [1969, 1968, 1958])
    assert_equal(eod.high_prices, [1987, 1972, 1995])
    assert_equal(eod.low_prices, [1960, 1944, 1946])
    assert_equal(eod.close_prices, [1978, 1958, 1980])
    
  @test
  def test_dividends(self):
    """Test the retrieved dividends."""
    eod = self.__eod_class('GE', date(2012, 2, 22), date(2012, 2, 24))
    assert_equal(eod.close_prices, [1939, 1931, 1924])
    assert_equal(eod.dividends, [None, 17, None]) 

  @test
  def test_splits(self):
    """Test the retrieved splits."""
    eod = self.__eod_class('GE', date(2000, 5, 5), date(2000, 5, 9))
    assert_equal(eod.close_prices, [15800, 5244, 5213])
    assert_equal(eod.splits, [None, Split(3,1), None]) 
    
  @test
  def test_dates(self):
    """Test that dates are in the correct order."""
    eod = self.__eod_class('GE', date(2012, 5, 7), date(2012, 5, 9))
    assert_equal(eod.dates, [date(2012, 5, 7), date(2012, 5, 8), date(2012, 5, 9)])
    
  @test
  def test_number_of_splits(self):
    """Test the correct number of splits are downloaded."""
    eod = self.__eod_class('GE', date(1900, 1, 1), date(2012, 5, 12))
    assert_equal(len([x for x in eod.splits if x is not None]), 3)
    assert_equal(eod.splits[eod.get_index_from_date(date(2000, 5, 8))], Split(3,1))
  
