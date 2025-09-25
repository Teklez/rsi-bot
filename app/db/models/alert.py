# app/db/models/alert.py
from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime
from sqlalchemy.sql import func
from ..session import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    symbol_id = Column(Integer, ForeignKey("symbols.id", ondelete="CASCADE"))
    rsi_value = Column(Numeric, nullable=False)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
