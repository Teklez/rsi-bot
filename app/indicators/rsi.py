from typing import List
import numpy as np

def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
    """
    Calculate Relative Strength Index (RSI)
    
    Args:
        prices: List of closing prices
        period: RSI period (default 14)
    
    Returns:
        List of RSI values
    """
    if len(prices) < period + 1:
        return []
    
    prices = np.array(prices)
    deltas = np.diff(prices)
    
    # Separate gains and losses
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Calculate initial average gain and loss
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    rsi_values = []
    
    for i in range(period, len(prices)):
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        rsi_values.append(rsi)
        
        # Update averages using Wilder's smoothing
        if i < len(prices) - 1:
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    return rsi_values

def is_oversold(rsi: float, threshold: float = 30) -> bool:
    """Check if RSI indicates oversold condition"""
    return rsi < threshold

def is_overbought(rsi: float, threshold: float = 70) -> bool:
    """Check if RSI indicates overbought condition"""
    return rsi > threshold

def get_rsi_signal(rsi: float, oversold_threshold: float = 30, overbought_threshold: float = 70) -> str:
    """
    Get trading signal based on RSI
    
    Returns:
        'buy' for oversold, 'sell' for overbought, 'hold' for neutral
    """
    if is_oversold(rsi, oversold_threshold):
        return 'buy'
    elif is_overbought(rsi, overbought_threshold):
        return 'sell'
    else:
        return 'hold'
