from apscheduler.schedulers.blocking import BlockingScheduler
from my_fin.state.db import init_db
from my_fin.strategy.trend import run_strategy
from my_fin.config import SYMBOLS
from datetime import datetime

def job():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行分钟级策略监控...")
    for symbol in SYMBOLS:
        run_strategy(symbol)

def main():
    # 1. 初始化数据库表结构
    init_db()
    
    print("==================================")
    print("系统启动，初始化数据库完成...")
    print(f"当前监控标的: {SYMBOLS}")
    print("==================================")
    
    # 2. 启动定时任务 (分钟频)
    scheduler = BlockingScheduler()
    # 设定为每分钟执行一次，生产环境可结合工作日及交易时间(如 09:30-11:30, 13:00-15:00)进行 cron 表达式优化
    scheduler.add_job(job, 'cron', minute='*')
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n系统已退出")

if __name__ == "__main__":
    main()
