from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, ATR
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # NQ futures ticker might vary based on the data provider's format.
        self.tickers = ["NQ"]
        self.trade_open = False
        
    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        # Choosing a smaller interval for day trading purposes.
        return "5min"
    
    @property
    def data(self):
        # No additional data required for this example.
        return []
    
    def run(self, data):
        # Initialize allocation with no position.
        allocation_dict = {"NQ": 0}
        
        # Get latest data for calculations.
        nq_data = data["ohlcv"][-1]["NQ"]  # Assuming last item is the most recent.
        
        # Check if the market data is sufficient.
        if len(data["ohlcv"]) < 15:  # We need at least 15 points to start our analysis.
            return TargetAllocation(allocation_dict)
        
        # Calculate indicators.
        ema_short = EMA("NQ", data["ohlcv"], length=5)[-1]
        ema_long = EMA("NQ", data["ohlcv"], length=10)[-1]
        rsi = RSI("NQ", data["ohlcv"], length=14)[-1]
        atr = ATR("NQ", data["ohlcv"], length=14)[-1]
        
        # Define strategy logic.
        # Entry Conditions
        if ema_short > ema_long and rsi < 70 and not self.trade_open:
            # Conditions to enter a long position.
            allocation_dict["NQ"] = 0.1  # Adjust size according to account risk capacity.
            self.trade_open = True
            log("Entering long position on NQ Futures")
            
        # Exit Conditions
        elif ema_short < ema_long or rsi > 70 and self.trade_open:
            # Conditions to exit position.
            allocation_dict["NQ"] = 0  # Closing the position.
            self.trade_open = False
            log("Exiting position on NQ Futures")
            
        # Adjust based on ATR if needed for stop loss or position size adjustment.
        
        return TargetAssignment(allocation_dict)

# Note: Ensure you have real-time data and the capability to handle frequent transactions for day trading.
# Always test the strategy in a simulation environment before going live.