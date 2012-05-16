"""This file contains the XXX of the DJ Scrooge backtesting API.
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
    proboscis: <https://github.com/rackspace/python-proboscis>
"""
from proboscis import test
from proboscis.asserts import assert_equal
from proboscis.asserts import assert_true
from StringIO import StringIO
from djscrooge.library.end_of_day.yahoo import HeadingCsv, Yahoo
from datetime import date
from djscrooge.backtest import Split

@test(groups=['csv'])
class TestHeadingCsv(object):
  """Tests for the HeadingCsv class."""
  
  @test
  def testBasic(self):
    """Test that a simple CSV file object is correctly parsed."""
    f = StringIO("Foo,Bar,Baz\n1,2,3\n4,5,6")
    csv = HeadingCsv(f)
    row = 0
    for line in csv:
      assert_equal(len(line), 3)
      assert_true(line.has_key('Foo'))
      assert_true(line.has_key('Bar'))
      assert_true(line.has_key('Baz'))
      if row == 0:
        assert_equal(line['Foo'], '1')
        assert_equal(line['Bar'], '2')
        assert_equal(line['Baz'], '3')
      elif row == 1:
        assert_equal(line['Foo'], '4')
        assert_equal(line['Bar'], '5')
        assert_equal(line['Baz'], '6')
      row += 1
    assert_equal(row, 2)

@test(depends_on_groups=['csv'])
class TestYahoo:
  """Tests the Yahoo EndOfDay class."""
  
  @test
  def test_prices(self):
    """Test the prices retrieved from Yahoo."""
    yahoo = Yahoo('GE', date(2012, 4, 27), date(2012, 5, 1))
    assert_equal(yahoo.open_prices, [1969, 1968, 1958])
    assert_equal(yahoo.high_prices, [1987, 1972, 1995])
    assert_equal(yahoo.low_prices, [1960, 1944, 1946])
    assert_equal(yahoo.close_prices, [1978, 1958, 1980])
    
  @test
  def test_dividends(self):
    """Test the dividends retrieved from Yahoo."""
    yahoo = Yahoo('GE', date(2012, 2, 22), date(2012, 2, 24))
    assert_equal(yahoo.close_prices, [1939, 1931, 1924])
    assert_equal(yahoo.dividends, [None, 17, None]) 

  @test
  def test_splits(self):
    """Test the splits retrieved from Yahoo."""
    yahoo = Yahoo('GE', date(2000, 5, 5), date(2000, 5, 9))
    assert_equal(yahoo.close_prices, [15800, 5244, 5213])
    assert_equal(yahoo.splits, [None, Split(3,1), None]) 
    
  @test
  def test_dates(self):
    """Test that dates are in the correct order."""
    yahoo = Yahoo('GE', date(2012, 5, 7), date(2012, 5, 9))
    assert_equal(yahoo.dates, [date(2012, 5, 7), date(2012, 5, 8), date(2012, 5, 9)])
    

if __name__ == "__main__":
  from proboscis import TestProgram
  TestProgram().run_and_exit()