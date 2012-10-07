"""This file contains the test_ychart_provider module of the Pengoe Backtesting API.
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
from StringIO import StringIO
from djscrooge.library.financials.ycharts_provider import YchartsProvider

GOOG_DATA = """period,Google Free Cash Flow
2002-12-31,118.0700
2003-03-31,
2003-06-30,116.6210
2003-09-30,71.9710
2003-12-31,30.0480
2004-03-31,122.0080
2004-06-30,66.3130
2004-09-30,160.7110
2004-12-31,309.0170
2005-03-31,387.2310
2005-06-30,467.1560
2005-09-30,354.2150
2005-12-31,412.6030
2006-03-31,479.8660
2006-06-30,141.5860
2006-09-30,512.1020
2006-12-31,544.1560
2007-03-31,622.7000
2007-06-30,654.8280
2007-09-30,1080.0030
2007-12-31,1015.0390
2008-03-31,937.8490
2008-06-30,1068.6370
2008-09-30,1733.4550
2008-12-31,1754.0590
2009-03-31,1987.0000
2009-06-30,1470.0000
2009-09-30,2539.0000
2009-12-31,2510.0000
2010-03-31,2345.0000
2010-06-30,1609.0000
2010-09-30,2128.0000
2010-12-31,981.0000
2011-03-31,2282.0000
2011-06-30,2602.0000
2011-09-30,3270.0000
2011-12-31,2973.0000
2012-03-31,3087.0000
2012-06-30,3478.0000
"""

@test
class TestYchartsProvider():
  """Tests for the YchartsProvider class."""
  
  @test(groups=['setup'])
  def setup(self):   
    """Setup a YchartsPovider object for testing"""
    self.provider = YchartsProvider('GOOG', StringIO(GOOG_DATA), ['free_cash_flow'])
  
  @test(depends_on_groups=['setup'])
  def test_get_all_before(self):
    """Test the get_all_before method."""
    results = self.provider.get_all_before('free_cash_flow', date(2010, 1, 1))
    assert_equal(len(results), 26)
    assert_equal(results[0], 116621000.0)
    assert_equal(results[-1], 2539000000.0)
  
  @test(depends_on_groups=['setup'])
  def test_get_most_recent(self):
    """Test the get_most_recent method."""
    result = self.provider.get_most_recent('free_cash_flow', date(2010, 1, 1))
    assert_equal(result, 2539000000.0)
    
  @test(depends_on_groups=['setup'])
  def test_get_next_date(self):
    """Test the get_next_date method."""
    result = self.provider.get_next_date(date(2011, 10, 1))
    assert_equal(result, date(2011, 10, 27))

  
  @test(depends_on_groups=['setup'])
  def get_first_date(self):    
    """Test the get_first_date method."""
    result = self.provider.get_first_date()
    assert_equal(result, date(2004,8,17))
if __name__ == "__main__":
  from proboscis import TestProgram
  TestProgram().run_and_exit()