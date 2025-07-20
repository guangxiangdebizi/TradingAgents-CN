// MongoDB 副本集初始化脚本

print('🔧 初始化 MongoDB 副本集...');

// 配置副本集
var config = {
  "_id": "rs0",
  "members": [
    {
      "_id": 0,
      "host": "mongo1:27017",
      "priority": 2
    },
    {
      "_id": 1,
      "host": "mongo2:27017",
      "priority": 1
    },
    {
      "_id": 2,
      "host": "mongo3:27017",
      "priority": 1
    }
  ]
};

// 初始化副本集
try {
  rs.initiate(config);
  print('✅ 副本集初始化成功');
} catch (e) {
  print('⚠️ 副本集可能已经初始化: ' + e);
}

// 等待副本集稳定
sleep(5000);

// 检查副本集状态
var status = rs.status();
print('📊 副本集状态: ' + status.ok);

// 切换到主节点
var primary = db.hello().primary;
print('🎯 主节点: ' + primary);

// 创建应用数据库和用户
db = db.getSiblingDB('tradingagents');

try {
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
} catch (e) {
  print('⚠️ 用户可能已存在: ' + e);
}

print('🎉 MongoDB 集群配置完成！');
