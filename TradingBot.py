import ta.momentum
from YahooFinanceAPI import YahooFinanceAPI;
import pandas as pd;
import ta;
import os;

class TradingBot:
  def __init__(self, symbol, period, interval):
    self.symbol = symbol;
    self.yahoo_finance_api = YahooFinanceAPI(symbol);
    self.fetchData(period, interval);
  
  def fetchData(self, period, interval):
    # print(f"[FETCHING] Fetching {self.symbol} data for {period} with {interval} interval...");
    df = self.yahoo_finance_api.getHistoricalData(period=period, interval=interval);
    
    if df.empty:
      print(f"[ERROR] No historical data found for {self.symbol}. Check API or market status.")
      return
    
    # Drop rows with missing values
    df.dropna(inplace=True)

    # Convert close to a 1d array shape
    df["Close"] = df["Close"].values.ravel();

    # Store the data and calculate indicators to be used
    self.data = self.calculateIndicators(df);
    return self.data;
  
  def calculateIndicators(self, df):
    df = df.copy();
    
    # Moving average data of the last n data points
    df["SMA_9"] = df["Close"].rolling(window=9).mean();
    df["SMA_20"] = df["Close"].rolling(window=20).mean();
    df["SMA_30"] = df["Close"].rolling(window=30).mean();
    df["SMA_40"] = df["Close"].rolling(window=40).mean();
    df["SMA_50"] = df["Close"].rolling(window=50).mean();
    
    # Calculate Typical price (Short term trend detection)
    df["TP"] = (df["High"] + df["Low"] + df["Close"]) / 3;
    
    # Calculate VWAP (Weighted Average)
    df["VWAP"] = (df["Close"] * df["Volume"]).cumsum() / df["Volume"].cumsum();
    
    # Relative Strength Index (Momentum Indicator)
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"].squeeze(),window=14).rsi();
    
    # MACD (Moving Average Convergence Divergence)
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_Signal"] = macd.macd_signal()

    return df;
  
  def checkTradeSignal(self, row):    
    # SAFER ENTRY
    # Safer entry reduces profits but is safer, works better with 1m interval 
    # For more safety increase SMA_30
    uptrend = (row["SMA_9"] > row["SMA_20"]) and (row["SMA_20"] > row["SMA_30"]);
    
    # RISKIER ENTRY:
    # Riskier entry combos well with higher interval such as 5m and higher stop loss %
    # uptrend = (row["SMA_9"] > row["SMA_20"])
    
    # Ensure RSI is not in overbought
    momentum_ok = (row["RSI"] > 50) and (row["RSI"] < 80);
    
    price_above_vwap = row["Close"] > row["VWAP"];
    
    if uptrend and momentum_ok and price_above_vwap:
      return "BUY"
    
    # HOLD (No clear signal)
    return "HOLD"