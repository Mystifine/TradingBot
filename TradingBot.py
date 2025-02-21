import ta.momentum
import ta.volatility
import pandas as pd;
import numpy as np;
import ta;
import datetime;
import pytz;

from MarketAPI import MarketAPI;

class TradingBot:
  def __init__(self, symbol, period, interval, cash, trading_tax, api : MarketAPI):
    print(f"Initializing trading bot for {symbol}");
    self.symbol = symbol;
    self.period = period;
    self.interval = interval;
    self.api = api(symbol);
    
    self.trading_tax = trading_tax; # In $
    self.initial_cash = cash;
    self.cash = cash;
    self.shares = 0;

    self.trailing_stop_price = None;
    self.highest_marked_priced = None;
    self.entry_price = None;
    
    # Cache trading logs data
    self.trade_log = [];
    
    # Fetch data to use to analyze trends
    df = self.fetchData(period, interval);
    if df is None:
      return;
    print(f"Data fetched for over {period} at {interval} interval.");

    # Calculte Indicators on past data     
    self.data = self.calculateIndicators(df);
    print(f"Indicators calculated")

    # Calculate Volatility and create dynamic stop loss value
    self.stop_loss_price = self.calculateStopLossPrice();
    print(f"Risk parameters computed | Calculated Stop Loss: ${self.stop_loss_price:.2f}");
    
  def fetchData(self, period, interval):
    df = self.api.getHistoricalData(period=period, interval=interval);
    
    if df is None or df.empty:
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
    average_true_range = self.data["ATR"].rolling(window=10).mean().iloc[-1]
    
    # By default set the stop loss price to the average true range * 2
    atr_multiplier = 2;
    stop_loss_price = average_true_range * atr_multiplier;
    
    return stop_loss_price;

  def calculateIndicators(self, df):
    df = df.copy();
    
    # Moving average data of the last n data points
    df["SMA_9"] = df["Close"].rolling(window=9).mean();
    #df["SMA_20"] = df["Close"].rolling(window=20).mean();
    df["SMA_30"] = df["Close"].rolling(window=30).mean();
    #df["SMA_40"] = df["Close"].rolling(window=40).mean();
    df["SMA_50"] = df["Close"].rolling(window=50).mean();
    
    # Calculate VWAP (Weighted Average)
    df["Cumulative_TPV"] = (df["Close"] * df["Volume"]).groupby(df.index.date).cumsum()
    df["Cumulative_Volume"] = df["Volume"].groupby(df.index.date).cumsum()
    df["VWAP"] = df["Cumulative_TPV"] / df["Cumulative_Volume"]
    
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
    # Ignore the first 30 minutes and last 30 minutes in a trade
    market_time = row.name.tz_convert(pytz.timezone("US/Eastern"));
    market_hour = market_time.hour;
    market_minute = market_time.minute;
    
    # Do not engage in any activities in the first 30 minutes and last 30 minutes of the stock market
    if (market_hour == 9 and market_minute < 30) or (market_hour == 15 and market_minute >= 30):
      return "HOLD";
    
    # Force sell at the 25 minute mark to avoid random market spikes near the end and start of the day
    if self.shares > 0 and market_hour == 15 and market_minute == 25:
      return "SELL";
    
    buy_signal = False;
            
    # RSI above 50 is good indicator of uptrend / bullish
    rsi_strength = row["RSI"] > 53;
    # MACD Bullish cross
    macd_bullish = (row["MACD"] > 0) and row["MACD"] > row["MACD_Signal"] #row["MACD"] > row["MACD_Signal"] or (row["MACD"] > -0.01);
    # Price breaking above short term trend
    price_above_sma9 = row["Close"] > row["SMA_9"];
    # SMA Confirmation of bullish movement
    SMA_confirmation = row["SMA_9"] > row["SMA_30"];
    # Ensure average true range is increasing
    atr_increasing = row["ATR"] > self.data["ATR"].rolling(window=10).mean().iloc[-1] * 1.05;
    # Ensure price is above VWAP
    price_above_vwap = row["Close"] > row["VWAP"];
    
    # Strong trend indication, we want to play it safe
    if (rsi_strength and macd_bullish and price_above_sma9 and SMA_confirmation and atr_increasing and price_above_vwap):
      buy_signal = True;
    
    # Check if holding shares and create an exit condition.
    if self.shares > 0 and self.entry_price is not None:
  
      # Fixed Stop-loss (cuts losses) 
      # If the buy signal is strong we can hold because otherwise we would just make another purchase that adds to transaction costs
      if (row["Close"] < (self.entry_price - self.stop_loss_price) and not buy_signal):
        return "SELL";
      
      # Mark the highest marked price
      if self.highest_marked_priced is None:
        self.highest_marked_priced = self.entry_price;
      
      # Set up initial trailing stop price
      if self.trailing_stop_price is None:
        self.trailing_stop_price = self.entry_price - self.stop_loss_price;
      
      # If the price moves favorably, move the trailing stop price up but only on strong gains to prevent premature exits
      self.highest_marked_priced = max(self.highest_marked_priced, row["Close"]);
      
      new_trailing_stop = self.trailing_stop_price;
      if (row["Close"] > self.entry_price):
        
        gain_percent = ((row["Close"]/self.entry_price) - 1);
        
        # For every percent gain we get we will make the stop loss price tighter.
        # At 50% gains we will 100% cash out.
        guarantee_cash_out_threshold = 0.8;
        # If gain percent is 50 -> 50/50 = 1, 1-1 = 0. Set the multiplier to 0 so we will exit at current price
        # If gain percent is 25 -> 25/50 = 0.5, 1-0.5 = .5, set multiplier to .5 so if stop loss price was .1 it will shrink to .05 making it closer to the closing price
        # If gain percent is 1 -> 1/50 = 0.02, 1-0.02 = 0.98, set multiplier to 0.98 so we start choking out the trailing stop price
        stop_loss_price_multiplier = 1 - (gain_percent / guarantee_cash_out_threshold);
        #stop_loss_price_multiplier = 1 - (np.log1p(gain_percent) / np.log1p(guarantee_cash_out_threshold))

        # We want to secure profits, if there is high growth rate tighten the rope to secure profits
        new_trailing_stop = row["Close"] - (self.stop_loss_price * stop_loss_price_multiplier)
        self.trailing_stop_price = max(self.trailing_stop_price, new_trailing_stop);
        import numpy as np

      # If the price drops to our trailing_stop_price then we will sell and guarantee profits
      # If we would still buy then perhaps we should hold, buying would lead to increased transaction costs
      if row["Close"] < self.trailing_stop_price and not buy_signal:
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
      
      # Reset values
      self.entry_price = None;
      self.highest_marked_priced = None;
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
