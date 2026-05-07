from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Position(Base):
    """
    持仓记录表
    用于记录当前策略买入并持有中的股票状态
    """
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # 唯一自增主键
    symbol = Column(String(20), unique=True, nullable=False)    # 股票代码 (如 sh600519)
    buy_price = Column(Float, nullable=False)                   # 买入成本价
    buy_time = Column(DateTime, default=datetime.now)           # 买入时间
    volume = Column(Integer, nullable=False)                    # 持仓数量 (股数)
    last_observed_price = Column(Float, nullable=True)          # 最后观察价格 (用于计算回落止盈)
