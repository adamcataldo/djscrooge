"""This file contains the postgres_cache module of the DJ Scrooge backtesting API.
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
    sqlalchemy: <http://www.sqlalchemy.org/>
"""

from djscrooge.config import Config
from djscrooge.backtest import EndOfDay
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
import djscrooge.backtest

def postgres(end_of_day_source_class=Config().POSTGRES_CACHE_END_OF_DAY_SOURCE_CLASS):
  """Returns a Postgres object, which is used to cache data.
  
  end_of_day_source_class -- The class responsible for getting data to feed the cache.
  
  The Postgres object is an EndOfDay subclass, which should provide fast access to the 
  data already downloaded. This is critical for big experiments. It is lazy in that it only 
  gets data it needs to. This function will automatically create all DB tables the first
  time it is called on a new database.
  
  The djscrooge.config.POSTGRES_CONNECTION_STRING is used to determine the connection to the
  database.
  """
  engine = create_engine(Config().POSTGRES_CONNECTION_STRING)
  Base = declarative_base()
  class Symbol(Base):
    __tablename__ = 'symbol'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)
    last_update = Column(Date, nullable=False)
    last_adj_close = Column(Integer, nullable=False)
    last_adj_close_date = Column(Date, nullable=False)
    
    def __init__(self, symbol, last_update, last_adj_close, last_adj_close_date):
      self.symbol = symbol
      self.last_update = last_update
      self.last_adj_close = last_adj_close
      self.last_adj_close_date = last_adj_close_date
  
  class Price(Base):
    __tablename__ = 'price'
    __table_args__ = (PrimaryKeyConstraint('id', 'date'),)
    
    id = Column(Integer, ForeignKey('symbol.id'), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Integer, nullable=False)    
    high = Column(Integer, nullable=False)    
    low = Column(Integer, nullable=False)    
    close = Column(Integer, nullable=False)    
    adj_close = Column(Integer, nullable=False)    
    volume = Column(Integer, nullable=False)   
    
    def __init__(self, id, date, open, high, low, close, adj_close, volume):
      self.id = id
      self.date = date
      self.open = open
      self.high = high
      self.low = low
      self.close = close
      self.adj_close = adj_close
      self.volume = volume
      
  class Dividend(Base):
    __tablename__ = 'dividend'
    __table_args__ = (PrimaryKeyConstraint('id', 'date'),)
    
    id = Column(Integer, ForeignKey('symbol.id'), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Integer, nullable=False)
    
    def __init__(self, id, date, amount):
      self.id = id
      self.date = date
      self.amount = amount
      
  class Split(Base):
    __tablename__ = 'split'
    __table_args__ = (PrimaryKeyConstraint('id', 'date'),)
    
    id = Column(Integer, ForeignKey('symbol.id'), nullable=False)
    date = Column(Date, nullable=False)
    numerator = Column(Integer, nullable=False)
    denominator = Column(Integer, nullable=False)
    
    def __init__(self, id, date, split):
      self.id = id
      self.date = date
      self.numerator = split.numerator
      self.denominator = split.denominator
    
  Base.metadata.create_all(engine)  
  
  Session = sessionmaker(bind=engine)
  
  def upload_all_data(session, eod, symbol, stock_id, start=0):
    n = len(eod.dates)
    for i in range(start, n):
      session.add(Price(stock_id, eod.dates[i], eod.open_prices[i], eod.high_prices[i], eod.low_prices[i], eod.close_prices[i], eod.adj_close_prices[i], eod.volumes[i]))
      if eod.dividends[i] is not None:
        session.add(Dividend(stock_id, eod.dates[i], eod.dividends[i]))
      if eod.splits[i] is not None:
        session.add(Split(stock_id, eod.dates[i], eod.splits[i]))
    session.commit()
       
  class Postgres(EndOfDay):
    
    def __init__(self, symbol, start_date, end_date):
      super(Postgres, self).__init__(symbol, start_date, end_date)
      today = datetime.now().date()
      session = Session()
      try:
        row = session.execute("SELECT min(id) AS id FROM symbol WHERE symbol = '%s'" % symbol).first()
        stock_id = row['id']
        if stock_id is None:
          eod = end_of_day_source_class(symbol, date(1900,1,1), today)
          n = len(eod.open_prices)
          session.add(Symbol(symbol, today, eod.adj_close_prices[n-1], eod.dates[n-1]))
          stock_id = session.query(Symbol.id).filter(Symbol.symbol == symbol).first()[0]
          upload_all_data(session, eod, symbol, stock_id)          
        else:
          symbol_data = session.query(Symbol).filter(Symbol.id == stock_id).first()
          last_update = symbol_data.last_update
          last_adj_close = symbol_data.last_adj_close
          last_adj_close_date = symbol_data.last_adj_close_date
          if last_update < end_date:
            eod = end_of_day_source_class(symbol, last_adj_close_date, today)
            if eod.adj_close_prices[0] != last_adj_close:
              session.execute("DELETE FROM price WHERE symbol = '%s'" % symbol)
              eod = end_of_day_source_class(symbol, date(1900,1,1), today)
              upload_all_data(session, eod, symbol, stock_id)
            elif len(eod.dates) > 1:
              upload_all_data(session, eod, symbol, stock_id, 1)
        prices = session.query(Price).filter(Price.id == stock_id).filter(Price.date >= start_date).filter(Price.date <= end_date)
        for price in prices:
          self.open_prices.append(price.open)
          self.high_prices.append(price.high)
          self.low_prices.append(price.low)
          self.close_prices.append(price.close)
          self.adj_close_prices.append(price.adj_close)
          self.volumes.append(price.volume)
          self.dates.append(price.date)  
          self.dividends.append(None)
          self.splits.append(None)
          
        dividends = session.query(Dividend.date, Dividend.amount).filter(Dividend.id == stock_id).filter(Dividend.date >= start_date).filter(Dividend.date <= end_date)
        for dividend in dividends:
          i = self.get_index_from_date(dividend.date)
          self.dividends[i] = dividend.amount
        splits = session.query(Split.date, Split.numerator, Split.denominator).filter(Split.id == stock_id).filter(Split.date >= start_date).filter(Split.date <= end_date)
        for split in splits:
          i = self.get_index_from_date(split.date)
          self.splits[i] =  djscrooge.backtest.Split(split.numerator, split.denominator)    
      finally:
        session.close()
          
  return Postgres
      