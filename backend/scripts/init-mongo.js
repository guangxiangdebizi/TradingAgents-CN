// MongoDB 初始化脚本
// 创建数据库、集合和索引

// 切换到 tradingagents 数据库
db = db.getSiblingDB('tradingagents');

// 创建应用用户
db.createUser({
  user: 'tradingagents',
  pwd: 'tradingagents123',
  roles: [
    {
      role: 'readWrite',
      db: 'tradingagents'
    }
  ]
});

print('✅ 创建应用用户成功');

// ==================== 股票基础信息集合 ====================
db.createCollection('stock_info');

// 创建索引
db.stock_info.createIndex({ "symbol": 1 }, { unique: true });
db.stock_info.createIndex({ "market": 1 });
db.stock_info.createIndex({ "industry": 1 });
db.stock_info.createIndex({ "name": "text" }); // 全文搜索

print('✅ 创建 stock_info 集合和索引');

// ==================== 股票历史数据集合（时序集合）====================
// 使用 MongoDB 5.0+ 的时序集合特性
db.createCollection('stock_daily', {
  timeseries: {
    timeField: 'trade_date',
    metaField: 'symbol',
    granularity: 'hours'
  }
});

// 创建索引
db.stock_daily.createIndex({ "symbol": 1, "trade_date": 1 });
db.stock_daily.createIndex({ "trade_date": 1 });
db.stock_daily.createIndex({ "symbol": 1, "trade_date": -1 }); // 最新数据优先

print('✅ 创建 stock_daily 时序集合和索引');

// ==================== 股票分钟数据集合 ====================
db.createCollection('stock_minute', {
  timeseries: {
    timeField: 'datetime',
    metaField: 'symbol',
    granularity: 'minutes'
  }
});

// 创建索引和TTL（30天后自动删除）
db.stock_minute.createIndex({ "datetime": 1 }, { expireAfterSeconds: 2592000 }); // 30天
db.stock_minute.createIndex({ "symbol": 1, "datetime": 1 });

print('✅ 创建 stock_minute 时序集合和索引');

// ==================== 财务数据集合 ====================
db.createCollection('stock_financials');

// 创建索引
db.stock_financials.createIndex({ "symbol": 1, "report_date": 1, "report_type": 1 }, { unique: true });
db.stock_financials.createIndex({ "report_date": 1 });

print('✅ 创建 stock_financials 集合和索引');

// ==================== 分析结果集合 ====================
db.createCollection('analysis_results');

// 创建索引
db.analysis_results.createIndex({ "analysis_id": 1 }, { unique: true });
db.analysis_results.createIndex({ "stock_code": 1, "created_at": -1 });
db.analysis_results.createIndex({ "created_at": 1 }, { expireAfterSeconds: 7776000 }); // 90天后删除

print('✅ 创建 analysis_results 集合和索引');

// ==================== 分析进度集合 ====================
db.createCollection('analysis_progress');

// 创建索引和TTL
db.analysis_progress.createIndex({ "analysis_id": 1 }, { unique: true });
db.analysis_progress.createIndex({ "created_at": 1 }, { expireAfterSeconds: 86400 }); // 24小时后删除

print('✅ 创建 analysis_progress 集合和索引');

// ==================== 用户配置集合 ====================
db.createCollection('user_configs');

// 创建索引
db.user_configs.createIndex({ "user_id": 1 }, { unique: true });

print('✅ 创建 user_configs 集合和索引');

// ==================== 系统配置集合 ====================
db.createCollection('system_configs');

// 创建索引
db.system_configs.createIndex({ "config_key": 1 }, { unique: true });

print('✅ 创建 system_configs 集合和索引');

// ==================== 插入示例数据 ====================

// 插入股票基础信息
db.stock_info.insertMany([
  {
    symbol: '000001',
    name: '平安银行',
    market: 'A股',
    industry: '银行',
    sector: '金融',
    list_date: new Date('1991-04-03'),
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    symbol: '000002',
    name: '万科A',
    market: 'A股',
    industry: '房地产',
    sector: '房地产',
    list_date: new Date('1991-01-29'),
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    symbol: '600519',
    name: '贵州茅台',
    market: 'A股',
    industry: '白酒',
    sector: '食品饮料',
    list_date: new Date('2001-08-27'),
    created_at: new Date(),
    updated_at: new Date()
  }
]);

print('✅ 插入示例股票信息');

// 插入系统配置
db.system_configs.insertMany([
  {
    config_key: 'data_retention_days',
    config_value: 90,
    description: '数据保留天数',
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    config_key: 'cache_ttl_seconds',
    config_value: 1800,
    description: '缓存过期时间（秒）',
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    config_key: 'max_analysis_concurrent',
    config_value: 5,
    description: '最大并发分析任务数',
    created_at: new Date(),
    updated_at: new Date()
  }
]);

print('✅ 插入系统配置');

// ==================== 创建视图（用于复杂查询）====================

// 最新股价视图
db.createView('stock_latest_prices', 'stock_daily', [
  {
    $sort: { symbol: 1, trade_date: -1 }
  },
  {
    $group: {
      _id: '$symbol',
      latest_price: { $first: '$close' },
      trade_date: { $first: '$trade_date' },
      change: { $first: { $subtract: ['$close', '$open'] } },
      change_pct: { $first: { $multiply: [{ $divide: [{ $subtract: ['$close', '$open'] }, '$open'] }, 100] } },
      volume: { $first: '$volume' }
    }
  },
  {
    $lookup: {
      from: 'stock_info',
      localField: '_id',
      foreignField: 'symbol',
      as: 'info'
    }
  },
  {
    $unwind: '$info'
  },
  {
    $project: {
      symbol: '$_id',
      name: '$info.name',
      market: '$info.market',
      latest_price: 1,
      trade_date: 1,
      change: 1,
      change_pct: 1,
      volume: 1
    }
  }
]);

print('✅ 创建 stock_latest_prices 视图');

// ==================== 分片配置（生产环境）====================
// 注意：这部分在单机环境下不会执行，仅作为参考

/*
// 启用分片
sh.enableSharding('tradingagents');

// 为股票日线数据创建分片键
sh.shardCollection('tradingagents.stock_daily', { symbol: 1, trade_date: 1 });

// 为分析结果创建分片键
sh.shardCollection('tradingagents.analysis_results', { stock_code: 1, created_at: 1 });

print('✅ 配置分片策略');
*/

print('🎉 MongoDB 初始化完成！');
print('📊 数据库: tradingagents');
print('👤 用户: tradingagents');
print('🔑 密码: tradingagents123');
print('📝 集合数量: ' + db.getCollectionNames().length);
