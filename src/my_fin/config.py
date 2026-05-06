import os
from dotenv import load_dotenv

load_dotenv()

# 通知服务配置
BARK_URL = os.getenv("BARK_URL", "")

# 数据库配置 (支持 sqlite 或 mysql)
# 例如切换 mysql: mysql+pymysql://user:pass@localhost:3306/db_name
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///positions.db")

# 监控的股票池列表
SYMBOLS = os.getenv("SYMBOLS", "sh600519").split(",")
