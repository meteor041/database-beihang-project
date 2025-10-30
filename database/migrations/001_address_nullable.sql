-- 数据库迁移脚本: 允许订单表的 address_id 为空
-- 用途: 支持自取订单无需填写收货地址
-- 执行时间: 2025-10-30

-- 1. 删除原有外键约束
ALTER TABLE `order` DROP FOREIGN KEY `order_ibfk_4`;

-- 2. 修改 address_id 字段为可空
ALTER TABLE `order` MODIFY COLUMN address_id INT DEFAULT NULL COMMENT '收货地址ID(自取时可为空)';

-- 3. 重新添加外键约束（支持 NULL）
ALTER TABLE `order`
ADD CONSTRAINT `order_ibfk_4`
FOREIGN KEY (address_id) REFERENCES address(address_id) ON DELETE RESTRICT;

-- 验证修改
DESCRIBE `order`;
