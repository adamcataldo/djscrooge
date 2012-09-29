"""This file contains the test_async_http_client module of the Pengoe Backtesting API.
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
from djscrooge.util.async_http_client import AsyncHttpClient
from asyncore import loop

class GoogleClient(AsyncHttpClient):
  """A handler for requests from Google."""
  
  def __init__(self, result_array):
    """The client should write True in the first element of result_array
    if it gets a proper request from Google."""
    AsyncHttpClient.__init__(self, 'http://www.google.com')
    self.result_array = result_array
    
  def handle_completion(self, response_string):
    """Handle the retrieved data."""
    self.result_array[0] = "I'm Feeling Lucky" in response_string
    
class WikiClient(AsyncHttpClient):
  """A handler for requests from Wikipedia."""
  
  def __init__(self, result_array):
    """The client should write True in the second element of result_array
    if it gets a proper request from Wikipedia.org."""
    AsyncHttpClient.__init__(self, 'http://www.wikipedia.org')
    self.result_array = result_array
    
  def handle_completion(self, response_string):
    """Handle the retrieved data."""
    self.result_array[1] = 'Wikipedia' in response_string
    
@test
class TestAsyncHttpClient(object):
  """Tests for the AsyncHttpClient class."""
  
  @test
  def test_loop(self):
    """Tests parallel HTTP requests."""
    result_array = [False, False]
    GoogleClient(result_array)
    WikiClient(result_array)
    loop()
    assert_equal(result_array, [True, True])
    
if __name__ == "__main__":
  from proboscis import TestProgram
  TestProgram().run_and_exit()