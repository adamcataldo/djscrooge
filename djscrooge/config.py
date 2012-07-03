"""This file contains the Configuration definitions of the DJ Scrooge backtesting API.
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
    
Change these values to change the configuration used during runtime.
"""

class Config(object):
  """Contains all configurations objects, avaliable as attributes."""
  
  BACKTEST_SYMBOL_FOR_ALL_DATES = 'GE'

  @property
  def CACHE_END_OF_DAY_SOURCE_CLASS(self):
    import djscrooge.library.end_of_day.yahoo
    return djscrooge.library.end_of_day.yahoo.Yahoo
  
  @property
  def MONGODB_CONNECTION(self):
    import pymongo
    return pymongo.Connection()