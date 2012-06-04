"""This file contains the main test procedure of the DJ Scrooge backtesting API.
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

import os
import pkgutil
import djscrooge.test

if __name__ == '__main__':
  """Calling this file as the main script to run will invoke all tests."""
  dir = os.path.dirname(djscrooge.test.__file__)
  for p in pkgutil.walk_packages('djscrooge.test'):
    __import__('djscrooge.test.' + p[1], globals(), locals(), [], -1)
  from proboscis import TestProgram
  TestProgram().run_and_exit()