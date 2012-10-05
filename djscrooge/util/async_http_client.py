"""This file contains the async_http_client of the Pengoe Backtesting API.
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
from asyncore import dispatcher
from socket import AF_INET, SOCK_STREAM
from StringIO import StringIO
from urlparse import urlparse

class AsyncHttpClient(dispatcher):
  """This convenience class is a wrapper around the asyncore.dispatcher 
  object to make it simple to create asyncronous HTTP GET requests.
  
  Subclasses should implement the handle_completion to process the
  returned data. This method takes in an argument returning the retrieved
  data as a string.
  """

  def __init__(self, url):
    self.url = url
    self.parsed_url = urlparse(url)
    dispatcher.__init__(self)
    self.write_buffer = 'GET %s HTTP/1.0\r\n\r\n' % self.url
    self.read_buffer = StringIO()
    self.create_socket(AF_INET, SOCK_STREAM)
    address = (self.parsed_url.netloc, 80)
    self.connect(address)
    
  def handle_completion(self, response_string):
    """Sublcasses should implement this. 
    
    The response_string is the returned data as a string."""
    raise NotImplementedError("handle_completion must be implemented by a subclass.")

  def handle_close(self):
    """Close the socket and call the handle_completion method."""
    self.close()
    x = self.read_buffer.getvalue()
    i = x.find("\r\n\r\n")
    val = x[i+4:]
    self.handle_completion(val)

  def writable(self):
    """Return True until the request has been made."""
    return (len(self.write_buffer) > 0)

  def readable(self):
    """This is always True."""
    return True

  def handle_write(self):
    """Send the request."""
    sent = self.send(self.write_buffer)
    self.write_buffer = self.write_buffer[sent:]

  def handle_read(self):
    """Handle the next chunk of recieved data."""
    data = self.recv(8192)
    self.read_buffer.write(data)    
