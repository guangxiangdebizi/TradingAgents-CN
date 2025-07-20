-- ClickHouse 初始化脚本
-- 创建股票历史数据表

-- 创建数据库
CREATE DATABASE IF NOT EXISTS tradingagents;

-- 使用数据库
USE tradingagents;

-- 股票基本信息表
CREATE TABLE IF NOT EXISTS stock_info (
    symbol String,
    name String,
    market String,
    industry Nullable(String),
    sector Nullable(String),
    list_date Nullable(Date),
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY symbol;

-- 股票日线数据表（主要存储表）
CREATE TABLE IF NOT EXISTS stock_daily (
    symbol String,
    trade_date Date,
    open Decimal(10, 2),
    high Decimal(10, 2),
    low Decimal(10, 2),
    close Decimal(10, 2),
    volume UInt64,
    amount Decimal(15, 2),
    turnover_rate Nullable(Decimal(8, 4)),
    pe_ratio Nullable(Decimal(8, 2)),
    pb_ratio Nullable(Decimal(8, 2)),
    market_cap Nullable(Decimal(15, 2)),
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date);

-- 股票分钟数据表（实时数据）
CREATE TABLE IF NOT EXISTS stock_minute (
    symbol String,
    datetime DateTime,
    open Decimal(10, 2),
    high Decimal(10, 2),
    low Decimal(10, 2),
    close Decimal(10, 2),
    volume UInt64,
    amount Decimal(15, 2),
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(datetime)
ORDER BY (symbol, datetime)
TTL datetime + INTERVAL 30 DAY; -- 30天后自动删除

-- 技术指标表
CREATE TABLE IF NOT EXISTS stock_indicators (
    symbol String,
    trade_date Date,
    ma5 Nullable(Decimal(10, 2)),
    ma10 Nullable(Decimal(10, 2)),
    ma20 Nullable(Decimal(10, 2)),
    ma60 Nullable(Decimal(10, 2)),
    macd Nullable(Decimal(8, 4)),
    macd_signal Nullable(Decimal(8, 4)),
    macd_hist Nullable(Decimal(8, 4)),
    rsi Nullable(Decimal(6, 2)),
    kdj_k Nullable(Decimal(6, 2)),
    kdj_d Nullable(Decimal(6, 2)),
    kdj_j Nullable(Decimal(6, 2)),
    created_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(created_at)
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date);

-- 财务数据表
CREATE TABLE IF NOT EXISTS stock_financials (
    symbol String,
    report_date Date,
    report_type String, -- 'Q1', 'Q2', 'Q3', 'annual'
    revenue Nullable(Decimal(15, 2)),
    net_income Nullable(Decimal(15, 2)),
    total_assets Nullable(Decimal(15, 2)),
    total_equity Nullable(Decimal(15, 2)),
    roe Nullable(Decimal(8, 4)),
    roa Nullable(Decimal(8, 4)),
    debt_ratio Nullable(Decimal(8, 4)),
    eps Nullable(Decimal(8, 2)),
    bps Nullable(Decimal(8, 2)),
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (symbol, report_date, report_type);

-- 市场指数表
CREATE TABLE IF NOT EXISTS market_index (
    index_code String,
    index_name String,
    trade_date Date,
    open Decimal(10, 2),
    high Decimal(10, 2),
    low Decimal(10, 2),
    close Decimal(10, 2),
    volume UInt64,
    amount Decimal(15, 2),
    change_pct Decimal(8, 4),
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(trade_date)
ORDER BY (index_code, trade_date);

-- 创建物化视图用于快速查询
-- 最新价格视图
CREATE MATERIALIZED VIEW IF NOT EXISTS stock_latest_price
ENGINE = ReplacingMergeTree(trade_date)
ORDER BY symbol
AS SELECT
    symbol,
    argMax(close, trade_date) as latest_price,
    argMax(trade_date, trade_date) as trade_date,
    argMax(volume, trade_date) as volume,
    argMax(amount, trade_date) as amount
FROM stock_daily
GROUP BY symbol;

-- 月度统计视图
CREATE MATERIALIZED VIEW IF NOT EXISTS stock_monthly_stats
ENGINE = SummingMergeTree()
ORDER BY (symbol, month)
AS SELECT
    symbol,
    toYYYYMM(trade_date) as month,
    max(high) as month_high,
    min(low) as month_low,
    argMax(close, trade_date) as month_close,
    sum(volume) as total_volume,
    sum(amount) as total_amount
FROM stock_daily
GROUP BY symbol, toYYYYMM(trade_date);

-- 创建索引以提高查询性能
-- 注意：ClickHouse 主要依靠 ORDER BY 来优化查询，不需要额外的索引

-- 插入一些示例数据
INSERT INTO stock_info VALUES 
('000001', '平安银行', 'A股', '银行', '金融', '1991-04-03', now(), now()),
('000002', '万科A', 'A股', '房地产', '房地产', '1991-01-29', now(), now()),
('600519', '贵州茅台', 'A股', '白酒', '食品饮料', '2001-08-27', now(), now());

-- 创建用户和权限
CREATE USER IF NOT EXISTS 'tradingagents'@'%' IDENTIFIED BY 'tradingagents123';
GRANT ALL ON tradingagents.* TO 'tradingagents'@'%';
