-- 校内二手物品交易平台数据库表结构
-- 使用华为云GaussDB(for MySQL)

-- 1. 用户表 (User)
CREATE TABLE user (
    user_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户唯一标识',
    student_id VARCHAR(20) NOT NULL UNIQUE COMMENT '学号',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码(加密存储)',
    real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
    phone VARCHAR(11) NOT NULL COMMENT '手机号',
    email VARCHAR(100) NOT NULL COMMENT '邮箱',
    avatar VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
    credit_score INT DEFAULT 100 COMMENT '信用评分',
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    last_login DATETIME DEFAULT NULL COMMENT '最后登录时间',
    status ENUM('active', 'frozen', 'deleted') DEFAULT 'active' COMMENT '账户状态',
    
    -- 约束
    CONSTRAINT chk_credit_score CHECK (credit_score >= 0 AND credit_score <= 100),
    CONSTRAINT chk_phone CHECK (phone REGEXP '^1[3-9][0-9]{9}$'),
    CONSTRAINT chk_email CHECK (email REGEXP '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 分类表 (Category)
CREATE TABLE category (
    category_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '分类唯一标识',
    category_name VARCHAR(50) NOT NULL COMMENT '分类名称',
    parent_category_id INT DEFAULT NULL COMMENT '父分类ID',
    description TEXT DEFAULT NULL COMMENT '分类描述',
    icon VARCHAR(255) DEFAULT NULL COMMENT '分类图标URL',
    sort_order INT DEFAULT 0 COMMENT '排序顺序',
    
    -- 外键约束
    FOREIGN KEY (parent_category_id) REFERENCES category(category_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品分类表';

-- 3. 商品表 (Item)
CREATE TABLE item (
    item_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '商品唯一标识',
    user_id INT NOT NULL COMMENT '发布用户ID',
    category_id INT NOT NULL COMMENT '商品分类ID',
    title VARCHAR(100) NOT NULL COMMENT '商品标题',
    description TEXT NOT NULL COMMENT '商品描述',
    price DECIMAL(10,2) NOT NULL COMMENT '价格',
    original_price DECIMAL(10,2) DEFAULT NULL COMMENT '原价',
    condition_level ENUM('brand_new', 'like_new', 'very_good', 'good', 'acceptable') NOT NULL COMMENT '新旧程度',
    images JSON DEFAULT NULL COMMENT '商品图片URLs(JSON数组)',
    location VARCHAR(100) NOT NULL COMMENT '交易地点',
    publish_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    status ENUM('available', 'sold', 'removed') DEFAULT 'available' COMMENT '商品状态',
    view_count INT DEFAULT 0 COMMENT '浏览次数',
    
    -- 约束
    CONSTRAINT chk_price CHECK (price > 0),
    CONSTRAINT chk_original_price CHECK (original_price IS NULL OR original_price >= price),
    CONSTRAINT chk_view_count CHECK (view_count >= 0),
    
    -- 外键约束
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES category(category_id) ON DELETE RESTRICT,
    
    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_category_id (category_id),
    INDEX idx_status (status),
    INDEX idx_publish_date (publish_date),
    FULLTEXT INDEX idx_title_desc (title, description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

-- 4. 地址表 (Address)
CREATE TABLE address (
    address_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '地址唯一标识',
    user_id INT NOT NULL COMMENT '用户ID',
    recipient_name VARCHAR(50) NOT NULL COMMENT '收件人姓名',
    phone VARCHAR(11) NOT NULL COMMENT '联系电话',
    province VARCHAR(20) NOT NULL COMMENT '省份',
    city VARCHAR(20) NOT NULL COMMENT '城市',
    district VARCHAR(20) NOT NULL COMMENT '区县',
    detailed_address VARCHAR(200) NOT NULL COMMENT '详细地址',
    postal_code VARCHAR(6) DEFAULT NULL COMMENT '邮政编码',
    is_default BOOLEAN DEFAULT FALSE COMMENT '是否默认地址',
    address_type ENUM('dormitory', 'home', 'other') DEFAULT 'dormitory' COMMENT '地址类型',
    
    -- 约束
    CONSTRAINT chk_phone_addr CHECK (phone REGEXP '^1[3-9][0-9]{9}$'),
    CONSTRAINT chk_postal_code CHECK (postal_code IS NULL OR postal_code REGEXP '^[0-9]{6}$'),
    
    -- 外键约束
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户地址表';

-- 5. 订单表 (Order)
CREATE TABLE `order` (
    order_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单唯一标识',
    order_number VARCHAR(32) NOT NULL UNIQUE COMMENT '订单编号',
    buyer_id INT NOT NULL COMMENT '买家用户ID',
    seller_id INT NOT NULL COMMENT '卖家用户ID',
    item_id INT NOT NULL COMMENT '商品ID',
    address_id INT DEFAULT NULL COMMENT '收货地址ID(自取时可为空)',
    total_amount DECIMAL(10,2) NOT NULL COMMENT '订单总金额',
    payment_method ENUM('alipay', 'wechat', 'cash') NOT NULL COMMENT '支付方式',
    payment_status ENUM('pending', 'paid', 'refunded') DEFAULT 'pending' COMMENT '支付状态',
    delivery_method ENUM('meet', 'express') NOT NULL COMMENT '交付方式',
    order_status ENUM('pending_payment', 'paid', 'shipped', 'completed', 'cancelled') DEFAULT 'pending_payment' COMMENT '订单状态',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    payment_time DATETIME DEFAULT NULL COMMENT '支付时间',
    ship_time DATETIME DEFAULT NULL COMMENT '发货时间',
    complete_time DATETIME DEFAULT NULL COMMENT '完成时间',
    notes TEXT DEFAULT NULL COMMENT '订单备注',
    
    -- 约束
    CONSTRAINT chk_total_amount CHECK (total_amount > 0),
    CONSTRAINT chk_buyer_seller CHECK (buyer_id != seller_id),
    
    -- 外键约束
    FOREIGN KEY (buyer_id) REFERENCES user(user_id) ON DELETE RESTRICT,
    FOREIGN KEY (seller_id) REFERENCES user(user_id) ON DELETE RESTRICT,
    FOREIGN KEY (item_id) REFERENCES item(item_id) ON DELETE RESTRICT,
    FOREIGN KEY (address_id) REFERENCES address(address_id) ON DELETE RESTRICT,
    
    -- 索引
    INDEX idx_buyer_id (buyer_id),
    INDEX idx_seller_id (seller_id),
    INDEX idx_item_id (item_id),
    INDEX idx_order_status (order_status),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- 6. 消息表 (Message)
CREATE TABLE message (
    message_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '消息唯一标识',
    sender_id INT NOT NULL COMMENT '发送者用户ID',
    receiver_id INT NOT NULL COMMENT '接收者用户ID',
    item_id INT NOT NULL COMMENT '相关商品ID',
    content TEXT NOT NULL COMMENT '消息内容',
    message_type ENUM('text', 'image') DEFAULT 'text' COMMENT '消息类型',
    send_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    is_read BOOLEAN DEFAULT FALSE COMMENT '是否已读',
    is_withdrawn BOOLEAN DEFAULT FALSE COMMENT '是否已撤回',
    reply_to INT DEFAULT NULL COMMENT '回复的消息ID',

    -- 约束
    CONSTRAINT chk_sender_receiver CHECK (sender_id != receiver_id),

    -- 外键约束
    FOREIGN KEY (sender_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES item(item_id) ON DELETE CASCADE,
    FOREIGN KEY (reply_to) REFERENCES message(message_id) ON DELETE SET NULL,

    -- 索引
    INDEX idx_sender_id (sender_id),
    INDEX idx_receiver_id (receiver_id),
    INDEX idx_item_id (item_id),
    INDEX idx_send_time (send_time),
    INDEX idx_conversation (sender_id, receiver_id, item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消息表';

-- 7. 收藏表 (Wishlist) - 多对多关系表
CREATE TABLE wishlist (
    wishlist_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '收藏记录唯一标识',
    user_id INT NOT NULL COMMENT '用户ID',
    item_id INT NOT NULL COMMENT '商品ID',
    add_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    notes VARCHAR(200) DEFAULT NULL COMMENT '收藏备注',
    
    -- 外键约束
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES item(item_id) ON DELETE CASCADE,
    
    -- 唯一约束(防止重复收藏)
    UNIQUE KEY uk_user_item (user_id, item_id),
    
    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_item_id (item_id),
    INDEX idx_add_time (add_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户收藏表';

-- 8. 评价表 (Review) - 补充实体，用于交易后评价
CREATE TABLE review (
    review_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '评价唯一标识',
    order_id INT NOT NULL COMMENT '订单ID',
    reviewer_id INT NOT NULL COMMENT '评价者用户ID',
    reviewee_id INT NOT NULL COMMENT '被评价者用户ID',
    rating INT NOT NULL COMMENT '评分(1-5)',
    content TEXT DEFAULT NULL COMMENT '评价内容',
    review_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '评价时间',
    
    -- 约束
    CONSTRAINT chk_rating CHECK (rating >= 1 AND rating <= 5),
    CONSTRAINT chk_reviewer_reviewee CHECK (reviewer_id != reviewee_id),
    
    -- 外键约束
    FOREIGN KEY (order_id) REFERENCES `order`(order_id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (reviewee_id) REFERENCES user(user_id) ON DELETE CASCADE,
    
    -- 唯一约束(每个订单每个用户只能评价一次)
    UNIQUE KEY uk_order_reviewer (order_id, reviewer_id),
    
    -- 索引
    INDEX idx_reviewee_id (reviewee_id),
    INDEX idx_review_time (review_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交易评价表';

-- 插入基础分类数据
INSERT INTO category (category_name, parent_category_id, description, sort_order) VALUES
('教材书籍', NULL, '各类教材和学习用书', 1),
('电子产品', NULL, '手机、电脑、数码设备等', 2),
('生活用品', NULL, '日常生活所需用品', 3),
('服装配饰', NULL, '衣服、鞋子、包包等', 4),
('运动器材', NULL, '健身器材、球类用品等', 5),
('其他', NULL, '其他类别商品', 6);

-- 插入二级分类
INSERT INTO category (category_name, parent_category_id, description, sort_order) VALUES
('专业课教材', 1, '各专业课程教材', 1),
('公共课教材', 1, '公共基础课教材', 2),
('课外读物', 1, '小说、杂志等课外书籍', 3),
('手机', 2, '智能手机及配件', 1),
('电脑', 2, '笔记本电脑、台式机等', 2),
('数码配件', 2, '耳机、充电器、数据线等', 3);

-- ============================================
-- 存储过程 (Stored Procedures)
-- ============================================

-- 存储过程1: 完成订单
-- 功能: 将订单状态改为completed，并给买卖双方各加5分信用分
DELIMITER //
CREATE PROCEDURE sp_complete_order(IN p_order_id INT)
BEGIN
    DECLARE v_buyer_id INT;
    DECLARE v_seller_id INT;
    DECLARE v_current_status VARCHAR(20);

    -- 获取订单信息
    SELECT buyer_id, seller_id, order_status
    INTO v_buyer_id, v_seller_id, v_current_status
    FROM `order` WHERE order_id = p_order_id;

    -- 检查订单状态是否为shipped（只有已发货的订单才能完成）
    IF v_current_status != 'shipped' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '只有已发货的订单才能确认收货';
    END IF;

    -- 更新订单状态为已完成
    UPDATE `order`
    SET order_status = 'completed', complete_time = NOW()
    WHERE order_id = p_order_id;

    -- 给买家加5分信用分（不超过100）
    UPDATE user
    SET credit_score = LEAST(100, credit_score + 5)
    WHERE user_id = v_buyer_id;

    -- 给卖家加5分信用分（不超过100）
    UPDATE user
    SET credit_score = LEAST(100, credit_score + 5)
    WHERE user_id = v_seller_id;
END //
DELIMITER ;

-- 存储过程2: 取消订单
-- 功能: 取消订单并将商品状态恢复为available
DELIMITER //
CREATE PROCEDURE sp_cancel_order(IN p_order_id INT)
BEGIN
    DECLARE v_item_id INT;
    DECLARE v_current_status VARCHAR(20);

    -- 获取订单信息
    SELECT item_id, order_status
    INTO v_item_id, v_current_status
    FROM `order` WHERE order_id = p_order_id;

    -- 检查订单状态（已完成的订单不能取消）
    IF v_current_status = 'completed' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '已完成的订单无法取消';
    END IF;

    -- 更新订单状态为已取消
    UPDATE `order`
    SET order_status = 'cancelled'
    WHERE order_id = p_order_id;

    -- 恢复商品状态为可购买
    UPDATE item
    SET status = 'available'
    WHERE item_id = v_item_id;
END //
DELIMITER ;

-- 存储过程3: 获取用户统计信息
-- 功能: 返回用户的商品数、订单数、收藏数等统计信息
DELIMITER //
CREATE PROCEDURE sp_get_user_statistics(IN p_user_id INT)
BEGIN
    SELECT
        (SELECT COUNT(*) FROM item WHERE user_id = p_user_id AND status = 'available') AS active_items,
        (SELECT COUNT(*) FROM item WHERE user_id = p_user_id AND status = 'sold') AS sold_items,
        (SELECT COUNT(*) FROM `order` WHERE buyer_id = p_user_id) AS buy_orders,
        (SELECT COUNT(*) FROM `order` WHERE seller_id = p_user_id) AS sell_orders,
        (SELECT COUNT(*) FROM wishlist WHERE user_id = p_user_id) AS wishlist_count,
        (SELECT AVG(rating) FROM review WHERE reviewee_id = p_user_id) AS avg_rating;
END //
DELIMITER ;

-- 存储过程4: 批量标记消息已读
-- 功能: 将某个会话中的所有未读消息标记为已读
DELIMITER //
CREATE PROCEDURE sp_mark_messages_read(
    IN p_user_id INT,
    IN p_other_user_id INT,
    IN p_item_id INT
)
BEGIN
    UPDATE message
    SET is_read = TRUE
    WHERE receiver_id = p_user_id
      AND sender_id = p_other_user_id
      AND item_id = p_item_id
      AND is_read = FALSE;
END //
DELIMITER ;

-- ============================================
-- 触发器 (Triggers)
-- ============================================

-- 触发器1: 订单创建后自动更新商品状态为sold
DELIMITER //
CREATE TRIGGER trg_after_order_insert
AFTER INSERT ON `order`
FOR EACH ROW
BEGIN
    UPDATE item
    SET status = 'sold'
    WHERE item_id = NEW.item_id;
END //
DELIMITER ;

-- 触发器2: 订单取消后自动恢复商品状态为available
DELIMITER //
CREATE TRIGGER trg_after_order_cancel
AFTER UPDATE ON `order`
FOR EACH ROW
BEGIN
    -- 当订单状态从非cancelled变为cancelled时，恢复商品状态
    IF OLD.order_status != 'cancelled' AND NEW.order_status = 'cancelled' THEN
        UPDATE item
        SET status = 'available'
        WHERE item_id = NEW.item_id;
    END IF;
END //
DELIMITER ;

-- 触发器3: 评价创建后自动更新被评价者信用分
DELIMITER //
CREATE TRIGGER trg_after_review_insert
AFTER INSERT ON review
FOR EACH ROW
BEGIN
    DECLARE v_credit_change INT;

    -- 根据评分计算信用分变化
    SET v_credit_change = CASE NEW.rating
        WHEN 5 THEN 3   -- 5星好评 +3分
        WHEN 4 THEN 1   -- 4星好评 +1分
        WHEN 3 THEN 0   -- 3星中评 不变
        WHEN 2 THEN -2  -- 2星差评 -2分
        WHEN 1 THEN -5  -- 1星差评 -5分
        ELSE 0
    END;

    -- 更新被评价者的信用分（保持在0-100范围内）
    UPDATE user
    SET credit_score = LEAST(100, GREATEST(0, credit_score + v_credit_change))
    WHERE user_id = NEW.reviewee_id;
END //
DELIMITER ;

-- 触发器4: 用户注册时自动设置初始信用分
-- (虽然有DEFAULT值，但触发器可以处理更复杂的初始化逻辑)
DELIMITER //
CREATE TRIGGER trg_before_user_insert
BEFORE INSERT ON user
FOR EACH ROW
BEGIN
    -- 确保新用户信用分为100
    IF NEW.credit_score IS NULL THEN
        SET NEW.credit_score = 100;
    END IF;

    -- 设置注册时间
    IF NEW.registration_date IS NULL THEN
        SET NEW.registration_date = NOW();
    END IF;
END //
DELIMITER ;

-- 触发器5: 地址设为默认时，自动取消其他默认地址
DELIMITER //
CREATE TRIGGER trg_before_address_update
BEFORE UPDATE ON address
FOR EACH ROW
BEGIN
    -- 如果将地址设为默认，取消该用户其他地址的默认状态
    IF NEW.is_default = TRUE AND OLD.is_default = FALSE THEN
        UPDATE address
        SET is_default = FALSE
        WHERE user_id = NEW.user_id AND address_id != NEW.address_id;
    END IF;
END //
DELIMITER ;

-- ============================================
-- 推荐索引 (建议添加以提升查询性能)
-- ============================================

-- 优化未读消息查询
ALTER TABLE message ADD INDEX idx_receiver_unread (receiver_id, is_read);

-- 优化订单状态+时间组合查询
ALTER TABLE `order` ADD INDEX idx_status_time (order_status, create_time);

-- 优化评价统计查询
ALTER TABLE review ADD INDEX idx_reviewee_rating (reviewee_id, rating);