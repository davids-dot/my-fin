from apscheduler.schedulers.blocking import BlockingScheduler
from state.db import init_db
from strategy.trend import run_strategy
from config import SYMBOLS, logger

def job():
    logger.info("开始执行分钟级策略监控...")
    for symbol in SYMBOLS:
        run_strategy(symbol)

def main():
    # 1. 初始化数据库表结构
    init_db()
    
    logger.info("==================================")
    logger.info("系统启动，初始化数据库完成...")
    logger.info(f"当前监控标的: {SYMBOLS}")
    logger.info("==================================")
    
    # 2. 启动定时任务 (分钟频)
    scheduler = BlockingScheduler()
    # 设定为每分钟执行一次，生产环境可结合工作日及交易时间(如 09:30-11:30, 13:00-15:00)进行 cron 表达式优化
    scheduler.add_job(job, 'cron', minute='*')
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("系统已退出")

if __name__ == "__main__":
    main()
