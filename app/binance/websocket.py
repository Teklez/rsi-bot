import asyncio
import json
import websockets
from typing import Dict, List, Callable, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BinanceWebSocketClient:
    BASE_URL = "wss://stream.binance.com:9443/ws"
    
    def __init__(self):
        self.connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.price_data: Dict[str, List[float]] = {}
        self.callbacks: List[Callable] = []
        self.running = False
    
    def add_callback(self, callback: Callable):
        """Add a callback function to be called when price data is received"""
        self.callbacks.append(callback)
    
    async def start_stream(self, symbols: List[str]):
        """Start WebSocket streams for given symbols"""
        if not symbols:
            return
        
        self.running = True
        
        # Create stream names for kline data (1h intervals)
        streams = [f"{symbol.lower()}@kline_1h" for symbol in symbols]
        stream_url = f"{self.BASE_URL}/{'/'.join(streams)}"
        
        logger.info(f"Starting WebSocket stream for symbols: {symbols}")
        
        try:
            async with websockets.connect(stream_url) as websocket:
                self.connections['kline'] = websocket
                
                async for message in websocket:
                    if not self.running:
                        break
                    
                    try:
                        data = json.loads(message)
                        await self._handle_kline_data(data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing WebSocket message: {e}")
                    except Exception as e:
                        logger.error(f"Error handling WebSocket data: {e}")
                        
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.running = False
    
    async def _handle_kline_data(self, data: Dict):
        """Handle incoming kline data from WebSocket"""
        try:
            if 'k' not in data:
                return
            
            kline = data['k']
            symbol = kline['s']
            is_closed = kline['x']  # True if kline is closed
            
            if not is_closed:
                return  # Only process closed klines for RSI calculation
            
            close_price = float(kline['c'])
            
            # Store price data
            if symbol not in self.price_data:
                self.price_data[symbol] = []
            
            self.price_data[symbol].append(close_price)
            
            # Keep only last 100 prices for RSI calculation
            if len(self.price_data[symbol]) > 100:
                self.price_data[symbol] = self.price_data[symbol][-100:]
            
            # Notify callbacks
            for callback in self.callbacks:
                try:
                    await callback(symbol, self.price_data[symbol].copy())
                except Exception as e:
                    logger.error(f"Error in callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling kline data: {e}")
    
    async def stop_stream(self):
        """Stop all WebSocket streams"""
        self.running = False
        
        for connection in self.connections.values():
            if not connection.closed:
                await connection.close()
        
        self.connections.clear()
        logger.info("WebSocket streams stopped")
    
    def get_price_data(self, symbol: str) -> List[float]:
        """Get stored price data for a symbol"""
        return self.price_data.get(symbol, [])
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get the latest price for a symbol"""
        prices = self.price_data.get(symbol, [])
        return prices[-1] if prices else None
