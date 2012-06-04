"""This file contains the test_postgres_cache module of the DJ Scrooge backtesting API.
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
    sqlalchemy: <http://www.sqlalchemy.org/>
"""
from proboscis import test
from proboscis.asserts import assert_equal
from djscrooge.test.library.end_of_day.test_end_of_day import TestEndOfDay
from djscrooge.library.end_of_day.postgres_cache import postgres
from datetime import date

@test(depends_on_groups=['csv'])
class TestPostgres(TestEndOfDay):
  """Tests the Yahoo EndOfDay class."""
  
  def __init__(self):
    super(TestPostgres, self).__init__(postgres())   
    
  @test
  def test_tie(self):
    """Test that a single day for TIE works."""
    eod_class = postgres()
    eod = eod_class('TIE', date(2002, 1, 15), date(2002, 1, 15))
    assert_equal(len(eod.close_prices), 1)
    assert_equal(len(eod.dividends), 1)
    assert_equal(len(eod.splits), 1)

if __name__ == "__main__":
  from proboscis import TestProgram
  TestProgram().run_and_exit()