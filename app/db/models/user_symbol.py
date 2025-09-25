# app/db/models/user_symbol.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ..session import Base

class UserSymbol(Base):
    __tablename__ = "user_symbols"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    symbol_id = Column(Integer, ForeignKey("symbols.id", ondelete="CASCADE"), primary_key=True)
