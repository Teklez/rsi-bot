from sqlalchemy import Column, Integer, BigInteger, DateTime
from sqlalchemy.sql import func
from ..session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
