from apscheduler.schedulers.blocking import BlockingScheduler
from state.db import init_db
from strategy.trend import run_intraday_monitor
from strategy.screener import run_daily_screener
from config import logger

def job_intraday():
    run_intraday_monitor()

def job_screener():
    run_daily_screener()

def main():
    # 1. 初始化数据库表结构 (基于 sql 文件)
    init_db()
    
    logger.info("==================================")
    logger.info("系统启动，初始化数据库完成...")
    logger.info("==================================")
    
    # 2. 启动定时任务
    scheduler = BlockingScheduler()
    
    # 任务A: 盘中实时监控 (每分钟执行一次)
    # 实际环境可以加上 day_of_week='mon-fri', hour='9-11,13-14', minute='*'
    scheduler.add_job(job_intraday, 'cron', minute='*', id='intraday_monitor')
    
    # 任务B: 盘后离线日线选股器 (每天 15:30 执行)
    # 实际环境可以加上 day_of_week='mon-fri'
    scheduler.add_job(job_screener, 'cron', hour=15, minute=30, id='daily_screener')
    
    try:
        logger.info("调度器已启动: [盘中监控(分钟频)] + [盘后选股(15:30)]")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("系统已退出")

if __name__ == "__main__":
    main()
