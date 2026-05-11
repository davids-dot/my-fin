from datetime import datetime
from sqlalchemy import text
from sqlalchemy.dialects.sqlite import insert
import pandas as pd

from config import logger, MAX_PE, MIN_MARKET_CAP, EXCLUDE_INDUSTRIES
from state.db import get_session
from state.models import StockDaily, WatchList, StockList
from data.market import fetch_incremental_daily_raw

def run_daily_screener():
    """
    离线日线选股器
    1. 获取全市场今日日线数据，更新到 stock_daily 和 stock_list (基本面)
    2. 执行“多因子”选股策略 (基本面过滤 + 技术面选股)
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
    
    logger.info("正在更新 stock_daily 和 stock_list 基本面...")
    daily_records = []
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
            # 1.1 准备日线历史数据
            close_price = float(row['最新价'])
            open_price = float(row['开盘'])
            high_price = float(row['最高'])
            low_price = float(row['最低'])
            vol = int(row['成交量'])
            amt = float(row['成交额'])
            
            import math
            if not math.isnan(close_price) and not math.isnan(open_price):
                daily_records.append({
                    "symbol": symbol,
                    "trade_date": today,
                    "open": open_price,
                    "close": close_price,
                    "high": high_price,
                    "low": low_price,
                    "volume": vol,
                    "amount": amt
                })

            # 1.2 更新 stock_list 中的基本面快照 (精简写法)
            data = {
                'symbol': symbol, 'name': str(row['名称']),
                'pe': float(row['市盈率-动态']) if pd.notna(row['市盈率-动态']) else None,
                'market_cap': float(row['总市值']) / 1e8 if pd.notna(row['总市值']) else None,
                'industry': str(row['板块']) if pd.notna(row['板块']) else None
            }
            
            stmt_list = insert(StockList).values(data).on_conflict_do_update(
                index_elements=['symbol'],
                set_={'pe': data['pe'], 'market_cap': data['market_cap'], 'industry': data['industry']}
            )
            session.execute(stmt_list)

        except Exception:
            continue
            
    if daily_records:
        stmt_daily = insert(StockDaily).values(daily_records)
        stmt_daily = stmt_daily.on_conflict_do_nothing(index_elements=['symbol', 'trade_date'])
        session.execute(stmt_daily)
        
    session.commit()
    logger.info(f"增量数据及基本面更新完成，共处理 {len(daily_records)} 条日线记录。")

    # 2. 执行选股策略 (基本面过滤 + 连续两日上涨)
    
    # SQLite 窗口函数查询连涨，并关联 stock_list 进行基本面过滤
    # 过滤条件: PE < MAX_PE, 市值 > MIN_MARKET_CAP, 排除指定行业
    exclude_industries_str = "','".join(EXCLUDE_INDUSTRIES)
    query = text(f"""
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
    SELECT d.symbol, d.close as target_buy_price
    FROM ranked_daily d
    JOIN stock_list s ON d.symbol = s.symbol
    WHERE d.rn = 1 
      AND d.close > d.prev_close 
      AND d.prev_close > d.prev2_close
      AND (s.pe IS NULL OR s.pe < :max_pe)
      AND (s.market_cap IS NULL OR s.market_cap > :min_mcap)
      AND (s.industry IS NULL OR s.industry NOT IN ('{exclude_industries_str}'))
    """)
    
    results = session.execute(query, {
        "max_pe": MAX_PE,
        "min_mcap": MIN_MARKET_CAP
    }).fetchall()
    
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
