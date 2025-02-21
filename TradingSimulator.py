import pandas as pd;
import yfinance as yf;
import time;
import os;
import datetime;
from TradingBot import TradingBot;

class TradingSimulator:
  def __init__(self, trading_bot : TradingBot):
    # Trading bot to handle decision making
    self.trading_bot = trading_bot;
    self.total_value = None;

  def liveSimulation(self, speed, onFinish):
    print(f"Starting real-time simulation for {self.trading_bot.symbol}...");
    
    self.simulation_mode = "LIVE";
    
    latest_row = None;
    while True:
      try:
        latest_data = self.trading_bot.yahoo_finance_api.getHistoricalData(period="1d", interval="1m");
        if latest_data is None or latest_data.empty:
          print("Error fetching live data. Retrying...")
          time.sleep(5)
          continue  # Skip iteration and retry
      
        latest_row = latest_data.iloc[-1];
        
        new_entry = pd.DataFrame([latest_row]);
        self.trading_bot.data = pd.concat([self.trading_bot.data, new_entry]).tail(200);
        self.trading_bot.data = self.trading_bot.updateLastRowIndicator(self.trading_bot.data);
        latest_row = self.trading_bot.data.iloc[-1];
        
        action = self.trading_bot.checkTradeSignal(latest_row);
        if action in ["BUY", "SELL"]:
          self.trading_bot.executeTrade(action, latest_row["Close"]);
          
        # Print real-time update
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Action: {action} | Price: ${latest_row['Close']:.2f}")
      
        # Wait before next iteration (simulating real-time)
        time.sleep(speed)
      except KeyboardInterrupt:
        onFinish();
        break;
      finally:
        self.total_value = self.trading_bot.cash + self.trading_bot.shares * (latest_row["Close"]);

  def runSimulation(self, speed=0.1):
    # print("Starting Trading Simulator");
    last_row = None;
    
    self.simulation_mode = "HISTORY";
    
    for index, row in self.trading_bot.data.iterrows():
      action = self.trading_bot.checkTradeSignal(row);
      # print(f"Action: {action} | Close: {row['Close']:.2f} | RSI: {row['RSI']:.2f} | SMA_9: {row['SMA_9']:.2f} | SMA_20: {row["SMA_20"]:.2f} | SMA_50: {row["SMA_50"]:.2f} | VWAP: {row["VWAP"]:.2f}")
      
      if action in ["BUY", "SELL"]:
        self.trading_bot.executeTrade(action, row["Close"]);
      last_row = row;
      time.sleep(speed);
    
    # Output all trades
    # self.printTradeSummary();
    self.total_value = self.trading_bot.cash + self.trading_bot.shares * (last_row["Close"]);
    print(f"Simulation Complete {self.trading_bot.symbol} | Cash Left: {self.trading_bot.cash:.2f} | Shares Left: {self.trading_bot.shares:.2f} | Total Value: {self.total_value:.2f}");

    return self.total_value;
        
  def logSimulationResults(self):
    if self.total_value is None:
      print("Simulation has not been ran yet");
      return;
  
    # Define filename format (e.g., "SPY_10000_1d_1m.txt")
    filename = f"{self.trading_bot.initial_cash}_{self.trading_bot.trading_tax}_{self.trading_bot.period}_{self.trading_bot.interval}.txt"
    log_dir = f"simulation_data/{self.trading_bot.symbol}/{self.simulation_mode}"  # Store logs in a dedicated folder
    os.makedirs(log_dir, exist_ok=True)  # Create folder if not exists

    filepath = os.path.join(log_dir, filename)

    # Format trade log to be readable
    formatted_log = "";
    formatted_log += "{:<20} {:<5} {:<10} {:<12} {:<10}\n".format("Time", "No.", "Action", "Price", "Shares")
    for i, trade in enumerate(self.trading_bot.trade_log, start=1):
      action, price, order_time, shares = trade
      formatted_log += "    {:<20} {:<5} {:<10} ${:<12.2f} {:<10}\n".format(order_time, i, action, price, int(shares))
      
    # Prepare data to save
    log_data = f"""\
    === Trading Simulation Log ===
    Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Symbol: {self.trading_bot.symbol}
    Period: {self.trading_bot.period}
    Interval: {self.trading_bot.interval}
    Tax: ${self.trading_bot.trading_tax:.2f}
    Initial Cash: ${self.trading_bot.initial_cash:.2f}
    Final Value: ${self.total_value:.2f}
    Profit/Loss: ${self.total_value - self.trading_bot.initial_cash:.2f} ({((self.total_value - self.trading_bot.initial_cash) / self.trading_bot.initial_cash) * 100:.2f}%)
    Stop Loss Price: {self.trading_bot.stop_loss_price:.2f}
    Total Trades: {len(self.trading_bot.trade_log)}
    Trade History:
    {formatted_log}
    ==============================
"""

    # Save to file
    with open(filepath, "w") as file:
      file.write(log_data)

    print(f"Simulation results saved to {filepath}")