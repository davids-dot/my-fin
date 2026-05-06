from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Position(Base):
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False)
    buy_price = Column(Float, nullable=False)
    buy_time = Column(DateTime, default=datetime.now)
    volume = Column(Integer, nullable=False)
    last_observed_price = Column(Float, nullable=True)
