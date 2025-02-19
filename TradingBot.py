import ta.momentum
import ta.volatility
from YahooFinanceAPI import YahooFinanceAPI;
import pandas as pd;
import numpy as np;
import ta;

class TradingBot:
  def __init__(self, symbol, period, interval, cash, trading_tax):
    print(f"Initializing trading bot for {symbol}");
    self.symbol = symbol;
    self.period = period;
    self.interval = interval;
    self.yahoo_finance_api = YahooFinanceAPI(symbol);
    self.initial_cash = cash;
    self.cash = cash;
    self.shares = 0;
    self.entry_price = None;
    self.trading_tax = trading_tax; # In $
    
    # Cache trading logs data
    self.trade_log = [];
    
    # Fetch data to use to analyze trends
    df = self.fetchData(period, interval);
    print(f"Data fetched for over {period} at {interval} interval.");

    # Calculte Indicators on past data     
    self.data = self.calculateIndicators(df);
    print(f"Indicators calculated")

    # Calculate Volatility and create dynamic stop loss and profit take values
    self.stop_loss_price, self.profit_take_price = self.calculateDynamicRiskParameters();
    print(f"Dynamic risk parameters calculated | Stop Loss: ${self.stop_loss_price:.2f} | Profit Take: ${self.profit_take_price:.2f}");
    
  def fetchData(self, period, interval):
    df = self.yahoo_finance_api.getHistoricalData(period=period, interval=interval);
    
    if df.empty:
      print(f"No historical data found for {self.symbol}. Check API or market status.")
      return
    
    # Drop rows with missing values
    df.dropna(inplace=True)

    # Convert close to a 1d array shape
    df["Close"] = df["Close"].values.ravel();

    # Store the data and calculate indicators to be used
    self.data = self.calculateIndicators(df);
    return self.data;
  
  def calculateDynamicRiskParameters(self):
    # Get the latest ATR value
    atr_value = self.data["ATR"].iloc[-1];

    # Calculate actual stop loss and profit take prices
    raw_stop_loss_price = atr_value * 1.5;
    raw_take_profit_price = atr_value * 3;
    
    # Include tax consideration, trading tax is multiplied by 2 because buy and sell usually applies the trading tax
    adjusted_stop_loss_price = raw_stop_loss_price + ((self.trading_tax * 2) / self.data["Close"].iloc[-1]);
    adjusted_take_profit_price = raw_take_profit_price + ((self.trading_tax * 2) / self.data["Close"].iloc[-1]);
    
    return adjusted_stop_loss_price, adjusted_take_profit_price;

  def calculateIndicators(self, df):
    df = df.copy();
    
    # Moving average data of the last n data points
    df["SMA_9"] = df["Close"].rolling(window=9).mean();
    df["SMA_20"] = df["Close"].rolling(window=20).mean();
    df["SMA_30"] = df["Close"].rolling(window=30).mean();
    df["SMA_40"] = df["Close"].rolling(window=40).mean();
    df["SMA_50"] = df["Close"].rolling(window=50).mean();
    
    # Calculate VWAP (Weighted Average)
    df["VWAP"] = (df["Close"] * df["Volume"]).cumsum() / df["Volume"].cumsum();
    
    # Relative Strength Index (Momentum Indicator)
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"].squeeze(),window=14).rsi();
    
    # MACD (Moving Average Convergence Divergence)
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_Signal"] = macd.macd_signal();
    
    # Calculate average true range (Volatility measure)
    df["ATR"] = ta.volatility.AverageTrueRange(high=df["High"], low=df["Low"], close=df["Close"], window=14).average_true_range();
    return df;
  
  def updateLastRowIndicator(self, df):
    df = df.copy();
    
    # Moving average data of the last n data points
    df["SMA_9"] = df["Close"].rolling(window=9).mean();
    df["SMA_20"] = df["Close"].rolling(window=20).mean();
    df["SMA_30"] = df["Close"].rolling(window=30).mean();
    df["SMA_40"] = df["Close"].rolling(window=40).mean();
    df["SMA_50"] = df["Close"].rolling(window=50).mean();
    
    # Calculate VWAP (Weighted Average)
    df["VWAP"] = (df["Close"] * df["Volume"]).cumsum() / df["Volume"].cumsum();
    
    # Relative Strength Index (Momentum Indicator)
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"],window=14).rsi();
    
    # MACD (Moving Average Convergence Divergence)
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_Signal"] = macd.macd_signal();
    
    # Calculate average true range (Volatility measure)
    df["ATR"] = ta.volatility.AverageTrueRange(high=df["High"], low=df["Low"], close=df["Close"], window=14).average_true_range();
    return df;
  
  def checkTradeSignal(self, row):  
    # Check if holding shares and create an exit condition.
    if self.shares > 0 and self.entry_price is not None:
  
      # Because the stop_loss_price and profit_take_price are offsets, we need to apply it to our entry price
      if row["Close"] <= (self.entry_price - self.stop_loss_price):
        return "SELL";

      if row["Close"] >= (self.entry_price + self.profit_take_price):
        return "SELL";
    
    # STRONG UPTREND CHECK: This is a strict uptrend checker that signals immediate buy
    uptrend = (row["SMA_9"] > row["SMA_20"]) and (row["SMA_20"] > row["SMA_40"]);
    
    # LENIENT MACD CROSSOVER CHECK: Allows for earlier trend detection and earlier entry
    macd_crossover = (row["MACD"] > row["MACD_Signal"]) and (row["MACD"] > 0); # Bullish cross over
    
    # MOMENTUM CHECK: Looks for momentum in the trend
    momentum_ok = (row["RSI"] > 50) and (row["RSI"] < 80);
    
    # PRICE CHECK: Price confirmation
    price_above_vwap = row["Close"] > row["VWAP"];

    # If we see strong uptrend or a macd_crossover we can look to buy
    if (uptrend or macd_crossover) and momentum_ok and price_above_vwap:
      return "BUY";
    
    # HOLD (No clear signal)
    return "HOLD"
  
  def executeTrade(self, action, price):
    if action == "BUY":
      # We must have enough left over to make a trade to sell;
      # Remove trading tax intentionally to reduce our purchasing power;
      available_cash = self.cash - self.trading_tax;
      if (available_cash >= price):
        purchased_shares = available_cash // price;
        total_cost = (purchased_shares * price + self.trading_tax);
        self.cash -= total_cost;
        self.shares += purchased_shares;
        
        self.entry_price = price;
        
        self.trade_log.append((action, price, total_cost, purchased_shares))
        # print(f"Bought {purchased_shares} shares at ${price:.2f}, Cash Left: ${self.cash:.2f}")

    elif (action == "SELL" and self.shares > 0):
      sold_shares = self.shares;
      net_revenue = (sold_shares * price) - self.trading_tax;
      self.cash += net_revenue;
      self.shares = 0;
      
      self.entry_price = None;
      
      self.trade_log.append((action, price, net_revenue, sold_shares))
      # print(f"Sold {sold_shares} shares at ${price:.2f}, New Balance: ${self.cash:.2f}")

  def printTradeSummary(self):
    print("\nTrade Summary:")
    if not self.trade_log:
      print("No trades executed.")
      return

    df_trades = pd.DataFrame(self.trade_log)
    print(df_trades)
