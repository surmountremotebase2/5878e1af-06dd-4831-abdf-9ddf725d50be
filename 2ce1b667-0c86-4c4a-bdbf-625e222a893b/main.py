#Type code here
import pandas as pd
import numpy as np

class TradingStrategy:
    def __init__(self):
        self.lookback = 21
        self.ema_short_period = 8
        self.ema_long_period = 21
        self.rsi_period = 14
        self.atr_period = 14
        self.atr_multiplier = 1.5
        self.position_size = 1  # Adjust as needed
        self.stop_loss = None
        self.take_profit = None
    
    def initialize(self, context):
        context.asset = symbol('NQ')
        context.lookback = self.lookback
        
        schedule_function(self.check_signals, date_rules.every_day(), time_rules.market_open(hours=0, minutes=30))
        schedule_function(self.close_positions, date_rules.every_day(), time_rules.market_close(minutes=15))

    def check_signals(self, context, data):
        history = data.history(context.asset, ['close', 'high', 'low', 'volume'], context.lookback, '1m')
        
        # Calculate indicators
        close = history['close']
        high = history['high']
        low = history['low']
        volume = history['volume']
        
        ema_short = close.ewm(span=self.ema_short_period, adjust=False).mean()
        ema_long = close.ewm(span=self.ema_long_period, adjust=False).mean()
        rsi = self.compute_rsi(close, self.rsi_period)
        vwap = (close * volume).cumsum() / volume.cumsum()
        atr = self.compute_atr(high, low, close, self.atr_period)
        
        current_price = data.current(context.asset, 'price')
        
        # Generate signals
        long_entry = (ema_short[-1] > ema_long[-1] and​⬤