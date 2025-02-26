import matplotlib.pylab as plt;
import matplotlib.dates as mdates;
import pandas as pd;

class StockGraphingAPI():
  def __init__(self, symbol, period, interval, df):
    self.symbol = symbol;
    self.period = period;
    self.interval = interval;
    self.df = df;
    pass;
  
  def plotGraph(self):
    
    if self.df is None:
      print("No data to plot");
    
    fig, (ax1, ax2) = plt.subplots(2, figsize=(12,10), sharex=True, gridspec_kw={"height_ratios":[2,1]});
    
    # Increase interval for x axis
    ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=10));
    
    # Format the date
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    # Plot the price on the first sub plot
    ax1.plot(self.df.index, self.df["Close"], label="Closing Price", color="blue");
    
    # Display buy and sell signals
    if "Action" in self.df.columns:
      # Extract signals data
      buy_signals = self.df[self.df["Action"] == "BUY"];
      sell_signals = self.df[self.df["Action"] == "SELL"];
      hold_signals = self.df[self.df["Action"] == "HOLD"];
      
      # Plot buy signals
      ax1.scatter(buy_signals.index, buy_signals["Close"], marker="^", color='green', label="Buy Signal", s=40);
      
      # Plot sell signals
      ax1.scatter(sell_signals.index, sell_signals["Close"], marker="v", color='red', label="Sell Signal", s=40);

    if "SMA_9" in self.df.columns:
      # SMA_9 price range is similar to original price range so we can directly edit ax1
      ax1.plot(self.df.index, self.df["SMA_9"], label="SMA_9", color="purple");
      
    if "MACD" in self.df.columns and "MACD_Signal" in self.df.columns:
      ax2.plot(self.df.index, self.df["MACD"], label="MACD", color="blue")
      ax2.plot(self.df.index, self.df["MACD_Signal"], label="MACD Signal", color="red", linestyle="dashed")
      ax2.axhline(0, color="gray", linestyle="dotted", alpha=0.5)  # Zero line for MACD reference
      ax2.set_ylabel("MACD Value")
      ax2.set_title("MACD & MACD Signal")
      ax2.legend()
      ax2.grid()
      
    # Let's display information such as RSI and SMA_9
    if "RSI" in self.df.columns:
      ax3 = ax1.twinx();
      ax3.set_ylabel("RSI (0-100)", color = "orange");
      ax3.plot(self.df.index, self.df["RSI"], label="Relative Strength Index (RSI)", color = "orange");
      ax3.axhline(70, color="gray", linestyle="dotted", alpha=0.5)  # Overbought line
      ax3.axhline(30, color="gray", linestyle="dotted", alpha=0.5)  # Oversold line
      ax3.set_ylim([0, 100])  # RSI is always between 0 and 100
      ax3.tick_params(axis="y", labelcolor="orange")
    
    ax1.set_xlabel("Date");
    ax1.set_ylabel("Price");
    
    # Create space for title and bottom
    fig.subplots_adjust(top=0.92, bottom=0.15)

    # Rotate x-axis labels properly
    for label in ax2.get_xticklabels():
      label.set_rotation(90)    
    plt.title(f"{self.symbol} Stock Closing Price");
    plt.legend();
    plt.grid();
    plt.show();