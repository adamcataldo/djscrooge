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
from djscrooge.test.library.end_of_day.test_end_of_day import TestEndOfDay
from djscrooge.library.end_of_day.mongodb_cache import MongodbCache

@test()
class TestMongodbCache(TestEndOfDay):
  """Tests the Yahoo EndOfDay class."""
  
  def __init__(self):
    super(TestMongodbCache, self).__init__(MongodbCache)   

if __name__ == "__main__":
  from proboscis import TestProgram
  TestProgram().run_and_exit()