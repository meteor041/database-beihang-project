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