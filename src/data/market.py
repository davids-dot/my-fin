import akshare as ak
from config import logger
import requests
import urllib3

def _extract_code(symbol: str) -> str:
    """提取股票代码，去除市场前缀"""
    return symbol[2:] if symbol.startswith(('sh', 'sz')) else symbol

def get_daily_close_prices(symbol: str, num_days: int = 2) -> list[float] | None:
    """
    获取最近 N 天的日线收盘价 (剔除今天)。
    注意: symbol 需要适配 akshare 格式 (例如: sh600519 -> 600519)
    """
    try:
        code = _extract_code(symbol)
        
        # 获取 A 股日频历史数据，按前复权
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
        if df.empty or len(df) < num_days:
            return None
        
        # 获取最后几天的数据作为历史日线收盘价
        closes = df['收盘'].tail(num_days).tolist()
        return closes
    except (requests.exceptions.RequestException, urllib3.exceptions.HTTPError) as e:
        logger.error(f"网络异常: 获取日线数据失败 {symbol}: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"未知异常: 获取日线数据失败 {symbol}: {e}", exc_info=True)
        return None

def get_current_price(symbol: str) -> float | None:
    """
    获取单只股票盘中最新价格 (高效，无分页)
    """
    try:
        code = _extract_code(symbol)
        # 获取单只股票的实时行情数据 (新浪接口，速度极快)
        df = ak.stock_zh_a_spot_sina()
        row = df[df['代码'] == symbol] # 注意: 新浪接口的"代码"列通常带有 sh/sz 前缀，直接用传入的 symbol 匹配
        if not row.empty:
            return float(row.iloc[0]['最新价'])
        return None
    except (requests.exceptions.RequestException, urllib3.exceptions.HTTPError) as e:
        logger.error(f"网络异常: 获取单只股票实时价格失败 {symbol}: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"未知异常: 获取单只股票实时价格失败 {symbol}: {e}", exc_info=True)
        return None

def list_all_symbol_price() -> dict[str, float]:
    """
    批量获取全市场所有股票的最新价格
    返回字典格式: { '600519': 1500.0, ... }
    注意: 该接口会分页拉取全市场数据，耗时较长 (约1分钟)
    """
    try:
        # 获取全市场实时行情 (东方财富接口，分页拉取)
        df = ak.stock_zh_a_spot_em()
        if df.empty:
            return {}
            
        # 将代码作为索引，最新价转换为字典
        # df 结构包含 '代码' 和 '最新价' 列
        result_dict = dict(zip(df['代码'], df['最新价']))
        # 过滤掉 NaN 价格 (停牌等情况)
        import pandas as pd
        return {k: float(v) for k, v in result_dict.items() if pd.notna(v)}
    except (requests.exceptions.RequestException, urllib3.exceptions.HTTPError) as e:
        logger.error(f"网络异常: 批量获取全市场价格失败: {e}", exc_info=True)
        return {}
    except Exception as e:
        logger.error(f"未知异常: 批量获取全市场价格失败: {e}", exc_info=True)
        return {}
