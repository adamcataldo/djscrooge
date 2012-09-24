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
from proboscis.asserts import assert_equal
from djscrooge.library.financials.edgar import Edgar
from datetime import date

@test
class TestEdgar():
  """Tests for the Edgar class."""
  
  @test
  def test_get_latest_filing(self):
    """Test the get_latest_filing method."""
    x = Edgar('GOOG')
    assert_equal(x.get_latest_filing(date(2011, 10, 26)), date(2011, 6, 30))
    assert_equal(x.get_latest_filing(date(2011, 10, 27)), date(2011, 9, 30))
    assert_equal(x.get_latest_filing(date(2012, 1, 26)), date(2011, 9, 30))
    assert_equal(x.get_latest_filing(date(2012, 1, 27)), date(2011, 12, 31))
    
if __name__ == "__main__":
  from proboscis import TestProgram
  TestProgram().run_and_exit()