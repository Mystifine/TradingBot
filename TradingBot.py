import ta.momentum
import ta.volatility
from YahooFinanceAPI import YahooFinanceAPI;
import pandas as pd;
import numpy as np;
import ta;
import datetime;

class TradingBot:
  def __init__(self, symbol, period, interval, cash, trading_tax):
    print(f"Initializing trading bot for {symbol}");
    self.symbol = symbol;
    self.period = period;
    self.interval = interval;
    self.yahoo_finance_api = YahooFinanceAPI(symbol);
    
    self.trading_tax = trading_tax; # In $
    self.initial_cash = cash;
    self.cash = cash;
    self.shares = 0;
    self.trading_tax = trading_tax; # In $

    self.highest_marked_priced = None;
    self.entry_price = None;
    
    # Cache trading logs data
    self.trade_log = [];
    
    # Fetch data to use to analyze trends
    df = self.fetchData(period, interval);
    print(f"Data fetched for over {period} at {interval} interval.");

    # Calculte Indicators on past data     
    self.data = self.calculateIndicators(df);
    print(f"Indicators calculated")

    # Calculate Volatility and create dynamic stop loss value
    self.stop_loss_price = self.calculateStopLossPrice();
    print(f"Risk parameters computed | Stop Loss: ${self.stop_loss_price:.2f}");
    
  def fetchData(self, period, interval):
    df = self.yahoo_finance_api.getHistoricalData(period=period, interval=interval);
    
    if df.empty:
      print(f"No historical data found for {self.symbol}. Check API or market status.")
      return
    
    # Drop rows with missing values
    df.dropna(inplace=True);

    df.sort_index(ascending=True,inplace=True); # Oldest to newest
    
    # Store the data and calculate indicators to be used
    self.data = self.calculateIndicators(df);
    return self.data;
  
  def calculateStopLossPrice(self):
    # Calculate stop loss using average true range, ATR is how much the stock changes it price
    # Used as a volatility measaurement
    average_true_range = self.data["ATR"].iloc[-1];
    
    last_close = self.data["Close"].iloc[-1];
    sma_50 = self.data["SMA_50"].iloc[-1];
    relative_strength_index = self.data["RSI"].iloc[-1];
    macd = self.data["MACD"].iloc[-1];
    macd_signal= self.data["MACD_Signal"].iloc[-1];
    
    # By default set the stop loss price to the average true range * 2
    atr_multiplier = 2;
    if (last_close > sma_50 and relative_strength_index > 60 and macd > macd_signal):
      # Allow for more growth in strong bullish markets
      atr_multiplier = 3;
    elif (last_close < sma_50 and relative_strength_index < 40 and macd < macd_signal):
      # Cut losses in bad trends
      atr_multiplier = 1.5;
    else:
      # In average market 
      atr_multiplier = 2;
    
    stop_loss_price = average_true_range * atr_multiplier;
    
    return stop_loss_price;

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
  
  def checkTradeSignal(self, row):  
    buy_signal = False;
        
    # STRONG UPTREND CHECK: This is a strict uptrend checker that signals immediate buy
    uptrend = (row["SMA_9"] > row["SMA_20"]) and (row["SMA_20"] > row["SMA_40"]) and (row["SMA_40"] > row["SMA_50"]);
  
    # LENIENT MACD CROSSOVER CHECK: Allows for earlier trend detection and earlier entry
    macd_crossover = (row["MACD"] > row["MACD_Signal"]) and (row["MACD"] > 0)
    
    # MOMENTUM CHECK: Looks for strong momentum
    momentum_ok = (row["RSI"] > 50) and (row["RSI"] < 80);
    
    # PRICE CHECK: Price confirmation, we make it more lenient by lowering the VWAP value if we need to
    price_above_vwap = row["Close"] > row["VWAP"]
    price_above_ema = row["Close"] > row["SMA_20"] and row["Close"] > row["SMA_40"]  # Ensures strength
    
    # Check if volume is increasing (confirmation of demand)
    increasing_volume = row["Volume"] > (self.data["Volume"].rolling(window=5).mean().iloc[-1] * 1.25);

    # If we see strong uptrend or a macd_crossover we can look to buy
    #if uptrend and macd_crossover and momentum_ok and price_above_vwap and price_above_ema and increasing_volume:
    #if (macd_crossover and momentum_ok and price_above_vwap) or (row["RSI"] > 60 and price_above_ema):
    if (
      (macd_crossover and row["RSI"] > 55 and price_above_vwap) or # MACD + Momentum + VWAP
      (momentum_ok and increasing_volume and price_above_ema) or # Strong Volume + EMA
      (row["RSI"] > 60 and row["Close"] > row["SMA_9"] and increasing_volume) # RSI + EMA 9 Bounce
    ):
      buy_signal = True;
    
    # Check if holding shares and create an exit condition.
    if self.shares > 0 and self.entry_price is not None:
  
      # Fixed Stop-loss (cuts losses)
      if (row["Close"] <= (self.entry_price - self.stop_loss_price)):
        return "SELL";
      
      # Trailing stop-loss initial value setup
      if self.trailing_stop_price is None:
        self.trailing_stop_price = self.entry_price - self.stop_loss_price;
        
      # Mark the highest marked price
      if self.highest_marked_priced is None:
        self.highest_marked_priced = self.entry_price;
        
      # If the price moves favorably, move the trailing stop price up but only on strong gains to prevent premature exits
      growth_percent = (row["Close"] / self.highest_marked_priced) - 1
      self.highest_marked_priced = max(self.highest_marked_priced, row["Close"]);
      
      # If the growth is at least 0.5% then adjust
      if (row["Close"] > self.entry_price) and (growth_percent >= 0.005):
          
        new_trailing_stop = row["Close"] - (row["Close"] * (self.minimum_percent_stop_loss/100));
        
        # Always try to increase the trailing stop price so we can get out
        self.trailing_stop_price = max(self.trailing_stop_price, new_trailing_stop);
        
      # If the price drops to our trailing_stop_price then we will sell and guarantee profits
      if row["Close"] <= self.trailing_stop_price:
        return "SELL";
    
    if buy_signal:
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
        self.trailing_stop_price = price - self.stop_loss_price;
        
        self.trade_log.append((action, price, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), purchased_shares))
        # print(f"Bought {purchased_shares} shares at ${price:.2f}, Cash Left: ${self.cash:.2f}")

    elif (action == "SELL" and self.shares > 0):
      sold_shares = self.shares;
      net_revenue = (sold_shares * price) - self.trading_tax;
      self.cash += net_revenue;
      self.shares = 0;
      
      self.entry_price = None;
      self.trailing_stop_price = None;
      
      self.trade_log.append((action, price, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sold_shares))
      # print(f"Sold {sold_shares} shares at ${price:.2f}, New Balance: ${self.cash:.2f}")

  def printTradeSummary(self):
    print("\nTrade Summary:")
    if not self.trade_log:
      print("No trades executed.")
      return

    df_trades = pd.DataFrame(self.trade_log)
    print(df_trades)
