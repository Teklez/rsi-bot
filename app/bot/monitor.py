import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Set
from sqlalchemy.orm import Session
import logging

from app.binance.websocket import BinanceWebSocketClient
from app.indicators.rsi import calculate_rsi, get_rsi_signal
from app.db.session import get_db
from app.db.models.user_symbol import UserSymbol
from app.db.models.alert import Alert
from app.db.models.settings import Setting
from app.bot import app

logger = logging.getLogger(__name__)

class RSIMonitor:
    def __init__(self):
        self.ws_client = BinanceWebSocketClient()
        self.running = False
        self.subscribed_symbols: Set[str] = set()
        self.last_alert_time: Dict[str, datetime] = {}
        
        # Add callback for price updates
        self.ws_client.add_callback(self._on_price_update)
    
    async def start_monitoring(self):
        """Start the RSI monitoring with WebSocket"""
        self.running = True
        logger.info("RSI Monitor started with WebSocket")
        
        while self.running:
            try:
                # Get current subscribed symbols
                await self.update_subscribed_symbols()
                
                if self.subscribed_symbols:
                    # Start WebSocket stream for all symbols
                    await self.ws_client.start_stream(list(self.subscribed_symbols))
                else:
                    # No symbols to monitor, wait and retry
                    await asyncio.sleep(30)
                    
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)  # Wait 30 seconds before retrying
    
    async def stop_monitoring(self):
        """Stop the RSI monitoring loop"""
        self.running = False
        await self.ws_client.stop_stream()
        logger.info("RSI Monitor stopped")
    
    async def update_subscribed_symbols(self):
        """Update the list of subscribed symbols from database"""
        db = next(get_db())
        try:
            user_symbols = db.query(UserSymbol).all()
            symbols = set(us.symbol for us in user_symbols)
            
            if symbols != self.subscribed_symbols:
                self.subscribed_symbols = symbols
                logger.info(f"Updated subscribed symbols: {list(symbols)}")
                
        finally:
            db.close()
    
    async def _on_price_update(self, symbol: str, prices: List[float]):
        """Callback for when new price data is received via WebSocket"""
        try:
            if len(prices) < 15:  # Need at least 15 data points for RSI
                return
            
            # Calculate RSI
            rsi_values = calculate_rsi(prices, period=14)
            
            if not rsi_values:
                return
            
            current_rsi = rsi_values[-1]
            logger.info(f"{symbol}: RSI = {current_rsi:.2f}")
            
            # Get RSI thresholds from settings
            db = next(get_db())
            try:
                setting = db.query(Setting).first()
                oversold_threshold = setting.rsi_oversold_threshold if setting else 30
                overbought_threshold = setting.rsi_overbought_threshold if setting else 70
                
                # Check for oversold condition (potential buying opportunity)
                if current_rsi < oversold_threshold:
                    await self.create_alert(db, symbol, current_rsi, 'oversold')
                
                # Check for overbought condition (potential selling opportunity)
                elif current_rsi > overbought_threshold:
                    await self.create_alert(db, symbol, current_rsi, 'overbought')
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error processing price update for {symbol}: {e}")
    
    async def create_alert(self, db: Session, symbol: str, rsi_value: float, alert_type: str):
        """Create an alert for oversold or overbought condition"""
        try:
            # Check if we already alerted recently for this symbol and type
            alert_key = f"{symbol}_{alert_type}"
            last_alert = self.last_alert_time.get(alert_key)
            if last_alert and datetime.utcnow() - last_alert < timedelta(hours=1):
                return  # Skip if we already alerted recently
            
            # Get all users who have this symbol
            user_symbols = db.query(UserSymbol).filter(UserSymbol.symbol == symbol).all()
            
            if not user_symbols:
                return
            
            for user_symbol in user_symbols:
                # Create new alert
                alert = Alert(
                    user_id=user_symbol.user_id,
                    symbol=symbol,
                    rsi_value=rsi_value,
                    alert_type=alert_type
                )
                db.add(alert)
                
                # Send notification to user
                await self.send_alert_notification(user_symbol.user_id, symbol, rsi_value, alert_type)
            
            db.commit()
            self.last_alert_time[alert_key] = datetime.utcnow()
            logger.info(f"Created {alert_type} alerts for {symbol} with RSI {rsi_value:.2f}")
            
        except Exception as e:
            logger.error(f"Error creating alert for {symbol}: {e}")
            db.rollback()
    
    async def send_alert_notification(self, user_id: int, symbol: str, rsi_value: float, alert_type: str):
        """Send alert notification to user via Telegram"""
        try:
            # Get user's telegram_id from user_id
            from app.db.models.user import User
            db = next(get_db())
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return
            
            if alert_type == 'oversold':
                emoji = "📉"
                action = "potential buying opportunity"
                condition = "oversold"
            else:  # overbought
                emoji = "📈"
                action = "potential selling opportunity"
                condition = "overbought"
            
            message = f"{emoji} RSI Alert!\n\n{symbol}: RSI = {rsi_value:.2f}\n\nThis indicates an {condition} condition - {action}!"
            
            await app.bot.send_message(
                chat_id=user.telegram_id,
                text=message
            )
            
            logger.info(f"Sent {alert_type} alert to user {user.telegram_id} for {symbol}")
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
        finally:
            db.close()

# Global monitor instance
monitor = RSIMonitor()
