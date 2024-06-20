#Type code here
import pandas as pd
import numpy as np

def initialize(context):
    context.asset = symbol('NQ')
    context.lookback = 21
    context.ema_short_period = 8
    context.ema_long_period = 21
    context.rsi_period = 14
    context.atr_period = 14
    context.atr_multiplier = 1.5
    context.position_size = 1  # Adjust as needed
    
    schedule_function(check_signals, date_rules.every_day(), time_rules.market_open(hours=0, minutes=30))
    schedule_function(close_positions, date_rules.every_day(), time_rules.market_close(minutes=15))

def check_signals(context, data):
    history = data.history(context.asset, ['close', 'high', 'low', 'volume'], context.lookback, '1m')
    
    # Calculate indicators
    close = history['close']
    high = history['high']
    low = history['low']
    volume = history['volume']
    
    ema_short = close.ewm(span=context.ema_short_period, adjust=False).mean()
    ema_long = close.ewm(span=context.ema_long_period, adjust=False).mean()
    rsi = compute_rsi(close, context.rsi_period)
    vwap = (close * volume).cumsum() / volume.cumsum()
    atr = compute_atr(high, low, close, context.atr_period)
    
    current_price = data.current(context.asset, 'price')
    
    # Generate​⬤