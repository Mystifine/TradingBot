# TradingBot
This is a day trading bot designed with day trading parameters. Could be used for other forms of trading but it is not recommended as tests cases and simulations were done for day trading. This application focuses on buying and selling shares only.

Ideal Day Trading Parameters:
- 5m Interval allows for better ATR measurements. 1m interval introduces too much noise and triggers too many trades, fees will eat your balance alive.
- 1d Allows for recent data trends especially good for day trading since past data isn't as relevant. We are looking to read live trends.

## Features
- Dynamic stop loss based on ATR (Average True Range).
- Minimum % Stop loss on highest price (Trailing stop loss).
- Trailing stop loss allows for strong trends to keep running.
- Uptrend detection using SMA_N (Moving average over last n data points)
- MACD cross over check for bullish market and lenient entry (used in combination of Uptrend detection)
- Market momentum check using RSI (Relative Strength Index)
- VWAP indicator 