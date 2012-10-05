"""This file contains the edgar module of the DJ Scrooge backtesting API.
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
from urllib2 import urlopen
from lxml.etree import parse, HTMLParser
from datetime import datetime, timedelta
from djscrooge.util.async_http_client import AsyncHttpClient
from StringIO import StringIO
from asyncore import loop
from djscrooge.util.data_types import glb_index_in_sorted_list

class EdgarClient(AsyncHttpClient):
  """An HTTP client used to fetch a single return from Edgar."""

  def __init__(self, url, output_array, index):
    """Create an Edgar client to write the pair (filing_date, period_date) on the 
    output_array at index 'index'."""
    self.output_array = output_array
    self.index = index
    AsyncHttpClient.__init__(self, url)
  
  def handle_completion(self, response_string):
    date_format = '%Y-%m-%d'
    report = parse(StringIO(response_string), HTMLParser())    
    filing_date =report.xpath('id("formDiv")/div[2]/div[1]/div[2]')[0].text
    filing_date = datetime.strptime(filing_date, date_format).date()
    period_date = report.xpath('id("formDiv")/div[2]/div[2]/div[2]')[0].text
    period_date = datetime.strptime(period_date, date_format).date()                                    
    self.output_array[self.index] = (filing_date, period_date)    
  
class Edgar(object):
  """Class for discovering the latest financial statements at a given date.
  
  This class is associated with a single ticker symbol. You pass a simulation
  date to the get_latest_filing method to get the end date of the last period
  for which financial statements had been submitted to the SEC. This way you
  can ensure your strategy cannot see into the future with respect to quarterly
  or annual financial statements.
  """
  
  def __init__(self, symbol):
    """Create a new Edgar object for the given ticker symbol."""
    self.symbol = symbol
    annual_dates = self.__get_reporting_dates(True)
    quarterly_dates = self.__get_reporting_dates(False)
    n = len(annual_dates)
    m = len(quarterly_dates)
    i = 0
    j = 0
    dates = []
    while i < n or j < m:
      if i == n:
        dates.append(quarterly_dates[j])
        j += 1
      elif j == m:
        dates.append(annual_dates[i])
        i += 1
      elif annual_dates[i][0] <= quarterly_dates[j][0]:
        dates.append(annual_dates[i])
        i += 1
      else:
        dates.append(quarterly_dates[j])
        j += 1
    self.filing_dates = [x[0] for x in dates]
    self.period_end_dates = [x[1] for x in dates]
    self.period_to_filing = {}
    for i in range(0, len(self.period_end_dates)):
      self.period_to_filing[self.period_end_dates[i]] = self.filing_dates[i]
  
  def __get_reporting_dates(self, is_annual):
    """Gets all annual or quarterly financial statement reporting dates.
    
    If is_annual is true, this returns the annual reporting statement dates.
    Otherwise, this returns the quarterly reporting statement dates.
    
    The return value is a list of tuples of form (filing_date, period_end_date), ordered from 
    least recent to most recent filing_date. Each is a datetime.date object.
    """
    symbol = self.symbol
    ns = { 'a' : 'http://www.w3.org/2005/Atom' }
    start_url = 'http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK='
    if is_annual:
      end_url = '&type=10-K%25&dateb=&owner=exclude&start=0&count=100&output=atom'
    else:
      end_url = '&type=10-Q%25&dateb=&owner=exclude&start=0&count=100&output=atom'
    url = start_url + symbol + end_url
    f = urlopen(url)
    ten_k_feed = parse(f)
    if is_annual:
      entry_path = '/a:feed/a:entry[a:category/@term="10-K" or a:category/@term="10-K405"]'
    else:
      entry_path = '/a:feed/a:entry[a:category/@term="10-Q"]'
    entries = ten_k_feed.xpath(entry_path, namespaces = ns)
    dates = [None] * len(entries)
    for i in range(0, len(entries)):
      entry = entries[i]
      href = entry.xpath('a:link/@href', namespaces = ns)[0]
      EdgarClient(href, dates, i)
    loop()
    dates.reverse()
    return dates
  
  def get_latest_filing(self, simulation_date):
    """Given the simulation_date, return the last filing period submitted to Edgar.
    
    This returns None if the given simulation_date occurs before the earliest filing
    with Edgar.
    """
    i = glb_index_in_sorted_list(simulation_date - timedelta(1), self.filing_dates)
    if i == -1:
      return None
    return self.period_end_dates[i]
  
  def get_filing_date(self, period_end_date):
    """Given the period end date, returns the filing date.
    
    This raises a ValueError if the period_end_date is not found.
    """
    if not self.period_to_filing.has_key(period_end_date):
      raise ValueError('No filing for %s.' % period_end_date.strftime('%Y-%m-%d'))
    return self.period_to_filing[period_end_date]