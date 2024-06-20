#Type code here
import pandas as pd
import numpy as np
import talib

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
    
    ema_short = talib.EMA(close, timeperiod=context.ema_short_period)
    ema_long = talib.EMA(close, timeperiod=context.ema_long_period)
    rsi = talib.RSI(close, timeperiod=context.rsi_period)
    vwap = (close * volume).cumsum() / volume.cumsum()
    atr = talib.ATR(high, low, close, timeperiod=context.atr_period)
    
    current_price = data.current(context.asset, 'price')
    
    # Generate signals
    long_entry = (ema_short[-1] > ema_long[-1] and 50 < rsi[-1] < 70 and current_price > vwap[-1])
    short_entry = (ema_short[-1] < ema_long[-1] and 30 < rsi[-1] < 50 and current_price < vwap[-1])
    
    # Check if we are in a position
    pos = context.portfolio.positions[context.asset].amount
    
    if long_entry and pos == 0:
        stop_price = current_price - context.atr_multiplier * atr[-1]
        take_profit_price = current_price + 2 * (current_price - stop_price)
        order_target_percent(context.asset, 1)
        context.stop_loss = stop_price
        context.take_profit = take_profit_price
        
    elif short_entry and pos == 0:
        stop_price = current_price + context.atr_multiplier * atr[-1]
        take_profit_price = current_price - 2 * (stop_price - current_price)
        order_target_percent(context.asset, -1)
        context.stop_loss = stop_price
        context.take_profit = take_profit_price

def close_positions(context, data):
    pos = context.portfolio.positions[context.asset].amount
    current_price = data.current(context.asset, 'price')
    
    if pos > 0 and (current_price <= context.stop_loss or current_price >= context.take_profit):
        order_target_percent(context.asset, 0)
    elif pos < 0 and (current_price >= context.stop_loss or current_price <= context.take_profit):
        order_target_percent(context.asset, 0)

def handle_data(context, data):
    # Can be used for live monitoring and dynamic adjustments
    pass

def analyze(context, perf):
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(2, 1, figsize=(12, 8))
    
    ax[0].plot(perf['portfolio_value'], label='Portfolio Value')
    ax[0].legend(loc='best')
    ax[0].set_ylabel('Portfolio Value')
    
    ax[1].plot(perf['gross_leverage'], label='Leverage')
    ax[1].legend(loc='best')
    ax[1].set_ylabel('Leverage')
    ax[1].set_xlabel('Time')
    
    plt.show()