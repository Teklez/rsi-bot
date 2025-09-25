# app/db/models/symbol.py
from sqlalchemy import Column, Integer, String
from ..session import Base

class Symbol(Base):
    __tablename__ = "symbols"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
