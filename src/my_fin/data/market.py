import akshare as ak

def get_daily_close_prices(symbol: str, num_days: int = 2) -> list[float]:
    """
    获取最近 N 天的日线收盘价 (剔除今天)。
    注意: symbol 需要适配 akshare 格式 (例如: sh600519 -> 600519)
    """
    try:
        code = symbol[2:] if symbol.startswith(('sh', 'sz')) else symbol
        # 获取 A 股日频历史数据，按前复权
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
        if df.empty or len(df) < num_days:
            return []
        
        # 获取最后几天的数据作为历史日线收盘价
        closes = df['收盘'].tail(num_days).tolist()
        return closes
    except Exception as e:
        print(f"获取日线数据失败 {symbol}: {e}")
        return []

def get_current_price(symbol: str) -> float | None:
    """
    获取盘中最新价格
    """
    try:
        code = symbol[2:] if symbol.startswith(('sh', 'sz')) else symbol
        # 获取实时行情
        df = ak.stock_zh_a_spot_em()
        row = df[df['代码'] == code]
        if not row.empty:
            return float(row.iloc[0]['最新价'])
        return None
    except Exception as e:
        print(f"获取实时价格失败 {symbol}: {e}")
        return None
