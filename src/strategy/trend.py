from datetime import datetime
from data.market import get_daily_close_prices, get_current_price
from state.db import get_session
from state.models import Position
from notify.bark import send_notification
from config import logger

def run_strategy(symbol: str):
    """
    执行策略逻辑:
    买入: T+1收盘 > T收盘，且 T+2(当前盘中) > T+1收盘
    卖出: 出现回落(当前 < 上次观察价格) 且 当前价格 > 买入价格(有收益)
    """
    session = get_session()
    try:
        current_price = get_current_price(symbol)
        if current_price is None:
            return

        position = session.query(Position).filter(Position.symbol == symbol).first()

        if not position:
            # 尚未持仓，判断是否满足买入条件
            # 获取最近2个交易日的收盘价 (T 和 T+1)
            closes = get_daily_close_prices(symbol, num_days=2)
            if closes is not None and len(closes) >= 2:
                day_t = closes[0]         # T 日收盘价
                day_t_plus_1 = closes[1]  # T+1 日收盘价

                # 判断连涨: T+1 > T 且 当前盘中 > T+1
                if day_t_plus_1 > day_t and current_price > day_t_plus_1:
                    # 触发买入
                    new_pos = Position(
                        symbol=symbol,
                        buy_price=current_price,
                        buy_time=datetime.now(),
                        volume=100,  # 默认买入 100 股
                        last_observed_price=current_price
                    )
                    session.add(new_pos)
                    session.commit()
                    send_notification(
                        title="【买入触发】", 
                        body=f"标的: {symbol}\n买入价: {current_price}\n逻辑: 连续2天上涨"
                    )
        else:
            # 已持仓，判断是否满足卖出条件
            last_price = position.last_observed_price or position.buy_price
            
            # 判断回落且盈利: 当前价格 < 上次观察价 且 当前价格 > 买入价
            if current_price < last_price and current_price > position.buy_price:
                profit = (current_price - position.buy_price) * position.volume
                session.delete(position)
                session.commit()
                send_notification(
                    title="【卖出触发】", 
                    body=f"标的: {symbol}\n卖出价: {current_price}\n收益: {profit:.2f}\n逻辑: 价格回落且止盈"
                )
            else:
                # 更新最高/最新观察价，用于下次判断回落
                # 这里可以采用追踪止盈逻辑，只有当价格创新高时才更新，或者每次都更新
                # 为了敏感度，我们每次都更新为最新价格，这样只要跌了就会触发
                if current_price != last_price:
                    position.last_observed_price = current_price
                    session.commit()
                    
    except Exception as e:
        logger.error(f"策略执行异常 {symbol}: {e}", exc_info=True)
    finally:
        session.close()
