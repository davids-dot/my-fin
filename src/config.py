import os
import logging
from dotenv import load_dotenv

load_dotenv()

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("my_fin")

# 通知服务配置
BARK_URL = os.getenv("BARK_URL", "")

# 数据库配置 (支持 sqlite 或 mysql)
# 例如切换 mysql: mysql+pymysql://user:pass@localhost:3306/db_name
# 使用绝对路径，确保 positions.db 生成在项目根目录
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "positions.db")
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = f"sqlite:///{DB_PATH}"

# 数据源提供商配置 (支持 'sina' 或 'em')
# sina: 新浪财经，速度快，抗封锁能力强，但缺少深度基本面字段 (市盈率、行业等为 NULL)
# em: 东方财富，包含深度基本面字段，但容易被代理或防火墙拦截 (报 RemoteDisconnected)
DATA_PROVIDER = os.getenv("DATA_PROVIDER", "sina").lower()

# 监控的股票池列表
SYMBOLS = os.getenv("SYMBOLS", "sh600519").split(",")

# 选股过滤阈值
MAX_PE = float(os.getenv("MAX_PE", "50.0"))           # 最大市盈率
MIN_MARKET_CAP = float(os.getenv("MIN_MARKET_CAP", "50.0")) # 最小市值 (亿元)
EXCLUDE_INDUSTRIES = os.getenv("EXCLUDE_INDUSTRIES", "银行,保险").split(",") # 排除的行业
