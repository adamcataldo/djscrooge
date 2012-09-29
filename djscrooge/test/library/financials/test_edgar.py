"""This file contains the test_edgar module of the Pengoe Backtesting API.
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
from proboscis.asserts import assert_equal, assert_raises
from djscrooge.library.financials.edgar import Edgar
from datetime import date

@test
class TestEdgar():
  """Tests for the Edgar class."""
  
  @test(groups=['setup'])
  def setup_edgar_object(self):
    """Setup an Edgar object for testing."""
    self.edgar_obj = Edgar('GOOG')
  
  @test(depends_on_groups=['setup'])
  def test_get_latest_filing(self):
    """Test the get_latest_filing method."""
    x = self.edgar_obj
    assert_equal(x.get_latest_filing(date(2011, 10, 26)), date(2011, 6, 30))
    assert_equal(x.get_latest_filing(date(2011, 10, 27)), date(2011, 9, 30))
    assert_equal(x.get_latest_filing(date(2012, 1, 26)), date(2011, 9, 30))
    assert_equal(x.get_latest_filing(date(2012, 1, 27)), date(2011, 12, 31))
    
  @test(depends_on_groups=['setup'])
  def test_get_filing_date(self):
    """Test the test_get_filing_date method."""
    x = self.edgar_obj
    assert_equal(x.get_filing_date(date(2011, 9, 30)), date(2011, 10, 26))
    assert_equal(x.get_filing_date(date(2011, 12, 31)), date(2012, 1, 26))
    assert_raises(ValueError, x.get_filing_date, date(2012, 1, 1))

if __name__ == "__main__":
  from proboscis import TestProgram
  TestProgram().run_and_exit()