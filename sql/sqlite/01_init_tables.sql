-- 1. 股票基础信息表 (全市场 A 股列表)
CREATE TABLE IF NOT EXISTS stock_list (
    symbol VARCHAR(20) PRIMARY KEY,           -- 股票代码 (带前缀, 如 sh600519)
    name VARCHAR(50) NOT NULL,                -- 股票名称
    market VARCHAR(10),                       -- 所属市场 (sh/sz/bj)
    status VARCHAR(10) DEFAULT 'ACTIVE'       -- 状态
);

-- 2. 股票日线历史表 (存储原始不复权数据)
CREATE TABLE IF NOT EXISTS stock_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(20) NOT NULL,              -- 股票代码 (带前缀)
    trade_date DATE NOT NULL,                 -- 交易日期 (YYYY-MM-DD)
    open FLOAT,                               -- 开盘价 (原始)
    close FLOAT,                              -- 收盘价 (原始)
    high FLOAT,                               -- 最高价 (原始)
    low FLOAT,                                -- 最低价 (原始)
    volume BIGINT,                            -- 成交量 (手)
    amount FLOAT,                             -- 成交额 (元)
    UNIQUE(symbol, trade_date)                -- 联合唯一索引，防止重复插入
);

-- 为查询优化建立索引
CREATE INDEX IF NOT EXISTS idx_daily_trade_date ON stock_daily(trade_date);
CREATE INDEX IF NOT EXISTS idx_daily_symbol ON stock_daily(symbol);

-- 3. 持仓记录表 (当前正在监控/持有的标的)
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(20) NOT NULL UNIQUE,       -- 股票代码 (带前缀)
    buy_price FLOAT NOT NULL,                 -- 买入成本价
    buy_time DATETIME DEFAULT CURRENT_TIMESTAMP, -- 买入时间
    volume INTEGER NOT NULL,                  -- 持仓数量
    last_observed_price FLOAT                 -- 最后观察价格 (用于止盈)
);

-- 4. 明日监控池 (选股结果表)
CREATE TABLE IF NOT EXISTS watch_list (
    symbol VARCHAR(20) PRIMARY KEY,           -- 股票代码
    add_date DATE NOT NULL,                   -- 选入日期 (哪天收盘后选出的)
    target_buy_price FLOAT,                   -- 目标买入价 (即 T+1 收盘价，盘中需大于此价才买入)
    status VARCHAR(10) DEFAULT 'PENDING'      -- 状态: PENDING(待监控), BOUGHT(已买入), EXPIRED(过期作废)
);
