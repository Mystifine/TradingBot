import os;
import pandas as pd;

from ib_insync import *;
from MarketAPIs.MarketAPI import MarketAPI;
from dotenv import load_dotenv;

class IBKRAPI(MarketAPI):
  def __init__(self, symbol):
    load_dotenv();
    
    super().__init__(symbol);
    
    self.ib = IB();
    self.contract = Stock(self.symbol, 'SMART', "USD");
    self.port = None;
    
    trading_state = os.getenv("IBKR_TRADE_STATE")
    if trading_state == "LIVE":
      self.port = os.getenv("IBKR_LIVE_TRADING_PORT");
    elif trading_state == "PAPER":
      self.port = os.getenv("IBKR_PAPER_TRADING_PORT");
    self.connect();
    pass;
  
  def connect(self):
    if self.ib.isConnected():
      return;
    
    if self.port is None:
      print("IBKR Port is not initialized");
      return;
    
    self.ib.connect('127.0.0.1', self.port, clientId=1);
    print(f"IBKR Connected: {self.ib.isConnected()}");
    
  def getPeriodFromYFPeriod(self, yf_period):
    yf_to_ibkr_period = {
      '1d': '1 D', '5d': '5 D', '1mo': '1 M', '3mo': '3 M',
      '6mo': '6 M', '1y': '1 Y', '2y': '2 Y', '5y': '5 Y',
      '10y': '10 Y', 'max': '20 Y'
    }
    
    return yf_to_ibkr_period.get(yf_period, '1 D');
  
  def getIntervalFromYFInterval(self, yf_interval):
    yf_to_ibkr_interval = {
      '1m': '1 min', '5m': '5 mins', '15m': '15 mins',
      '30m': '30 mins', '1h': '1 hour', '1d': '1 day',
      '1wk': '1 week', '1mo': '1 month'
    }
    
    return yf_to_ibkr_interval.get(yf_interval, '1 day');
    
  def disconnect(self):
    if self.ib.isConnected():
      self.ib.disconnect();
  
  def getHistoricalData(self, period, interval):
    duration = self.getPeriodFromYFPeriod(period);
    bar_size = self.getIntervalFromYFInterval(interval);
    
    contract = self.contract;
    
    bars = self.ib.reqHistoricalData(
      contract,
      endDateTime='',
      durationStr=duration,
      barSizeSetting=bar_size,
      whatToShow='MIDPOINT',
      useRTH=False,
      formatDate=1,
    )
    
    df = pd.DataFrame(bars);
    
    df.rename(
      columns={
        'date': 'Datetime', 
        'open': 'Open', 
        'high': 'High',
        'low': 'Low', 
        'close': 'Close', 
        'volume': 'Volume'
      }, 
      inplace=True
    )
    
    df.set_index('Datetime',inplace=True);
    
    return bars;
  
  def getStockPrice(self):
    contract = self.contract;
    market_data = self.ib.reqMktData(contract);
    return market_data.last;