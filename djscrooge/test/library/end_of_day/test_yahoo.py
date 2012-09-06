"""This file contains the test_yahoo module of the DJ Scrooge backtesting API.
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
from djscrooge.test.library.end_of_day.test_end_of_day import TestEndOfDay
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
class TestYahoo(TestEndOfDay):
  """Tests the Yahoo EndOfDay class."""
  
  def __init__(self):
    super(TestYahoo, self).__init__(Yahoo)  
    
  @test
  def test_split_only_days(self):
    """Test days with a split and no stock price data."""
    eod = Yahoo('WAT', date(2000, 8, 25), date(2000, 8, 30))
    assert_equal(eod.open_prices, [15050, 15688 / 2, 7900])
    assert_equal(eod.high_prices, [15844, 15688 / 2, 7962])
    assert_equal(eod.low_prices, [15025, 15688 / 2, 7712])
    assert_equal(eod.close_prices, [15688, 15688 / 2, 7762])
    assert_equal(eod.volumes, [450800, 0, 491200])
    assert_equal(eod.dividends, [None, None, None]) 
    assert_equal(eod.splits, [None, Split(2,1), None])
    
if __name__ == "__main__":
  from proboscis import TestProgram
  TestProgram().run_and_exit()