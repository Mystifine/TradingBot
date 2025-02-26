import os;
import requests;
import pandas as pd;
import yfinance as yf;
import time;
import matplotlib.pyplot as plt;

from dotenv import load_dotenv;
from MarketAPIs.YahooFinanceAPI import YahooFinanceAPI;
from MarketAPIs.FinnhubAPI import FinnhubAPI;
from MarketAPIs.IBKRAPI import IBKRAPI;
from TradingBot import TradingBot;
from TradingSimulator import TradingSimulator;
from StockGraphingAPI import StockGraphingAPI;

def simulateTest(symbol, period, interval, initial_cash, trading_tax, api):
  trading_bot = TradingBot(symbol, period, interval, initial_cash, trading_tax, api);
  simulator = TradingSimulator(trading_bot);
  simulator.runSimulation(0);
  simulator.logSimulationResults();

  #simulator.liveSimulation(1, simulator.logSimulationResults);
  
  return trading_bot;

def graphStockMarket(symbol, period, interval, df):
  stock_grapher = StockGraphingAPI(symbol, period, interval, df);
  stock_grapher.plotGraph();
  
def main():
  # Load environment variables
  load_dotenv();
  
  SYMBOL = "BABA";
  PERIOD = "1d";
  INTERVAL = "1m"; 
  INITIAL_CASH = 10000; 
  TRADING_TAX = 10; # $ per transaction
  
  # Simulation run
  trading_bot = simulateTest(SYMBOL, PERIOD, INTERVAL, INITIAL_CASH, TRADING_TAX, YahooFinanceAPI)
  
  # Graphing data
  graphStockMarket(SYMBOL, PERIOD, INTERVAL, trading_bot.data);
  
  """
  # Fetch the list of S&P 500 companies
  symbols = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "BRK.B", "JNJ", "XOM", "NVDA", "META",
    "UNH", "TSLA", "JPM", "V", "PG", "MA", "HD", "CVX", "MRK", "PEP",
    "KO", "LLY", "ABBV", "AVGO", "COST", "MCD", "WMT", "BAC", "PFE", "SPY",
    "TMO", "DIS", "CSCO", "VZ", "ADBE", "CMCSA", "NFLX", "ABT", "ACN", "DHR",
    "NKE", "NEE", "WFC", "INTC", "TXN", "LIN", "MDT", "HON", "UNP", "PM",
    "BMY", "QCOM", "LOW", "RTX", "MS", "INTU", "ORCL", "AMD", "AMGN", "CVS",
    "GS", "SCHW", "BLK", "IBM", "AMT", "ISRG", "PLD", "MDLZ", "BA", "BKNG",
    "CAT", "DE", "AXP", "GE", "NOW", "T", "LMT", "SYK", "SPGI", "MO",
    "ELV", "C", "ADI", "MU", "MMM", "ZTS", "USB", "GILD", "ADP", "CB",
    "PYPL", "COP", "TGT", "BDX", "CCI", "DUK", "SO", "MMC", "PNC", "APD",
    "CL", "TJX", "HUM", "CME", "MRNA", "UPS", "SLB", "FISV", "EW", "PGR",
    "ITW", "SHW", "EOG", "HCA", "CSX", "NSC", "ETN", "EMR", "FDX", "D",
    "WM", "NOC", "MCO", "KMB", "F", "ILMN", "REGN", "AON", "BSX", "DG",
    "KLAC", "MPC", "VRTX", "APTV", "ADM", "AEP", "COF", "MCK", "PSA", "AIG",
    "LRCX", "BK", "ORLY", "TRV", "CNC", "PRU", "MAR", "SBUX", "ECL", "CTAS",
    "IDXX", "PH", "TEL", "MNST", "AFL", "ALL", "OTIS", "WBA", "KHC", "AZO",
    "WELL", "CTSH", "RSG", "DOW", "BIIB", "SRE", "SPG", "STZ", "HLT", "PSX",
    "MET", "ROST", "HPQ", "VLO", "MSI", "OXY", "DLR", "PPG", "TFC", "ED",
    "YUM", "WMB", "BAX", "MCHP", "PCAR", "BKR", "ENPH", "JCI", "FCX", "NEM",
    "ES", "WEC", "ROK", "GPN", "XEL", "ANET", "KMI", "IFF", "EQR", "GLW",
    "STT", "MTD", "KEYS", "AJG", "VRSK", "CDNS", "AME", "FTNT", "HES", "MSCI",
    "CBRE", "EXC", "PSA", "VICI", "WST", "FIS", "CARR", "LHX", "CTVA", "KR",
    "DLTR", "NUE", "DHI", "WAT", "ZBH", "PAYX", "ODFL", "CMG", "TT", "AMP",
    "FAST", "SYY", "VTRS", "MLM", "A", "RMD", "GWW", "MTB", "LEN", "VMC",
    "TSN", "SWK", "DTE", "ETR", "HIG", "ALB", "EFX", "RJF", "FRC", "LUV",
    "NTRS", "CINF", "MKC", "HSY", "PPL", "CMS", "AEE", "ATO", "DOV", "XYL",
    "CAG", "HPE", "K", "SJM", "NWL", "NWSA", "NWS", "MOS", "IPG", "OMC",
    "WHR", "HAS", "LEG", "BWA", "SEE", "NLSN", "HII", "ALK", "L", "RE",
    "BEN", "IVZ", "AIZ", "LNC", "UNM", "PBCT", "FRT", "REG", "SLG", "VNO",
    "WY", "PFG", "LUMN", "HP", "NLOK", "JNPR", "FFIV", "XRX", "DXC", "HST",
    "PKG", "WRK", "IP", "NUE", "STLD", "RS", "ATI", "AA", "CENX", "X",
    "CLF", "AKS", "MT", "NEM", "GOLD", "AEM", "AU", "KGC", "BVN", "IAG",
    "NGD", "EGO", "AUY", "AGI", "PAAS", "HL", "CDE", "SSRM", "WPM", "SAND",
    "FNV", "RGLD", "OR", "NEM", "GOLD", "AEM", "AU", "KGC", "BVN", "IAG",
    "NGD", "EGO", "AUY", "AGI", "PAAS", "HL", "CDE", "SSRM", "WPM", "SAND",
    "FNV", "RGLD", "OR", "NEM", "GOLD", "AEM", "AU", "KGC", "BVN", "IAG",
    "NGD", "EGO", "AUY", "AGI", "PAAS", "HL", "CDE", "SSRM", "WPM", "SAND",
    "FNV", "RGLD", "OR", "NEM", "GOLD", "AEM", "AU", "KGC", "BVN", "IAG",
    "NGD",
  ]
   
  #symbols = ["BABA", "BAX", "MELI", "LRCX", "SMCI"];

  profit_count = 0;
  neutral_count = 0;
  loss_count = 0;
  total_gains = [];
  gain_symbols = [];
  total_losses = [];
  loss_symbols = [];
  for symbol in symbols:
    trading_bot = TradingBot(symbol, PERIOD, INTERVAL, INITIAL_CASH, TRADING_TAX);
    if trading_bot is None or not hasattr(trading_bot, "data") or trading_bot.data.empty:
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
    time.sleep(.25); # API Request limit or we might get banned
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
  total_stocks = profit_count + neutral_count + loss_count;
  print(f"Interval: {INTERVAL}");
  print(f"Period: {PERIOD}");
  print(f"Profit Rate: {(profit_count/ (total_stocks) )*100:.2f}%");
  print(f"Neutral Rate (No Orders): {(neutral_count/total_stocks)*100:.2f}%");
  print(f"Loss Rate: {(loss_count/total_stocks)*100:.2f}%");
  print(f"Total Stocks: {total_stocks}");
  print(f"Trading Tax: ${TRADING_TAX}");
  print(f"Average Gain: {average_gain:.2f}%")
  print(f"Average Loss: {average_loss:.2f}%")
  """
  
if __name__ == "__main__":
  main();