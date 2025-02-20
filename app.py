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
  PERIOD = "5d";
  INTERVAL = "1m"; 
  INITIAL_CASH = 10000; 
  TRADING_TAX = 0; # $ per transaction
  MINIMUM_PERCENT_STOP_LOSS = 1.6; # In %
  
  # Simulation run
  trading_bot = TradingBot(SYMBOL, PERIOD, INTERVAL, INITIAL_CASH, TRADING_TAX, MINIMUM_PERCENT_STOP_LOSS);
  simulator = TradingSimulator(trading_bot);
  simulator.runSimulation(0);
  # simulator.liveSimulation(1, simulator.logSimulationResults);
  simulator.logSimulationResults();

  """
  symbols = [
    # Greens
    "SOXL", "BOIL", "UCO", "SU", "NPI.TO", "DIS", "CYBN", "ERX",
    # Reds
    "BB", "AMC", "ENB", "BNS", "AC.TO",  "XIU.TO", "GME", "SOXS",
  ]

  profit_count = 0;
  neutral_count = 0;
  loss_count = 0;
  total_values = [];
  for symbol in symbols:
    trading_bot = TradingBot(symbol, PERIOD, INTERVAL, INITIAL_CASH, TRADING_TAX, MINIMUM_PERCENT_STOP_LOSS);
    if not hasattr(trading_bot, "data") or trading_bot.data.empty:
      continue  # Skip if no valid data

    simulator = TradingSimulator(trading_bot);
    total_value = simulator.runSimulation(0);
    simulator.logSimulationResults();
    if (total_value > INITIAL_CASH):
      profit_count += 1;
      total_values.append(total_value);
    elif (total_value == INITIAL_CASH):
      neutral_count += 1;
    elif (total_value < INITIAL_CASH):
      loss_count += 1;
      total_values.append(total_value);
      
  print(f"Profit Rate: {(profit_count/len(symbols))*100}%");
  print(f"Neutral Rate: {(neutral_count/len(symbols))*100}%");
  print(f"Loss Rate: {(loss_count/len(symbols))*100}%");
  
  changes = [(total_values[i] - total_values[i-1]) / INITIAL_CASH * 100 for i in range(1, len(total_values))]

  # Separate gains and losses
  profits = [c for c in changes if c > 0]
  losses = [-c for c in changes if c < 0]  # Convert losses to positive

  # Compute average gain and average loss
  average_gain = sum(profits) / len(profits) if profits else 0
  average_loss = sum(losses) / len(losses) if losses else 0

  print(f"Average Gain: {average_gain:.2f}%")
  print(f"Average Loss: {average_loss:.2f}%")
  """
if __name__ == "__main__":
  main();