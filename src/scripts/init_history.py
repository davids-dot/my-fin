import akshare as ak
from sqlalchemy.dialects.sqlite import insert
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

def init_stock_list():
    """
    获取全市场 A 股列表及基本面快照并存入 stock_list 表
    """
    logger.info(f"开始获取全市场 A 股列表及基本面数据... 当前配置的数据源: {DATA_PROVIDER}")
    try:
        if DATA_PROVIDER == 'em':
            # 记录请求信息
            logger.info("正在请求 东方财富 (East Money) 接口")
            logger.info("目标函数: ak.stock_zh_a_spot_em()")
            
            # 使用东财接口获取全市场快照 (包含 PE, 市值, 行业)
            df = ak.stock_zh_a_spot_em()
            code_col, name_col = '代码', '名称'
        else:
            # 回退使用新浪接口 (只包含基础字段)
            logger.info("正在请求 新浪财经 (Sina) 接口")
            logger.info("目标函数: ak.stock_info_a_code_name()")
            df = ak.stock_info_a_code_name()
            code_col, name_col = 'code', 'name'
            
        session = get_session()
        count = 0
        for _, row in df.iterrows():
            code = str(row[code_col])
            name = str(row[name_col])
            
            # 简单判断市场
            if code.startswith('6'):
                market = 'sh'
            elif code.startswith('0') or code.startswith('3'):
                market = 'sz'
            elif code.startswith('4') or code.startswith('8'):
                market = 'bj'
            else:
                continue
                
            symbol = f"{market}{code}"
            
            # 提取基本面字段 (仅东财接口支持)
            pe, market_cap, industry = None, None, None
            if DATA_PROVIDER == 'em':
                try:
                    pe = float(row['市盈率-动态']) if pd.notna(row['市盈率-动态']) else None
                    market_cap = float(row['总市值']) / 1e8 if pd.notna(row['总市值']) else None # 转换为亿元
                    industry = str(row['板块']) if pd.notna(row['板块']) else None
                except (ValueError, KeyError):
                    pass

            # 使用 SQLite 的 UPSERT 语法
            stmt = insert(StockList).values(
                symbol=symbol,
                name=name,
                market=market,
                status='ACTIVE',
                pe=pe,
                market_cap=market_cap,
                industry=industry
            ).on_conflict_do_update(
                index_elements=['symbol'],
                set_={
                    'name': name,
                    'pe': pe,
                    'market_cap': market_cap,
                    'industry': industry,
                    'status': 'ACTIVE'
                }
            )
            
            session.execute(stmt)
            count += 1
            
        session.commit()
        session.close()
        logger.info(f"股票列表及基本面初始化完成，共处理 {count} 只股票。")
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
        
        max_retries = 3
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                # 获取历史日线数据 (不复权)
                df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=end_date, adjust="")
                
                if df.empty:
                    logger.warning(f"[{symbol}] 无历史数据，跳过。")
                    success = True
                    break
                
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
                    
                success = True
                
            except Exception as e:
                retry_count += 1
                session.rollback()
                wait_time = retry_count * 2  # 递增等待时间: 2s, 4s, 6s
                logger.warning(f"[{symbol}] 拉取失败 (尝试 {retry_count}/{max_retries}): {e}. 等待 {wait_time}s 后重试...")
                time.sleep(wait_time)
                
        if not success:
            logger.error(f"[{symbol}] 彻底拉取失败，跳过该股票。")
            
        # 严格控制请求频率，防止被封 IP (东方财富对高频非常敏感)
        time.sleep(0.5)  # 从 0.2s 增加到 0.5s
            
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
