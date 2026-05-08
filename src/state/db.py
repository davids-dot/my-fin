from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL, logger
import os

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    初始化数据库表结构
    直接读取 sql/sqlite/01_init_tables.sql 执行，不依赖 SQLAlchemy 的 create_all()
    """
    sql_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "sql", "sqlite", "01_init_tables.sql"
    )
    
    if not os.path.exists(sql_file_path):
        logger.error(f"SQL初始化文件不存在: {sql_file_path}")
        return
        
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        # SQLite 支持通过 execute 运行多个由分号分隔的语句，但为了安全我们分句执行
        with engine.begin() as conn:
            for statement in sql_script.split(';'):
                if statement.strip():
                    conn.execute(text(statement))
        logger.info("数据库表结构初始化成功 (基于 01_init_tables.sql)")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}", exc_info=True)

def get_session():
    return SessionLocal()
