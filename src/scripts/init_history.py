import akshare as ak
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy import text
import pandas as pd
from datetime import datetime
import time

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import logger
from state.db import init_db, get_session
from state.models import StockList, StockDaily
from data.market import _extract_code

def init_stock_list():
    """
    获取全市场 A 股列表并存入 stock_list 表
    """
    logger.info("开始获取全市场 A 股列表...")
    try:
        # 获取 A 股所有股票信息 (新浪接口)
        df = ak.stock_info_a_code_name()
        
        session = get_session()
        count = 0
        for _, row in df.iterrows():
            code = str(row['code'])
            name = str(row['name'])
            
            # 简单判断市场
            if code.startswith('6'):
                market = 'sh'
            elif code.startswith('0') or code.startswith('3'):
                market = 'sz'
            elif code.startswith('4') or code.startswith('8'):
                market = 'bj'
            else:
                continue # 忽略其他
                
            symbol = f"{market}{code}"
            
            # 使用 SQLite 的 UPSERT 语法 (INSERT OR IGNORE)
            stmt = insert(StockList).values(
                symbol=symbol,
                name=name,
                market=market,
                status='ACTIVE'
            ).on_conflict_do_nothing()
            
            session.execute(stmt)
            count += 1
            
        session.commit()
        session.close()
        logger.info(f"股票列表初始化完成，共插入/更新 {count} 只股票。")
        return True
    except Exception as e:
        logger.error(f"初始化股票列表失败: {e}", exc_info=True)
        return False

def init_historical_daily(start_date="20200101"):
    """
    拉取全市场所有股票的历史日线数据 (原始/不复权)
    """
    session = get_session()
    # 获取所有 ACTIVE 股票
    stocks = session.query(StockList).filter(StockList.status == 'ACTIVE').all()
    total = len(stocks)
    logger.info(f"开始拉取历史日线数据，共计 {total} 只股票，起点日期: {start_date}")
    
    end_date = datetime.now().strftime("%Y%m%d")
    
    for idx, stock in enumerate(stocks):
        symbol = stock.symbol
        code = _extract_code(symbol)
        logger.info(f"[{idx+1}/{total}] 正在拉取 {symbol} ({stock.name}) ...")
        
        try:
            # 获取历史日线数据 (不复权)
            df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=end_date, adjust="")
            
            if df.empty:
                logger.warning(f"[{symbol}] 无历史数据，跳过。")
                continue
            
            # 批量插入准备
            records = []
            for _, row in df.iterrows():
                # 转换日期格式: "2023-01-01" -> datetime.date
                try:
                    trade_date = datetime.strptime(str(row['日期']), "%Y-%m-%d").date()
                except ValueError:
                    # 有些接口可能返回 20230101
                    trade_date = datetime.strptime(str(row['日期']), "%Y%m%d").date()
                    
                records.append({
                    "symbol": symbol,
                    "trade_date": trade_date,
                    "open": float(row['开盘']),
                    "close": float(row['收盘']),
                    "high": float(row['最高']),
                    "low": float(row['最低']),
                    "volume": int(row['成交量']),
                    "amount": float(row['成交额'])
                })
            
            if records:
                # 批量 UPSERT
                stmt = insert(StockDaily).values(records)
                stmt = stmt.on_conflict_do_nothing(index_elements=['symbol', 'trade_date'])
                session.execute(stmt)
                session.commit()
                
            # 控制请求频率，防止被封 IP
            time.sleep(0.2)
            
        except Exception as e:
            logger.error(f"[{symbol}] 拉取历史数据失败: {e}")
            session.rollback()
            time.sleep(1) # 出错后多等一会
            
    session.close()
    logger.info("全市场历史数据初始化完成！")

if __name__ == "__main__":
    logger.info("--- 开始执行初始化脚本 ---")
    init_db()
    
    # 1. 更新股票列表
    success = init_stock_list()
    
    # 2. 拉取历史数据 (建议手动执行时再放开注释，因为非常耗时)
    if success:
        print("\n股票列表已更新。")
        print("警告: 接下来将拉取 5000+ 只股票的历史数据，耗时可能超过 1 小时。")
        confirm = input("是否继续拉取历史数据？(y/n): ")
        if confirm.lower() == 'y':
            init_historical_daily(start_date="20230101") # 默认拉取近一年多
        else:
            print("已取消历史数据拉取。")
