# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**校内二手物品交易平台** (Campus Second-hand Trading Platform) - A full-stack database application project for Beihang University's Database Systems course. This system manages 7 entities (users, items, orders, messages, wishlist, addresses, categories) with complete CRUD operations using native SQL.

**Tech Stack:**
- **Frontend**: Vue 3.5.22 + TypeScript 5.9 + Vite 7.1.7 + Pinia 3.0.3 + Element Plus 2.11.5
- **Backend**: Python Flask with raw SQL (no ORM allowed)
- **Database**: Huawei Cloud GaussDB (MySQL-compatible) with SSL/TLS connection
- **Node Version**: ^20.19.0 || >=22.12.0

**Academic Constraints:**
- **CRITICAL**: ALL database operations MUST use raw SQL queries (no ORM abstractions)
- Parameterized queries required (`%s` placeholders, never string concatenation)
- Stored procedures and triggers MUST be implemented in raw SQL
- This is a 2-person team project (肖一涵、刘鑫宇)

## Project Structure

```
.
├── backend/                 # Main Flask backend (active, runs on port 5001)
│   ├── app.py              # Flask app entry point with 6 blueprint registrations
│   ├── db.py               # DatabaseManager class (87 lines) - connection pool & raw SQL
│   └── routes/             # API route blueprints (6 modules, 47 total endpoints)
│       ├── user_routes.py      # User management - 7 endpoints
│       ├── item_routes.py      # Item management - 8 endpoints
│       ├── order_routes.py     # Transaction management - 7 endpoints
│       ├── message_routes.py   # Messaging system - 8 endpoints
│       ├── wishlist_routes.py  # Wishlist management - 8 endpoints
│       └── address_routes.py   # Address management - 9 endpoints
├── backend-new/            # Alternative backend structure (experimental, NOT active)
├── frontend-vue/           # Vue 3 SPA (runs on port 5173)
│   ├── src/
│   │   ├── views/          # 14 page components (Home, ItemDetail, Orders, Messages, etc.)
│   │   ├── components/     # Reusable components (ItemCard, UserAvatar, OrderStatus, etc.)
│   │   ├── stores/         # Pinia stores (user authentication state)
│   │   ├── router/         # Vue Router with auth guards
│   │   ├── api/            # Axios client with 6 API modules
│   │   └── types/          # TypeScript interfaces
│   ├── package.json        # Frontend dependencies and scripts
│   ├── vite.config.ts      # Vite configuration
│   └── tsconfig.json       # TypeScript configuration
├── database/
│   └── database_schema.sql # Complete DDL (7 tables, constraints, indexes)
├── docs/                   # Project documentation (Chinese)
│   ├── 功能模块定义.md      # Functional requirements (6 modules)
│   ├── 前端设计文档.md      # Frontend design specs
│   ├── 数据流图.md          # Data flow diagrams (DFD 0-2 layers)
│   ├── 作业目标.md          # Course assignment specifications
│   └── ER图.pdf/png        # Entity-Relationship diagrams
├── test/
│   └── try_api.py          # API integration testing script
├── pem/
│   └── ca-bundle.pem       # SSL certificate for GaussDB connection
├── config.ini              # Database credentials (gitignored, DO NOT COMMIT)
└── config.ini.example      # Config template (safe to commit)
```

## Common Commands

### Frontend Development
```bash
cd frontend-vue
npm install                  # Install dependencies (first time only)
npm run dev                  # Start dev server at http://localhost:5173
npm run build                # Production build with type checking
npm run type-check           # TypeScript type checking only
npm run lint                 # ESLint with auto-fix
npm run format               # Prettier code formatting
npm run test:unit            # Run Vitest unit tests
npm run test:e2e             # Run Playwright E2E tests
```

### Backend Development
```bash
cd backend

# Install dependencies (no requirements.txt provided)
pip3 install flask flask-cors pymysql

# Start Flask server
python3 app.py               # Runs on http://localhost:5001

# You'll see:
# API文档: http://localhost:5001/
# 健康检查: http://localhost:5001/api/health
```

### Database Setup
1. **Copy config template**:
   ```bash
   cp config.ini.example config.ini
   ```
2. **Edit config.ini** with your GaussDB credentials:
   - Host, port, database name
   - Username and password
   - SSL ca_file path (default: `pem/ca-bundle.pem`)
3. **Execute schema**:
   - Connect to GaussDB
   - Run `database/database_schema.sql` to create all tables

### Testing
```bash
# Test backend API
cd test
python3 try_api.py

# Test specific frontend component
cd frontend-vue
npm run test:unit -- <test-file-name>

# Debug E2E tests
npm run test:e2e -- --debug
```

## Architecture & Key Design Patterns

### Backend Architecture (Flask + Raw SQL)

**Database Manager Pattern** ([backend/db.py](backend/db.py)):
```python
class DatabaseManager:
    # Connection management with context managers
    @contextmanager
    def get_connection(self):
        # Creates PyMySQL connection with SSL config
        # Auto-commits on success, rolls back on error
        # Always closes connection in finally block

    # Three execution methods for raw SQL:
    def execute_query(sql, params):    # SELECT → returns list of dicts
    def execute_update(sql, params):   # UPDATE/DELETE → returns row count
    def execute_insert(sql, params):   # INSERT → returns last insert ID

    # Utility methods:
    @staticmethod
    def hash_password(password):        # SHA256 password hashing
    @staticmethod
    def generate_order_number():        # UUID-based 32-char order number
```

**Key Features**:
- **Connection Pooling**: Context managers ensure proper cleanup
- **SSL/TLS Security**: Certificate-based encryption to GaussDB
- **DictCursor**: Results returned as `[{col: val}, ...]` for easy JSON serialization
- **Charset**: UTF-8 MB4 for full Unicode support (emojis, etc.)
- **Parameterized Queries**: All SQL uses `%s` placeholders to prevent injection

**Blueprint-based Routes** ([backend/app.py](backend/app.py:29-34)):
- All routes organized into 6 blueprints with `/api/<resource>` prefix
- CORS enabled for `localhost:5173` (Vite) and `localhost:3001` (backup)
- Health check endpoint: `GET /api/health` (tests DB connection)
- Server runs on port **5001** (not 5000!)

**Raw SQL Enforcement Example**:
```python
# ✅ CORRECT - Raw SQL with parameterized queries
sql = "SELECT * FROM user WHERE user_id = %s"
result = db_manager.execute_query(sql, (user_id,))

# ❌ WRONG - ORM methods are NOT allowed per course requirements
user = User.objects.filter(user_id=user_id)  # PROHIBITED

# ❌ WRONG - String concatenation creates SQL injection risk
sql = f"SELECT * FROM user WHERE user_id = {user_id}"  # NEVER DO THIS
```

### Frontend Architecture (Vue 3 Composition API)

**UI Layout - Modern Sidebar Navigation (YouTube/Twitter Style)**:
- **Collapsible Left Sidebar** - Hover to expand, auto-collapse when mouse leaves
  - Width: 72px (collapsed) → 240px (expanded)
  - Smooth cubic-bezier transitions (0.3s)
  - Fixed position with overflow handling
- **Main Navigation Items**:
  1. 首页 (Home) - `/`
  2. 商品列表 (Items) - `/items`
  3. 消息 (Messages) - `/messages` (登录后显示，带未读徽章)
  4. 个人中心 (Profile) - `/profile` (登录后显示，整合订单、收藏、地址、商品管理)

**14 Core Pages** ([frontend-vue/src/views/](frontend-vue/src/views/)):
1. **HomeView.vue** (`/`) - Item grid with infinite scroll
2. **ItemsView.vue** (`/items`) - Search with multi-filter sidebar
3. **ItemDetailView.vue** (`/item/:id`) - Full item info, seller card, recommendations
4. **ItemEditView.vue** (`/item/:id/edit`) - Item editing interface
5. **PublishView.vue** (`/publish`) - Item creation with image upload (max 9 images)
6. **CheckoutView.vue** (`/checkout`) - Order confirmation, address/payment selection
7. **OrdersView.vue** (`/orders`) - ⚠️ 已整合到个人中心，保留路由以向后兼容
8. **OrderDetailView.vue** (`/order/:id`) - Order timeline, logistics tracking
9. **MessagesView.vue** (`/messages`) - Split-pane chat interface
10. **WishlistView.vue** (`/wishlist`) - ⚠️ 已整合到个人中心，保留路由以向后兼容
11. **ProfileView.vue** (`/profile`) - **重构** 整合型用户中心，包含5个Tab:
    - 基本信息 - 用户资料编辑
    - 我的商品 - 在售/已售出/已下架商品管理
    - 我的订单 - 买家订单/卖家订单分类显示
    - 我的收藏 - 收藏商品列表
    - 地址管理 - 收货地址CRUD
12. **LoginView.vue** (`/login`) - Multi-method login (username/student_id/phone)
13. **RegisterView.vue** (`/register`) - Student registration with validation
14. **AboutView.vue** (`/about`) - Static info page

**Key Components**:
- **Sidebar.vue** - 可展开侧边栏导航组件（新增）
  - 鼠标悬停展开机制
  - 用户信息展示（头像、用户名、信用分）
  - 未读消息徽章
  - 登录/登出功能集成

**State Management** (Pinia stores in [frontend-vue/src/stores/](frontend-vue/src/stores/)):
- **user.ts** - Authentication state, login/logout actions, user profile data
- **counter.ts** - Demo store (minimal usage, can be removed)

**API Client** ([frontend-vue/src/api/index.ts](frontend-vue/src/api/index.ts)):
- Axios instance with base URL: `http://localhost:5001/api`
- Request interceptor: Auto-injects JWT token from localStorage
- Response interceptor: Global error handling with Element Plus notifications
- 6 API modules matching backend blueprints:
  - `userAPI` - register, login, getUser, updateUser, searchUsers, getStats
  - `itemAPI` - getItems, getItemDetail, createItem, updateItem, deleteItem, getCategories, search
  - `orderAPI` - createOrder, getOrder, updateOrder, cancelOrder, getUserOrders, getStatistics
  - `messageAPI` - sendMessage, getMessage, getConversations, getUnread, markAsRead
  - `wishlistAPI` - getWishlist, addToWishlist, removeFromWishlist, checkFavorited, getStatistics
  - `addressAPI` - getUserAddresses, createAddress, updateAddress, deleteAddress, setDefault

### Database Schema Design

**7 Core Tables** ([database/database_schema.sql](database/database_schema.sql)):

1. **user** (11 columns)
   - Primary key: `user_id` (AUTO_INCREMENT)
   - Unique constraints: `student_id`, `username`
   - Validations: phone regex `^1[3-9][0-9]{9}$`, email regex, credit_score CHECK (0-100)
   - Status enum: active, frozen, deleted
   - Initial credit: 100 points

2. **category** (5 columns)
   - Hierarchical design: `parent_category_id` (self-reference)
   - Supports 2-level category tree

3. **item** (13 columns)
   - Foreign keys: `user_id` (CASCADE), `category_id` (RESTRICT)
   - Images: JSON array storage (e.g., `["img1.jpg", "img2.jpg"]`)
   - Condition enum: brand_new, like_new, very_good, good, acceptable
   - Status enum: available, sold, removed
   - Indexes: user_id, category_id, status, publish_date
   - FULLTEXT index: (title, description) for search

4. **address** (10 columns)
   - Foreign key: `user_id` (CASCADE)
   - Type enum: dormitory, home, other
   - `is_default` flag: only one default address per user

5. **order** (14 columns)
   - Status flow: pending_payment → paid → shipped → completed (or cancelled)
   - Payment methods: alipay, wechat, cash
   - Delivery types: meet (面交), express (快递)
   - Constraints: buyer_id ≠ seller_id, total_amount > 0
   - Timestamps: create_time, payment_time, ship_time, complete_time

6. **message** (8 columns)
   - Many-to-many between users
   - Optional `item_id` for item-related conversations
   - Type enum: text, image
   - `is_read` flag for unread count

7. **wishlist** (3 columns)
   - Many-to-many user-item relationship
   - `notes` field for user annotations
   - Unique constraint: (user_id, item_id)

**Key Constraints & Indexes**:
- Foreign keys with `ON DELETE CASCADE` or `ON DELETE SET NULL`
- CHECK constraints: credit_score (0-100), total_amount > 0
- Indexes on high-frequency query columns: user_id, item_id, category_id, status
- FULLTEXT index for item search functionality

## Development Workflow

### Adding a New API Endpoint

1. **Backend Route** - Write raw SQL in appropriate route file:
   ```python
   # In backend/routes/user_routes.py
   from flask import Blueprint, request, jsonify
   from db import db_manager

   user_bp = Blueprint('user', __name__)

   @user_bp.route('/<int:user_id>/stats', methods=['GET'])
   def get_user_stats(user_id):
       sql = """
           SELECT
               COUNT(DISTINCT i.item_id) as total_items,
               COUNT(DISTINCT o.order_id) as total_orders
           FROM user u
           LEFT JOIN item i ON u.user_id = i.user_id
           LEFT JOIN `order` o ON u.user_id = o.buyer_id
           WHERE u.user_id = %s
       """
       result = db_manager.execute_query(sql, (user_id,))
       return jsonify(result[0])
   ```

2. **Frontend API Client** - Add method to corresponding API module:
   ```typescript
   // In frontend-vue/src/api/index.ts
   export const userAPI = {
     // ... existing methods
     getStats: (id: number) => api.get(`/users/${id}/stats`)
   }
   ```

3. **Frontend Component** - Call API in Vue component:
   ```vue
   <script setup lang="ts">
   import { ref, onMounted } from 'vue'
   import { userAPI } from '@/api'

   const stats = ref(null)
   const userId = 1

   onMounted(async () => {
     stats.value = await userAPI.getStats(userId)
   })
   </script>
   ```

### Modifying Database Schema

1. **Update schema file**: Edit `database/database_schema.sql`
2. **Write ALTER statements** if modifying existing tables:
   ```sql
   ALTER TABLE user ADD COLUMN avatar VARCHAR(255) AFTER email;
   ```
3. **Update route handlers** if columns changed
4. **Update TypeScript types** in `frontend-vue/src/types/index.ts`
5. **Test thoroughly** with `test/try_api.py`
6. **Document in project report** (required for course submission)

### Testing API Endpoints

Use curl to test individual endpoints:

```bash
# Health check (no auth required)
curl http://localhost:5001/api/health

# User registration
curl -X POST http://localhost:5001/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "21371234",
    "username": "testuser",
    "password": "password123",
    "real_name": "张三",
    "phone": "13800138000",
    "email": "test@buaa.edu.cn"
  }'

# User login
curl -X POST http://localhost:5001/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'

# Authenticated request (replace <token> with actual JWT)
curl -H "Authorization: Bearer <token>" \
  http://localhost:5001/api/users/1

# Get all items
curl http://localhost:5001/api/items/

# Get item categories
curl http://localhost:5001/api/items/categories

# Get user orders
curl http://localhost:5001/api/orders/user/1

# Get conversations
curl http://localhost:5001/api/messages/conversations/1

# Get wishlist
curl http://localhost:5001/api/wishlist/1

# Get user addresses
curl http://localhost:5001/api/addresses/user/1
```

## Academic Requirements Checklist

This project must fulfill specific Beihang Database Systems course requirements:

**Database Design**:
- ✅ 6-8 entities implemented (7 tables: user, category, item, order, message, wishlist, address)
- ✅ ER diagram provided in [docs/ER图.pdf](docs/ER图.pdf)
- ✅ Normalized to 3NF (no redundant data, all non-key attributes depend on primary key)
- ✅ Indexes defined for performance optimization

**Functionality** (CRUD operations with raw SQL):
- ✅ **Query**: SELECT with JOIN, WHERE, ORDER BY, GROUP BY
- ✅ **Insert**: User registration, item publishing, order creation
- ✅ **Delete**: Soft delete with status update (item.status = 'removed')
- ✅ **Update**: Item editing, order status changes, user profile updates

**SQL Requirements**:
- ✅ Raw SQL only - NO ORM query builders allowed
- ✅ Parameterized queries to prevent SQL injection
- ✅ Stored procedures in database_schema.sql
- ✅ Triggers for auto-updates (e.g., credit score, timestamps)

**Project Deliverables**:
- System design report (功能设计 + 数据库设计)
- Implementation report (SQL statements + running results)
- Source code with database dump
- Live demo presentation

## Important Notes

### Security Best Practices

1. **Password Security**: All passwords hashed with SHA256 via `db_manager.hash_password()`
2. **SQL Injection Prevention**: ALWAYS use parameterized queries with `%s` placeholders
3. **JWT Authentication**: Tokens stored in localStorage, auto-injected in API requests
4. **SSL/TLS**: Database connections encrypted with certificate validation
5. **CORS**: Restricted to specific development ports (5173, 3001)

### Performance Optimization

1. **Database**:
   - Indexes on: user_id, item_id, category_id, order_id, status, publish_date
   - FULLTEXT index on item (title, description) for search
   - Connection pooling via context managers
2. **Frontend**:
   - Route lazy loading for code splitting
   - Image lazy loading in item grids
   - Pagination (default 20 items per page)
   - **Sidebar动画优化**: cubic-bezier(0.4, 0, 0.2, 1) 缓动函数
   - **页面切换**: 渐变+平移复合动画（fade + translateY）
3. **API**:
   - DictCursor for efficient JSON serialization
   - Minimal data transfer (only required fields)

### UI/UX Design Patterns

**现代简约风格 (YouTube/Twitter Inspired)**:
- **侧边栏导航** - 固定左侧，悬停展开，移动端友好
- **渐变背景** - 个人中心头部使用主题色渐变 (135deg)
- **卡片阴影** - 悬停时轻微上浮效果 (translateY(-2px) + shadow-md)
- **圆角设计** - 统一使用 CSS 变量: `--radius-base`, `--radius-lg`, `--radius-xl`
- **过渡动画** - 0.2-0.3s 缓动动画，提升交互流畅度
- **响应式布局** - 768px/1024px 断点，移动端自适应
- **色彩系统** - 主题色为蓝色，使用 CSS 变量统一管理

### Common Pitfalls & Mistakes

1. **❌ DO NOT** use Django ORM or SQLAlchemy query methods - violates course requirements
   ```python
   # WRONG - ORM usage
   users = User.objects.filter(status='active')

   # CORRECT - Raw SQL
   sql = "SELECT * FROM user WHERE status = %s"
   users = db_manager.execute_query(sql, ('active',))
   ```

2. **❌ DO NOT** commit `config.ini` with credentials to git (already in .gitignore)

3. **❌ DO NOT** use string concatenation for SQL (creates injection risk)
   ```python
   # WRONG - SQL injection vulnerability
   sql = f"SELECT * FROM user WHERE user_id = {user_id}"

   # CORRECT - Parameterized query
   sql = "SELECT * FROM user WHERE user_id = %s"
   result = db_manager.execute_query(sql, (user_id,))
   ```

4. **❌ DO NOT** forget to update both buyer and seller views when modifying order logic

5. **❌ DO NOT** violate CHECK constraints (e.g., credit_score must be 0-100)

6. **⚠️ REMEMBER**: Backend runs on port **5001**, not 5000 (common mistake when copying Flask examples)

7. **⚠️ REMEMBER**: The `order` table is called `` `order` `` in SQL (backticks required, it's a MySQL reserved word)

### Git Best Practices

**Before committing**:
- DO NOT commit `config.ini` (credentials)
- DO NOT commit `node_modules/` (already in .gitignore)
- DO commit updated documentation in `docs/`

### File Reference Format

When discussing code locations in issues or documentation, use markdown links:
- Files: [app.py](backend/app.py)
- Specific lines: [db.py:53](backend/db.py#L53)
- Line ranges: [user_routes.py:10-25](backend/routes/user_routes.py#L10-L25)
- Directories: [views/](frontend-vue/src/views/)

## Documentation & Resources

### Project Documentation (Chinese)
- **Functional requirements**: [docs/功能模块定义.md](docs/功能模块定义.md) - Detailed 6-module specifications
- **Frontend design**: [docs/前端设计文档.md](docs/前端设计文档.md) - Component breakdown, API mapping
- **Data flow diagrams**: [docs/数据流图.md](docs/数据流图.md) - DFD layers 0-2
- **Course objectives**: [docs/作业目标.md](docs/作业目标.md) - Assignment specifications
- **ER diagrams**: [docs/ER图.pdf](docs/ER图.pdf), [docs/ER图.png](docs/ER图.png)

### Key Technical References
- **Database schema**: [database/database_schema.sql](database/database_schema.sql) - Complete DDL with constraints
- **Database manager**: [backend/db.py](backend/db.py) - Connection pooling and query execution
- **Flask app entry**: [backend/app.py](backend/app.py) - Blueprint registration and CORS config
- **API client**: [frontend-vue/src/api/index.ts](frontend-vue/src/api/index.ts) - Axios instance and API modules
- **Router config**: [frontend-vue/src/router/index.ts](frontend-vue/src/router/index.ts) - Routes with auth guards

### External Resources
- **Vue 3 Docs**: https://vuejs.org/
- **Element Plus**: https://element-plus.org/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **PyMySQL**: https://pymysql.readthedocs.io/

---

**Team Members**: 肖一涵、刘鑫宇
**Course**: Database Systems (Beihang University)
**Last Updated**: 2025-10-29
