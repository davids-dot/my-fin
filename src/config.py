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

# 监控的股票池列表
SYMBOLS = os.getenv("SYMBOLS", "sh600519").split(",")
