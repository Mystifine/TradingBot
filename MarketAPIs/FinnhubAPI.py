import os;
import requests;
import pandas as pd;
import datetime;

from MarketAPIs.MarketAPI import MarketAPI;
from dotenv import load_dotenv;

class FinnhubAPI(MarketAPI):
  def __init__(self, symbol):
    super().__init__(symbol);
    load_dotenv();
    self.api_key = os.getenv("FINNHUB_IO_API_KEY");
    pass;
  
  def getResolutionFromInterval(self, yf_interval):
    interval_mapping = {
      "1m": "1",
      "2m": "1",  # Finnhub does not support 2m, so default to 1m
      "5m": "5",
      "15m": "15",
      "30m": "30",
      "1h": "60",
      "1d": "D",
      "1wk": "W",
      "1mo": "M"
    }
    return interval_mapping.get(yf_interval, "D");
  
  def getStartTimeEndTimeFromPeriod(self, yf_period):
    end_time = int(datetime.datetime.now().timestamp());
    start_time = end_time;
    period_mapping = {
      "1d": 1 * 24 * 60 * 60,  # 1 day in seconds
      "5d": 5 * 24 * 60 * 60,
      "1mo": 30 * 24 * 60 * 60,  # Approximate for 1 month
      "3mo": 90 * 24 * 60 * 60,  # Approximate for 3 months
      "6mo": 180 * 24 * 60 * 60,
      "1y": 365 * 24 * 60 * 60,
      "2y": 2 * 365 * 24 * 60 * 60,
      "5y": 5 * 365 * 24 * 60 * 60,
      "10y": 10 * 365 * 24 * 60 * 60,
      "ytd": (datetime.datetime.now() - datetime.datetime(datetime.datetime.now().year, 1, 1)).total_seconds(),
      "max": 50 * 365 * 24 * 60 * 60  # 50 years (approximate for max history)
    }
    if yf_period in period_mapping:
      start_time = end_time - period_mapping[yf_period];
    
    return start_time, end_time;
  
  def getStockPrice(self):
    url = f"https://finnhub.io/api/v1/quote?symbol={self.symbol}&token={self.api_key}";
    response = requests.get(url=url);
    data = response.json();
    return data['c'];
  
  def getHistoricalData(self, period, interval):

    start_time, end_time = self.getStartTimeEndTimeFromPeriod(period);
    resolution = self.getResolutionFromInterval(interval);
    
    url = f"https://finnhub.io/api/v1/stock/candle?symbol={self.symbol}&resolution={resolution}&from={start_time}&to={end_time}&token={self.api_key}"
    response = requests.get(url)
    data = response.json();

    if data["s"] == "ok":
      df = pd.DataFrame({
        "Time": [datetime.datetime.fromtimestamp(t) for t in data["t"]],
        "Open": data["o"],
        "High": data["h"],
        "Low": data["l"],
        "Close": data["c"],
        "Volume": data["v"],
      });
      return df;
    else:
      print("Error fetching data");
      return None;
           
  