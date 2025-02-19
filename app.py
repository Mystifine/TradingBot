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
  INTERVAL = "5m"; 
  INITIAL_CASH = 10000; 
  TRADING_TAX = 0; # Per transaction
  
  # Simulation run
  #trading_bot = TradingBot(SYMBOL, PERIOD, INTERVAL, INITIAL_CASH, TRADING_TAX);
  #simulator = TradingSimulator(trading_bot);
  #simulator.runSimulation(0);
  #simulator.liveSimulation(1, simulator.logSimulationResults);
  #simulator.logSimulationResults();


  symbols = [
    # Greens
    "SOXL", "BOIL", "UCO", "SU", "NPI.TO", "DIS", "CYBN", "ERX",
    # Reds
    "BB", "AMC", "ENB", "BNS", "AC.TO",  "XIU.TO", "GME", "SOXS",
  ]

  profit_count = 0;
  neutral_count = 0;
  loss_count = 0;
  for symbol in symbols:
    trading_bot = TradingBot(symbol, PERIOD, INTERVAL, INITIAL_CASH, TRADING_TAX);
    if not hasattr(trading_bot, "data") or trading_bot.data.empty:
      continue  # Skip if no valid data

    simulator = TradingSimulator(trading_bot);
    total_value = simulator.runSimulation(0);
    simulator.logSimulationResults();
    if (total_value > INITIAL_CASH):
      profit_count += 1;
    elif (total_value == INITIAL_CASH):
      neutral_count += 1;
    elif (total_value < INITIAL_CASH):
      loss_count += 1;
  print(f"Profit Rate: {(profit_count/len(symbols))*100}%");
  print(f"Neutral Rate: {(neutral_count/len(symbols))*100}%");
  print(f"Loss Rate: {(loss_count/len(symbols))*100}%");

if __name__ == "__main__":
  main();