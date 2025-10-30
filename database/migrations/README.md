# 数据库迁移记录

本目录记录项目开发过程中的数据库结构变更。

## 执行顺序

| 编号 | 文件名 | 说明 | 执行时间 |
|------|--------|------|----------|
| 001 | 001_address_nullable.sql | 允许订单表的 address_id 为空，支持自取订单无需地址 | 2025-10-30 |

## 使用说明

### 新环境部署
1. 先执行 `database_schema.sql` 创建初始表结构
2. 按顺序执行 migrations 目录下的所有迁移脚本

### 执行迁移脚本
```bash
# 方式1: 使用 Python 后端执行
python3 -c "from backend.db import DatabaseManager; db = DatabaseManager(); db.execute_update(open('database/migrations/001_address_nullable.sql').read())"

# 方式2: 使用 mysql 命令行（需要 SSL 配置）
mysql -h <host> -u <username> -p --ssl-ca=pem/ca-bundle.pem <database> < database/migrations/001_address_nullable.sql
```

## 注意事项
- 每个迁移脚本只能执行一次
- 已执行的迁移不要重复执行
- 新成员加入项目需要执行所有迁移脚本
