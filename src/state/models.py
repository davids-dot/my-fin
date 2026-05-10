from sqlalchemy import Column, Integer, String, Float, DateTime, Date, BigInteger
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class StockList(Base):
    """
    股票基础信息表 (全市场 A 股列表)
    """
    __tablename__ = 'stock_list'
    
    symbol = Column(String(20), primary_key=True)       # 股票代码 (带前缀)
    name = Column(String(50), nullable=False)           # 股票名称
    market = Column(String(10))                         # 所属市场
    status = Column(String(10), default='ACTIVE')       # 状态
    pe = Column(Float)                                  # 市盈率 (动态)
    market_cap = Column(Float)                          # 总市值 (亿元)
    industry = Column(String(50))                       # 所属行业

class StockDaily(Base):
    """
    股票日线历史表 (存储原始不复权数据)
    """
    __tablename__ = 'stock_daily'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True) # 股票代码
    trade_date = Column(Date, nullable=False, index=True)   # 交易日期
    open = Column(Float)                                    # 开盘价
    close = Column(Float)                                   # 收盘价
    high = Column(Float)                                    # 最高价
    low = Column(Float)                                     # 最低价
    volume = Column(BigInteger)                             # 成交量
    amount = Column(Float)                                  # 成交额

class WatchList(Base):
    """
    明日监控池 (选股结果表)
    """
    __tablename__ = 'watch_list'
    
    symbol = Column(String(20), primary_key=True)           # 股票代码
    add_date = Column(Date, nullable=False)                 # 选入日期
    target_buy_price = Column(Float)                        # 目标买入价
    status = Column(String(10), default='PENDING')          # 状态 (PENDING, BOUGHT, EXPIRED)

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
