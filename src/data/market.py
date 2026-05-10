import akshare as ak
from config import logger, DATA_PROVIDER
import requests
import urllib3
import pandas as pd
from datetime import datetime

def _extract_code(symbol: str) -> str:
    """提取股票代码，去除市场前缀"""
    return symbol[2:] if symbol.startswith(('sh', 'sz')) else symbol

def fetch_incremental_daily_raw() -> pd.DataFrame | None:
    """
    增量获取今日全市场的日线数据 (原始/不复权)
    用于每天 15:30 盘后调度，更新 stock_daily 表
    返回 DataFrame，为了统一处理，标准化列名：代码, 名称, 最新价, 开盘, 最高, 最低, 成交量, 成交额
    """
    try:
        logger.info(f"开始拉取今日全市场增量日线数据 (原始)... 当前数据源: {DATA_PROVIDER}")
        
        if DATA_PROVIDER == 'em':
            logger.info("正在请求 东方财富 (East Money) 接口: ak.stock_zh_a_spot_em()")
            df = ak.stock_zh_a_spot_em()
            if df.empty:
                return None
            return df
        else:
            # 使用新浪接口作为替代方案
            logger.info("正在请求 新浪财经 (Sina) 接口: ak.stock_zh_a_spot_sina()")
            # 注意：新浪接口可能不包含完整的市盈率等字段，且列名不同
            df = ak.stock_zh_a_spot_sina()
            if df.empty:
                return None
                
            # 标准化列名以适配下游
            # 新浪接口通常有: 代码, 名称, 最新价, 涨跌额, 涨跌幅, 买入, 卖出, 昨收, 今开, 最高, 最低, 成交量, 成交额
            # 东财接口期望: 代码 (不带前缀), 名称, 最新价, 开盘, 最高, 最低, 成交量, 成交额, 市盈率-动态, 总市值, 板块
            df = df.rename(columns={
                '今开': '开盘'
            })
            
            # 新浪接口的"代码"自带 sh/sz 前缀，我们需要去掉前缀以保持和东财一致，方便下游处理
            if '代码' in df.columns:
                df['代码'] = df['代码'].apply(lambda x: str(x)[2:] if str(x).startswith(('sh', 'sz')) else str(x))
                
            return df
            
    except (requests.exceptions.RequestException, urllib3.exceptions.HTTPError) as e:
        logger.error(f"网络异常: 拉取今日全市场增量数据失败: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"未知异常: 拉取今日全市场增量数据失败: {e}", exc_info=True)
        return None

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
        logger.debug(f"正在请求 新浪财经 (Sina Finance) 接口: ak.stock_zh_a_spot_sina() for {symbol}")
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
    注意: 东财接口会分页拉取全市场数据，耗时较长
    """
    try:
        if DATA_PROVIDER == 'em':
            # 获取全市场实时行情 (东方财富接口，分页拉取)
            logger.debug("正在请求 东方财富 (East Money) 接口: ak.stock_zh_a_spot_em()")
            df = ak.stock_zh_a_spot_em()
            if df.empty:
                return {}
            code_col, price_col = '代码', '最新价'
        else:
            logger.debug("正在请求 新浪财经 (Sina) 接口: ak.stock_zh_a_spot_sina()")
            df = ak.stock_zh_a_spot_sina()
            if df.empty:
                return {}
            # 新浪的"代码"带前缀，去掉它
            df['代码'] = df['代码'].apply(lambda x: str(x)[2:] if str(x).startswith(('sh', 'sz')) else str(x))
            code_col, price_col = '代码', '最新价'
            
        # 将代码作为索引，最新价转换为字典
        result_dict = dict(zip(df[code_col], df[price_col]))
        # 过滤掉 NaN 价格 (停牌等情况)
        return {k: float(v) for k, v in result_dict.items() if pd.notna(v)}
    except (requests.exceptions.RequestException, urllib3.exceptions.HTTPError) as e:
        logger.error(f"网络异常: 批量获取全市场价格失败: {e}", exc_info=True)
        return {}
    except Exception as e:
        logger.error(f"未知异常: 批量获取全市场价格失败: {e}", exc_info=True)
        return {}
