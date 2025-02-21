from abc import abstractmethod;

class MarketAPI():
  def __init__(self, symbol):
    self.symbol = symbol;
    
  @abstractmethod
  def getStockPrice(self):
    pass;
  
  @abstractmethod
  def getHistoricalData(self, period, interval):
    pass;