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
  
  SYMBOL = "SOXL";
  PERIOD = "1d";
  INTERVAL = "1m"; 
  INITIAL_CASH = 10000; 
  TRADING_TAX = 10; # $ per transaction
  MINIMUM_PERCENT_STOP_LOSS = 1; # In %
  
  # Simulation run
  trading_bot = TradingBot(SYMBOL, PERIOD, INTERVAL, INITIAL_CASH, TRADING_TAX, MINIMUM_PERCENT_STOP_LOSS);
  simulator = TradingSimulator(trading_bot);
  #simulator.runSimulation(0);
  simulator.liveSimulation(1, simulator.logSimulationResults);
  #simulator.logSimulationResults();
  
  """
  symbols = [
    # Greens
    "SOXL", "BOIL", "UCO", "SU", "NPI.TO", "DIS", "CYBN", "ERX",
    # Reds
    "BB", "AMC", "ENB", "BNS", "AC.TO", "XIU.TO", "GME", "SOXS",
    # other
    "YINN", "NVDA", "NVD", "GOOG", "SAVA", "CHAU", "SMCI", "ASML", "FFIE", "AAPL", "AMD", "TSM", "INTC", "XPEV", "LI", "NIO", "TSLA", "SQQQ", "BABA", "RBLX", "META", "GOOS",
    # Big losses
    # "CNSP", "NKLA", "HCTI", "PWM", "BMBL", "ZCAR", "SOPA", "TWG", "POAI", "APTO", "KWE"
  ]

  profit_count = 0;
  neutral_count = 0;
  loss_count = 0;
  total_gains = [];
  gain_symbols = [];
  total_losses = [];
  loss_symbols = [];
  for symbol in symbols:
    trading_bot = TradingBot(symbol, PERIOD, INTERVAL, INITIAL_CASH, TRADING_TAX, MINIMUM_PERCENT_STOP_LOSS);
    if not hasattr(trading_bot, "data") or trading_bot.data.empty:
      continue  # Skip if no valid data

    simulator = TradingSimulator(trading_bot);
    total_value = simulator.runSimulation(0);
    simulator.logSimulationResults();
    
    percent_change = ((total_value - INITIAL_CASH) / INITIAL_CASH) * 100;
    if (total_value > INITIAL_CASH):
      profit_count += 1;
      gain_symbols.append(symbol);
      total_gains.append( percent_change );
    elif (total_value == INITIAL_CASH):
      neutral_count += 1;
    elif (total_value < INITIAL_CASH):
      loss_count += 1;
      loss_symbols.append(symbol);
      total_losses.append( abs(percent_change) )

  #print("All Percent Gains:", total_gains)
  #print("Gain Symbols:", gain_symbols);
  #print("All Percent Losses:", total_losses)
  #print("Loss Symbols:", loss_symbols);

  # Calculate average gain
  average_gain = 0;
  if (len(total_gains) == 0):
    average_gain = 0;
  else:
    average_gain = (sum(total_gains) / (len(total_gains)));
  
  average_loss = 0;
  if (len(total_losses) == 0):
    average_loss = 0;
  else:
    average_loss = (sum(total_losses) / (len(total_losses)));
  
  # Output Data
  print(f"Interval: {INTERVAL}");
  print(f"Period: {PERIOD}");
  print(f"Profit Rate: {(profit_count/len(symbols))*100:.2f}%");
  print(f"Neutral Rate (No Orders): {(neutral_count/len(symbols))*100:.2f}%");
  print(f"Loss Rate: {(loss_count/len(symbols))*100:.2f}%");
  print(f"Total Stocks: {len(symbols)}");
  print(f"Trading Tax: ${TRADING_TAX}");
  print(f"Average Gain: {average_gain:.2f}%")
  print(f"Average Loss: {average_loss:.2f}%")
  """
  
if __name__ == "__main__":
  main();