import requests
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class KlineData:
    symbol: str
    open_time: datetime
    close_time: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    quote_volume: float
    trades_count: int
    taker_buy_base_volume: float
    taker_buy_quote_volume: float

class BinanceClient:
    BASE_URL = "https://api.binance.com/api/v3"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RSI-Bot/1.0'
        })
    
    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> List[KlineData]:
        """
        Get kline/candlestick data for a symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Kline interval (1m, 5m, 15m, 30m, 1h, 4h, 1d)
            limit: Number of klines to retrieve (max 1000)
        """
        url = f"{self.BASE_URL}/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': min(limit, 1000)
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            klines = []
            for kline in data:
                klines.append(KlineData(
                    symbol=symbol,
                    open_time=datetime.fromtimestamp(kline[0] / 1000),
                    close_time=datetime.fromtimestamp(kline[6] / 1000),
                    open_price=float(kline[1]),
                    high_price=float(kline[2]),
                    low_price=float(kline[3]),
                    close_price=float(kline[4]),
                    volume=float(kline[5]),
                    quote_volume=float(kline[7]),
                    trades_count=int(kline[8]),
                    taker_buy_base_volume=float(kline[9]),
                    taker_buy_quote_volume=float(kline[10])
                ))
            
            return klines
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching klines for {symbol}: {e}")
            return []
    
    def get_24hr_ticker(self, symbol: str) -> Optional[Dict]:
        """Get 24hr ticker price change statistics"""
        url = f"{self.BASE_URL}/ticker/24hr"
        params = {'symbol': symbol}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching 24hr ticker for {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        url = f"{self.BASE_URL}/ticker/price"
        params = {'symbol': symbol}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return float(data['price'])
        except (requests.exceptions.RequestException, KeyError, ValueError) as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return None
