# TradingBot
This is a bot designed to day trade especially in volatile environments. 

# Best Parameters:
- 1m interval allows for best quick adaptive analysis in volatile environments.
- 8d period allows you to simulate trading over 8d of historic data. When actively trading you technically only need maybe 1-2 days. 
- 1% minimum losses cut is ideal for day trading, for long term trading you could increase it.

# Algorithm
1. Enter market safetly when trends suggest bullish movement and growth
2. If price drops to a threshold sell to cut losses
3. If price grows have a trailing stop loss price to allow infinite growth on strong trends (You've struck gold)

## Features
- Dynamic adaptive trailing losses combined with minimum % stop loss to maximize revenue and cut losses.
- Uptrend detection using SMA_N (Moving average over last n data points)
- MACD cross over check for bullish market and lenient entry (used in combination of Uptrend detection)
- Market momentum check using RSI (Relative Strength Index)
- VWAP indicator 