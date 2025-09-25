from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from ..session import Base

class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    rsi_threshold = Column(Integer, nullable=False, default=30)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
