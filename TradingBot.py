import ta.momentum
import ta.volatility
from YahooFinanceAPI import YahooFinanceAPI;
import pandas as pd;
import numpy as np;
import ta;

class TradingBot:
  def __init__(self, symbol, period, interval, cash, trading_tax, minimum_percent_stop_loss):
    print(f"Initializing trading bot for {symbol}");
    self.symbol = symbol;
    self.period = period;
    self.interval = interval;
    self.yahoo_finance_api = YahooFinanceAPI(symbol);
    self.initial_cash = cash;
    self.cash = cash;
    self.shares = 0;
    self.minimum_percent_stop_loss = minimum_percent_stop_loss;
    self.entry_price = None;
    self.trailing_stop_price = None;
    self.trading_tax = trading_tax; # In $
    
    # Cache trading logs data
    self.trade_log = [];
    
    # Fetch data to use to analyze trends
    df = self.fetchData(period, interval);
    print(f"Data fetched for over {period} at {interval} interval.");

    # Calculte Indicators on past data     
    self.data = self.calculateIndicators(df);
    print(f"Indicators calculated")

    # Calculate Volatility and create dynamic stop loss value
    self.stop_loss_price = self.calculateDynamicStopLossPrice();
    print(f"Dynamic risk parameters calculated | Stop Loss: ${self.stop_loss_price:.2f}");
    
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
  
  def calculateDynamicStopLossPrice(self):
    # Get the latest ATR value
    atr_value = self.data["ATR"].iloc[-1];

    base_stop_loss_multiplier = None;
    
    """
    if (atr_value > self.data["ATR"].mean()):
      # High Volatility, Give more space for growth
      base_stop_loss_multiplier = 2.5;
    else:
      # Low Volatility, Tighter space to cut losses
      base_stop_loss_multiplier = 2.0;
    """
    
    # Scaling based off RSI
    if self.data["RSI"].iloc[-1] > 65:
      base_stop_loss_multiplier = 2.8  # Looser stop for strong trends
    elif self.data["RSI"].iloc[-1] < 50:
        base_stop_loss_multiplier = 1.8  # Tighter stop for weaker trends
    else:
        base_stop_loss_multiplier = 2.5

      
    # Calculate actual stop loss and profit take prices
    # raw_stop_loss_price = atr_value * base_stop_loss_multiplier;
    raw_stop_loss_price = max(atr_value * base_stop_loss_multiplier, self.data["Close"].iloc[-1] * (self.minimum_percent_stop_loss/100))  # Ensure at least 1.5% stop-loss

    # Include tax consideration, trading tax is multiplied by 2 because buy and sell usually applies the trading tax
    adjusted_stop_loss_price = raw_stop_loss_price + ((self.trading_tax * 2) / self.data["Close"].iloc[-1]);
    
    return adjusted_stop_loss_price;

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
  
      # Fixed Stop-loss (Cuts losses)
      if row["Close"] <= (self.entry_price - self.stop_loss_price):
        return "SELL";
      
      # Trailing stop-loss initial value setup
      if self.trailing_stop_price is None:
        self.trailing_stop_price = self.entry_price - self.stop_loss_price;
        
      # If the price moves favorably, move the trailing stop price up but only on strong gains to prevent premature exits
      if row["Close"] > self.entry_price + (self.data["ATR"].iloc[-1] * 1.25):
        # Dynamically update trailing stop-loss value. Consider the volatility / volume
        atr_multiplier = 3;
        if row["RSI"] > 70:
            atr_multiplier = 3.5  # Let strong trends run longer
        elif row["RSI"] < 50:
            atr_multiplier = 2.2  # Cut weaker trends faster
        else:
            atr_multiplier = 3.0
          
        # Increase the trailing to be always a % under the highest price minimum.
        new_trailing_stop = row["Close"] - max(self.data["ATR"].iloc[-1] * atr_multiplier, row["Close"] * (self.minimum_percent_stop_loss/100));
        
        # Always try to increase the trailing stop price so we can get out
        self.trailing_stop_price = max(self.trailing_stop_price,new_trailing_stop);
        
      # If the price drops to our trailing_stop_price then we will sell and guarantee profits
      if row["Close"] <= self.trailing_stop_price:
        return "SELL";
    
    # STRONG UPTREND CHECK: This is a strict uptrend checker that signals immediate buy
    uptrend = (row["SMA_9"] > row["SMA_20"]) and (row["SMA_20"] > row["SMA_40"]);
    
    # LENIENT MACD CROSSOVER CHECK: Allows for earlier trend detection and earlier entry
    macd_crossover = (row["MACD"] > row["MACD_Signal"]) and (row["MACD"] > 0); # Bullish cross over
    
    # MOMENTUM CHECK: Looks for momentum in the trend
    momentum_ok = (row["RSI"] > 50) and (row["RSI"] < 80);
    
    # PRICE CHECK: Price confirmation, we make it more lenient by lowering the VWAP value if we need to
    price_above_vwap = row["Close"] > (row["VWAP"]);
    
    # Check if volume is increasing (confirmation of trend)
    increasing_volume = row["Volume"] > self.data["Volume"].rolling(window=5).mean().iloc[-1] * 1.2;

    # If we see strong uptrend or a macd_crossover we can look to buy
    if (uptrend or macd_crossover) and momentum_ok and price_above_vwap and increasing_volume:
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
        
        self.trade_log.append((action, price, total_cost, purchased_shares))
        # print(f"Bought {purchased_shares} shares at ${price:.2f}, Cash Left: ${self.cash:.2f}")

    elif (action == "SELL" and self.shares > 0):
      sold_shares = self.shares;
      net_revenue = (sold_shares * price) - self.trading_tax;
      self.cash += net_revenue;
      self.shares = 0;
      
      self.entry_price = None;
      self.trailing_stop_price = None;
      
      self.trade_log.append((action, price, net_revenue, sold_shares))
      # print(f"Sold {sold_shares} shares at ${price:.2f}, New Balance: ${self.cash:.2f}")

  def printTradeSummary(self):
    print("\nTrade Summary:")
    if not self.trade_log:
      print("No trades executed.")
      return

    df_trades = pd.DataFrame(self.trade_log)
    print(df_trades)
