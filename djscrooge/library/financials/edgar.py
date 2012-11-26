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
from datetime import datetime, timedelta, date
from djscrooge.util.async_http_client import AsyncHttpClient
from StringIO import StringIO
from asyncore import loop
from djscrooge.util.data_types import glb_index_in_sorted_list
from math import ceil

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
    self.__sanitize_filing_equals_period(annual_dates, 12)
    quarterly_dates = self.__get_reporting_dates(False)
    self.__sanitize_filing_equals_period(quarterly_dates, 3)
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
      elif annual_dates[i][1] <= quarterly_dates[j][1]:
        dates.append(annual_dates[i])
        i += 1
      else:
        dates.append(quarterly_dates[j])
        j += 1
    self.__sanitize_start_of_month_filing_dates(dates)
    self.__sanitize_off_period_end_dates(dates)
    self.__validate_filing_dates(dates)
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
  
  def __sanitize_filing_equals_period(self, dates, offset):
    """Sanitize any dates where filing_date == period_end_date.
    
    Note that this may fix some edge cases but not others.
    """
    for i in range(0, len(dates)):
      if dates[i][0] == dates[i][1]:
        if i > 0:
          test_month = dates[i-1][1].month + offset
          while test_month > 12:
            test_month -= 12
          if dates[i][1].month != test_month:
            new_month = dates[i-1][1].month + offset + 1
            new_year = dates[i-1][1].year
            while (new_month > 12):
              new_month -= 12
              new_year += 1
            new_period_end_date = date(new_year, new_month, 1) - timedelta(1)
            dates[i] = (dates[i][0], new_period_end_date)
          else:
            delta = timedelta(int(ceil(365.25 * offset / 12.0)))
            dates[i] = (dates[i-1][0] + delta, dates[i][1])
        else:
          test_month = dates[i+1][1].month - offset
          while test_month < 1:
            test_month += 12
          if dates[i][1].month != test_month:
            new_month = dates[i+1][1].month - offset + 1
            new_year = dates[i+1][1].year
            while (new_month < 1):
              new_month += 12
              new_year -= 1
            new_period_end_date = date(new_year, new_month, 1) - timedelta(1)
            dates[i] = (dates[i][0], new_period_end_date)
          else:
            delta = timedelta(int(ceil(365.25 * offset / 12.0)))
            dates[i] = (dates[i+1][0] - delta, dates[i][1])
            
  def __sanitize_start_of_month_filing_dates(self, dates):
    """Sanitize any dates where period_end_date is not at the end of the month.
    """
    for i in range(0, len(dates)):
      if (dates[i][1] + timedelta(1)).day != 1:
        if dates[i][1].day < 15:
          dates[i] = (dates[i][0], date(dates[i][1].year, dates[i][1].month, 1) - timedelta(1))
        else:
          month = dates[i][1].month + 1
          year = dates[i][1].year
          if month > 12:
            month = month - 12
            year = year + 1
          dates[i] = (dates[i][0], date(year, month, 1) - timedelta(1))
          
  def __sanitize_off_period_end_dates(self, dates):
    for i in range(1, len(dates) - 1):
      if (not self.__is_behind_by_months(dates[i-1][1], dates[i][1], 3)):
        if (self.__is_behind_by_months(dates[i-1][1], dates[i+1][1], 6)):
          month = dates[i-1][1].month + 4
          year = dates[i-1][1].year
          if month > 12:
            year = year + 1
            month = month - 12
          dates[i] = (dates[i][0], date(year, month, 1) - timedelta(1))
        elif (self.__is_behind_by_months(dates[i][1], dates[i+1][1], 3)):
          month = dates[i][1].month - 2
          year = dates[i][1].year
          if month < 1:
            year = year - 1
            month = month + 12
          dates[i-1] = (dates[i][0], date(year, month, 1) - timedelta(1))
        else:
          raise ValueError('No obvious recovery from bad end date: ' + dates[i][1].strftime('%Y-%m-%d'))
    if len(dates) > 1:
      n = len(dates)
      if (not self.__is_behind_by_months(dates[n-2][1], dates[n-1][1], 3)):
        month = dates[n-2][1].month + 4
        year = dates[n-2][1].year
        if month > 12:
          year = year + 1
          month = month - 12
        dates[n-1] = (dates[n-1][0], date(year, month, 1) - timedelta(1))
        
  def __validate_filing_dates(self, dates):
    """Validate all filing dates occur AFTER the corresponding period end date."""
    for x in dates:
      if x[0] <= x[1]:
        raise ValueError('Filing date %s came after period end date %s.' % (x[0].strftime('%Y-%m-%d'), x[1].strftime('%Y-%m-%d')))
  
  def __is_behind_by_months(self, x, y, n):
    """Return true iff x's month is n months behind y's month.
    
    n is assumed to be positive.
    """
    month = x.month + n
    year = x.year
    while month > 12:
      month -= 12
      year += 1
    return (y.month == month) and (y.year == year)
          
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