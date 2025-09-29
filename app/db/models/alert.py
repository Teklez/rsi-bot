# app/db/models/alert.py
from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, String
from sqlalchemy.sql import func
from ..session import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    symbol = Column(String, nullable=False)
    rsi_value = Column(Numeric, nullable=False)
    alert_type = Column(String, nullable=False)  # 'oversold' or 'overbought'
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
