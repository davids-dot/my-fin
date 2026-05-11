import akshare as ak
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import pandas as pd
from datetime import datetime
import time

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import logger, DATA_PROVIDER
from state.db import init_db, get_session
from state.models import StockList, StockDaily
from data.market import _extract_code

def _fetch_stock_list_data():
    """获取股票列表原始数据"""
    if DATA_PROVIDER == 'em':
        logger.info("请求 东方财富 接口: ak.stock_zh_a_spot_em()")
        return ak.stock_zh_a_spot_em(), '代码', '名称'
    
    logger.info("请求 新浪财经 接口: ak.stock_info_a_code_name()")
    return ak.stock_info_a_code_name(), 'code', 'name'

def _parse_fundamental(row) -> tuple:
    """提取基本面字段 (仅东财支持)"""
    if DATA_PROVIDER != 'em':
        return None, None, None
        
    try:
        pe = float(row['市盈率-动态']) if pd.notna(row['市盈率-动态']) else None
        mcap = float(row['总市值']) / 1e8 if pd.notna(row['总市值']) else None
        ind = str(row['板块']) if pd.notna(row['板块']) else None
        return pe, mcap, ind
    except (ValueError, KeyError):
        return None, None, None

def _upsert_stock_list(session, df, code_col, name_col) -> int:
    """批量更新股票基础信息"""
    count = 0
    for _, row in df.iterrows():
        code = str(row[code_col])
        if code.startswith('6'): market = 'sh'
        elif code.startswith(('0', '3')): market = 'sz'
        elif code.startswith(('4', '8')): market = 'bj'
        else: continue
            
        pe, mcap, ind = _parse_fundamental(row)
        data = {
            'symbol': f"{market}{code}", 'name': str(row[name_col]),
            'market': market, 'status': 'ACTIVE',
            'pe': pe, 'market_cap': mcap, 'industry': ind
        }
        
        stmt = insert(StockList).values(data).on_conflict_do_update(
            index_elements=['symbol'], set_=data
        )
        session.execute(stmt)
        count += 1
    return count

def init_stock_list():
    """初始化股票列表及基本面"""
    logger.info(f"开始获取 A 股列表... 数据源: {DATA_PROVIDER}")
    try:
        df, code_col, name_col = _fetch_stock_list_data()
        session = get_session()
        count = _upsert_stock_list(session, df, code_col, name_col)
        
        session.commit()
        session.close()
        logger.info(f"股票列表初始化完成，共处理 {count} 只股票。")
        return True
    except Exception as e:
        logger.error(f"初始化股票列表失败: {e}", exc_info=True)
        return False

def _parse_trade_date(date_str: str) -> datetime.date:
    """解析日期字符串，兼容 'YYYY-MM-DD' 和 'YYYYMMDD' 格式"""
    try:
        return datetime.strptime(str(date_str), "%Y-%m-%d").date()
    except ValueError:
        return datetime.strptime(str(date_str), "%Y%m%d").date()

def _fetch_and_save_daily(session, symbol, code, start_date, end_date) -> bool:
    """拉取并保存单只股票的历史日线数据"""
    if DATA_PROVIDER == 'em':
        df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=end_date, adjust="")
    else:
        # 新浪日线接口参数不同，不支持 start_date，通常返回近期数据
        df = ak.stock_zh_a_daily(symbol=symbol)
        
    if df is None or df.empty:
        logger.warning(f"[{symbol}] 无历史数据，跳过。")
        return True
        
    records = []
    # 新浪接口列名为 'date', 东财为 '日期'
    date_col = 'date' if DATA_PROVIDER != 'em' else '日期'
    
    for _, row in df.iterrows():
        records.append({
            "symbol": symbol,
            "trade_date": _parse_trade_date(row[date_col]),
            "open": float(row.get('开盘', row.get('open', 0))),
            "close": float(row.get('收盘', row.get('close', 0))),
            "high": float(row.get('最高', row.get('high', 0))),
            "low": float(row.get('最低', row.get('low', 0))),
            "volume": int(row.get('成交量', row.get('volume', 0))),
            "amount": float(row.get('成交额', row.get('amount', 0)))
        })
        
    if records:
        for i in range(0, len(records), 100):
            chunk = records[i:i+100]
            stmt = insert(StockDaily).values(chunk).on_conflict_do_nothing(
                index_elements=['symbol', 'trade_date']
            )
            session.execute(stmt)
        session.commit()
    return True

def init_historical_daily(start_date="20200101"):
    """拉取全市场所有股票的历史日线数据"""
    session = get_session()
    stocks = session.query(StockList).filter(StockList.status == 'ACTIVE').all()
    total = len(stocks)
    logger.info(f"开始拉取历史日线数据，共计 {total} 只股票，数据源: {DATA_PROVIDER}")
    
    end_date = datetime.now().strftime("%Y%m%d")
    
    for idx, stock in enumerate(stocks):
        symbol = stock.symbol
        code = _extract_code(symbol)
        logger.info(f"[{idx+1}/{total}] 正在拉取 {symbol} ({stock.name}) ...")
        
        max_retries = 3
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                success = _fetch_and_save_daily(session, symbol, code, start_date, end_date)
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"[{symbol}] 数据库异常，停止重试: {e}")
                retry_count = max_retries
            except Exception as e:
                retry_count += 1
                session.rollback()
                wait_time = retry_count * 2
                logger.warning(f"[{symbol}] 拉取失败 ({retry_count}/{max_retries}): {e}. 等待 {wait_time}s...")
                time.sleep(wait_time)
                
        if not success:
            logger.error(f"[{symbol}] 彻底拉取失败，跳过。")
            
        time.sleep(0.5)  # 频率控制
            
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
