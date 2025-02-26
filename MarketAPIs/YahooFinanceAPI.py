import time;
import yfinance as yf;
import pandas as pd;

from MarketAPIs.MarketAPI import MarketAPI

class YahooFinanceAPI(MarketAPI):
  def __init__(self, symbol):
    super().__init__(symbol);
    self.ticker = yf.Ticker(symbol);
    
  def getStockPrice(self):
    try:
      latest_price = self.ticker.history(period="1d")["Close"].iloc[-1];
      return round(latest_price, 2);
    except Exception as e:
      return {"error": str(e)};
    
  def getHistoricalData(self, period, interval):
    try:
      history = self.ticker.history(period=period,interval=interval);
      return history;
    except Exception as e:
      print(f"[ERROR]: An error has occured while getting historical data: {str(e)}");
      return None;
    
  def streamLivePrice(self, interval=2):
    try:
      while True:
        latest_price = self.getStockPrice();
        print(f"[LIVE PRICE REPORT] Live {self.symbol} Price: ${latest_price['price']}")
        time.sleep(interval)
    except KeyboardInterrupt:
        print("[LIVE PRICE REPORT PAUSED] Stopped Live Streaming")

    

