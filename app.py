import os;
from dotenv import load_dotenv;
from YahooFinanceAPI import YahooFinanceAPI;
from TradingBot import TradingBot;
from TradingSimulator import TradingSimulator;
import matplotlib.pyplot as plt;
import pandas as pd;

def main():
  # Load environment variables
  load_dotenv();
  
  SYMBOL = "SPY";
  PERIOD = "1d"; # one week average is decent test size for 5m interval, 1d pairs better with 1m
  INTERVAL = "1m"; # 5 minutes is good if combined with 1week+, If day trading with 1d then 1m pairs better
  INITIAL_CASH = 10000; # 10k is realistic 
  
  # 8-11% is pretty decent however if market isn't doing well the lower the safer and better generally
  PROFIT_TAKER_PERCENT = 9; #range(1, 21, 1);
  # Lower stop loss percent will reduce losses but it also removes oppurtunity for profit
  STOP_LOSS_PERCENT = 7;
  """
  soxl_yf_api = YahooFinanceAPI(SYMBOL);
  trading_bot = TradingBot(SYMBOL, PERIOD, INTERVAL);
  simulator = TradingSimulator(SYMBOL, INITIAL_CASH, trading_bot, STOP_LOSS_PERCENT, PROFIT_TAKER_PERCENT);
  simulator.runSimulation(0);
  """
  symbols = [
    "TSLA", "NVDA", "AMD", "AAPL", "GOOG", "META", "AMZN", "MSFT", "NFLX", "BA",
    "COIN", "PLTR", "GME", "NIO", "XPEV", "LI", "BABA", "PDD", "TME",
    "SOFI", "ROKU", "SPCE", "RIVN", "LCID", "FSLY", "SNOW", "CRWD", "ZM",
    "UPST", "AFRM", "ARKK", "BIDU", "JD", "SHOP", "DKNG", "CVNA", "MSTR",
    "RIOT", "MARA", "HUT", "WKHS", "NKLA", "QS", "FUBO", "BLNK", "RUN",
    "SOXL", "BOIL", "SPY", "GUSH", "ERX", "DIG", "EUO", "UTSL", "VOO", "QQQ"
  ]

  profit_count = 0;
  for symbol in symbols:
      trading_bot = TradingBot(symbol, PERIOD, INTERVAL);
      if not hasattr(trading_bot, "data") or trading_bot.data.empty:
        continue  # Skip if no valid data

      simulator = TradingSimulator(symbol, INITIAL_CASH, trading_bot, STOP_LOSS_PERCENT, PROFIT_TAKER_PERCENT);
      total_value = simulator.runSimulation(0);
      if (total_value >= INITIAL_CASH):
        profit_count += 1;
  print(f"Profit Rate: {(profit_count/len(symbols))*100}%")
  
  """
  # Testing for best profit taker value
  symbols = ["BOIL", "SOXL", "ERX", "GUSH", "SPY", "EUO", "UTSL", "DIG", "QQQ", "VOO", "UCO", "AAPL", "GOOG", "META", "X"]
  # symbols = ["BOIL"];
  results = [];
  for symbol in symbols:
    for i in PROFIT_TAKER_PERCENT_RANGE:
        trading_bot = TradingBot(symbol, PERIOD, INTERVAL);
        if not hasattr(trading_bot, "data") or trading_bot.data.empty:
          continue  # Skip if no valid data

        simulator = TradingSimulator(symbol, INITIAL_CASH, trading_bot, STOP_LOSS_PERCENT, i);
        total_value = simulator.runSimulation(0);
        
        # Calculate percentage difference from initial cash
        percent_diff = ((total_value - INITIAL_CASH) / INITIAL_CASH) * 100

        results.append({
          "Symbol": symbol,
          "ProfitTaker%": i,
          "FinalValue": total_value,
          #"%Diff": percent_diff
        })
        
  # Convert results to a DataFrame
  df_results = pd.DataFrame(results);
  df_results.to_csv("profit_taker_test_results.csv",index=False);

  # Compute the average final value for each profit-taker percentage
  df_avg = df_results.groupby("ProfitTaker%")["FinalValue"].mean().reset_index();
  
  # Plot results
  plt.figure(figsize=(12, 6))
  plt.plot(df_avg["ProfitTaker%"], df_avg["FinalValue"], marker='o', linestyle='-', label="Avg Final Value ($)")
  #plt.plot(df_avg["ProfitTaker%"], df_avg["%Diff"], marker='s', linestyle='--', label="Avg % Diff")
  plt.xlabel("Profit Taker Percentage")
  plt.ylabel("Value")
  plt.title("Average Final Value vs Profit Taker Percentage")
  plt.legend()
  plt.grid(True)
  plt.show()
  """
if __name__ == "__main__":
  main();