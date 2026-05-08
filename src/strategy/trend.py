from datetime import datetime
from data.market import list_all_symbol_price
from state.db import get_session
from state.models import Position, WatchList
from notify.bark import send_notification
from config import logger

def run_intraday_monitor():
    """
    盘中实时监控 (Intraday Monitor)
    只监控 watch_list (PENDING) 和 positions 中的股票
    """
    session = get_session()
    try:
        # 1. 获取需要监控的股票池
        pending_watch = session.query(WatchList).filter(WatchList.status == 'PENDING').all()
        positions = session.query(Position).all()
        
        watch_symbols = [w.symbol for w in pending_watch]
        pos_symbols = [p.symbol for p in positions]
        
        monitor_symbols = set(watch_symbols + pos_symbols)
        if not monitor_symbols:
            logger.info("当前无股票需要监控 (空仓且监控池为空)")
            return
            
        logger.info(f"开始盘中监控，共 {len(monitor_symbols)} 只标的...")
        
        # 2. 批量获取实时价格
        current_prices = list_all_symbol_price()
        if not current_prices:
            logger.warning("未获取到实时价格数据，跳过本次监控。")
            return
            
        # 3. 遍历评估
        for symbol in monitor_symbols:
            # list_all_symbol_price 返回的字典 key 不带 sh/sz 前缀
            code = symbol[2:] if symbol.startswith(('sh', 'sz')) else symbol
            current_price = current_prices.get(code)
            
            if current_price is None:
                continue
                
            # --- 评估买入逻辑 (在监控池中) ---
            if symbol in watch_symbols:
                watch_record = next(w for w in pending_watch if w.symbol == symbol)
                
                # 如果当前价格 > 目标买入价 (昨日收盘价)
                if current_price > watch_record.target_buy_price:
                    # 触发买入
                    new_pos = Position(
                        symbol=symbol,
                        buy_price=current_price,
                        buy_time=datetime.now(),
                        volume=100,  # 默认买入 100 股
                        last_observed_price=current_price
                    )
                    session.add(new_pos)
                    
                    # 更新监控池状态
                    watch_record.status = 'BOUGHT'
                    
                    logger.info(f"【买入触发】标的: {symbol}, 买入价: {current_price}, 目标价: {watch_record.target_buy_price}")
                    send_notification(
                        title="【买入触发】", 
                        body=f"标的: {symbol}\n买入价: {current_price}\n逻辑: 突破昨日收盘价"
                    )
            
            # --- 评估卖出逻辑 (已持仓) ---
            if symbol in pos_symbols:
                position = next(p for p in positions if p.symbol == symbol)
                last_price = position.last_observed_price or position.buy_price
                
                # 判断回落且盈利: 当前价格 < 上次观察价 且 当前价格 > 买入价
                if current_price < last_price and current_price > position.buy_price:
                    profit = (current_price - position.buy_price) * position.volume
                    session.delete(position)
                    
                    logger.info(f"【卖出触发】标的: {symbol}, 卖出价: {current_price}, 收益: {profit:.2f}")
                    send_notification(
                        title="【卖出触发】", 
                        body=f"标的: {symbol}\n卖出价: {current_price}\n收益: {profit:.2f}\n逻辑: 价格回落且止盈"
                    )
                else:
                    # 追踪止盈：更新最高/最新观察价
                    if current_price != last_price:
                        position.last_observed_price = current_price
                        
        session.commit()
        
    except Exception as e:
        logger.error(f"盘中监控执行异常: {e}", exc_info=True)
        session.rollback()
    finally:
        session.close()
