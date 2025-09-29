# app/db/models/user_symbol.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..base import Base

class UserSymbol(Base):
    __tablename__ = "user_symbols"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String, nullable=False)
    
    user = relationship("User", back_populates="symbols")
