from datetime import datetime
from sqlalchemy import text
from sqlalchemy.dialects.sqlite import insert

from config import logger
from state.db import get_session
from state.models import StockDaily, WatchList
from data.market import fetch_incremental_daily_raw

def run_daily_screener():
    """
    离线日线选股器
    1. 获取全市场今日日线数据，更新到 stock_daily
    2. 执行“连涨2天”策略
    3. 满足条件的个股加入 watch_list (明日监控池)
    """
    logger.info("=== 启动日线选股器 (Daily Screener) ===")
    
    # 1. 获取并更新增量数据
    df = fetch_incremental_daily_raw()
    if df is None or df.empty:
        logger.error("未获取到今日增量数据，选股中断。")
        return
        
    today = datetime.now().date()
    session = get_session()
    
    logger.info("正在更新 stock_daily 表...")
    records = []
    for _, row in df.iterrows():
        code = str(row['代码'])
        # 判断市场，简单拼接
        if code.startswith('6'):
            symbol = f"sh{code}"
        elif code.startswith('0') or code.startswith('3'):
            symbol = f"sz{code}"
        else:
            continue
            
        try:
            # 数据清洗
            close_price = float(row['最新价'])
            open_price = float(row['开盘'])
            high_price = float(row['最高'])
            low_price = float(row['最低'])
            vol = int(row['成交量'])
            amt = float(row['成交额'])
            
            # 如果没开盘或停牌，价格可能是 NaN
            import math
            if math.isnan(close_price) or math.isnan(open_price):
                continue
                
            records.append({
                "symbol": symbol,
                "trade_date": today,
                "open": open_price,
                "close": close_price,
                "high": high_price,
                "low": low_price,
                "volume": vol,
                "amount": amt
            })
        except Exception:
            continue
            
    if records:
        stmt = insert(StockDaily).values(records)
        stmt = stmt.on_conflict_do_nothing(index_elements=['symbol', 'trade_date'])
        session.execute(stmt)
        session.commit()
    logger.info(f"增量数据更新完成，共处理 {len(records)} 条记录。")

    # 2. 执行选股策略 (连续两日上涨: T收盘 > T-1收盘 且 T-1收盘 > T-2收盘)
    # 为了性能，我们直接写 SQL 查询过去3天的数据
    logger.info("开始执行选股策略...")
    
    # SQLite 窗口函数查询连涨
    query = text("""
    WITH ranked_daily AS (
        SELECT 
            symbol, 
            trade_date, 
            close,
            LAG(close, 1) OVER (PARTITION BY symbol ORDER BY trade_date) as prev_close,
            LAG(close, 2) OVER (PARTITION BY symbol ORDER BY trade_date) as prev2_close,
            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY trade_date DESC) as rn
        FROM stock_daily
    )
    SELECT symbol, close as target_buy_price
    FROM ranked_daily
    WHERE rn = 1 
      AND close > prev_close 
      AND prev_close > prev2_close
    """)
    
    results = session.execute(query).fetchall()
    
    # 3. 更新 WatchList
    # 首先将旧的 PENDING 状态置为 EXPIRED
    session.execute(text("UPDATE watch_list SET status = 'EXPIRED' WHERE status = 'PENDING'"))
    
    watch_records = []
    for r in results:
        watch_records.append({
            "symbol": r[0],
            "add_date": today,
            "target_buy_price": r[1],
            "status": "PENDING"
        })
        
    if watch_records:
        stmt = insert(WatchList).values(watch_records)
        stmt = stmt.on_conflict_do_update(
            index_elements=['symbol'],
            set_={
                'add_date': stmt.excluded.add_date,
                'target_buy_price': stmt.excluded.target_buy_price,
                'status': stmt.excluded.status
            }
        )
        session.execute(stmt)
        
    session.commit()
    session.close()
    
    logger.info(f"=== 日线选股器执行完毕，共选出 {len(watch_records)} 只股票加入明日监控池 ===")

if __name__ == "__main__":
    run_daily_screener()
