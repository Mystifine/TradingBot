import pandas as pd;
import yfinance as yf;
import time;
import ta;
from TradingBot import TradingBot;

class TradingSimulator:
  def __init__(self, symbol, cash, trading_bot : TradingBot, stop_loss_percent, take_profit_percent):
    self.symbol = symbol;
    self.trading_bot = trading_bot;

    self.cash = cash;
    self.shares = 0;
    self.trading_tax = 10;

    self.stop_loss_percent = stop_loss_percent;
    self.take_profit_percent = take_profit_percent;
    self.entry_price = None;
    self.adjusted_entry_price = None;
    
    self.trade_log = [];
    
  def checkTradeSignal(self, row):
    if self.shares > 0 and self.adjusted_entry_price is not None:
      stop_loss_price = self.adjusted_entry_price * (1 - self.stop_loss_percent)
      take_profit_price = self.adjusted_entry_price * (1 + (self.take_profit_percent * 0.01))

      # Ensure after-tax revenue is still profitable
      if row["Close"] <= stop_loss_price:
        print(f"Stop-loss triggered at ${row['Close']:.2f} (Entry: ${self.entry_price:.2f})")
        return "SELL"

      #print(f"Consider selling: @{row["Close"]} | {take_profit_price}");
      if row["Close"] >= take_profit_price:
        after_tax_profit = (self.shares * row["Close"]) - self.trading_tax - (self.shares * self.adjusted_entry_price);
        if (after_tax_profit > 0):
          print(f"Take-profit triggered at ${row['Close']:.2f} (Entry: ${self.entry_price:.2f})")
          return "SELL"
    return self.trading_bot.checkTradeSignal(row);
  
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
        self.adjusted_entry_price = price + (self.trading_tax / purchased_shares);
        
        self.trade_log.append((action, price, total_cost, purchased_shares))
        print(f"Bought {purchased_shares} shares at ${price:.2f}, Cash Left: ${self.cash:.2f}")

    elif (action == "SELL" and self.shares > 0):
      sold_shares = self.shares;
      revenue = (sold_shares * price) - self.trading_tax;
      self.cash += revenue;
      self.shares = 0;
      
      self.entry_price = None;
      self.adjusted_entry_price = None;
      
      self.trade_log.append((action, price, revenue, sold_shares))
      print(f"Sold {sold_shares} shares at ${price:.2f}, New Balance: ${self.cash:.2f}")

  def printTradeSummary(self):
    print("\nTrade Summary:")
    if not self.trade_log:
      print("No trades executed.")
      return

    df_trades = pd.DataFrame(self.trade_log)
    print(df_trades)

  def runSimulation(self, speed=0.1):
    print("Starting Trading Simulator");
    last_row = None;
    for index, row in self.trading_bot.data.iterrows():

      action = self.checkTradeSignal(row);
      print(f"Action: {action} | Close: {row['Close']:.2f} | RSI: {row['RSI']:.2f} | SMA_9: {row['SMA_9']:.2f} | SMA_20: {row["SMA_20"]:.2f} | SMA_50: {row["SMA_50"]:.2f} | VWAP: {row["VWAP"]:.2f}")
      
      if action in ["BUY", "SELL"]:
        self.executeTrade(action, row["Close"]);
      last_row = row;
      time.sleep(speed);
    
    # Output all trades
    self.printTradeSummary();
    print(f"Simulation Complete | Cash Left: {self.cash} | Shares Left: {self.shares} | Total Value: {self.cash + self.shares * (last_row["Close"])}");

    total_value = self.cash + self.shares * (last_row["Close"]);
    return total_value;
        
    