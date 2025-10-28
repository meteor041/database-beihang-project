# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**校内二手物品交易平台** (Campus Second-hand Trading Platform) - A full-stack database application project for Beihang University's Database Systems course. This system manages 6-8 entities (users, items, orders, messages, wishlist, addresses, categories) with complete CRUD operations using native SQL.

**Tech Stack:**
- **Frontend**: Vue 3 + TypeScript + Vite + Pinia + Element Plus
- **Backend**: Python Flask with raw SQL (no ORM)
- **Database**: Huawei Cloud GaussDB (for MySQL) with SSL connection
- **Node Version**: ^20.19.0 || >=22.12.0

**Academic Constraints:**
- **CRITICAL**: ALL database operations MUST use raw SQL queries (no ORM abstractions like Django filters)
- High-level frameworks (like Django) are allowed ONLY for database connection
- Stored procedures and triggers MUST be implemented in raw SQL
- This is a 2-person team project with clear task division

## Project Structure

```
.
├── backend/                 # Main Flask backend (active, runs on port 5001)
│   ├── app.py              # Flask app entry point with blueprint registration
│   ├── db.py               # Database manager with connection pool & raw SQL execution
│   └── routes/             # API route blueprints (6 modules, 47 total endpoints)
│       ├── user_routes.py      # User management - 7 endpoints (register, login, get/update user, etc.)
│       ├── item_routes.py      # Item management - 8 endpoints (publish, browse, search, categories, etc.)
│       ├── order_routes.py     # Transaction management - 7 endpoints (create, update, cancel, statistics, etc.)
│       ├── message_routes.py   # Messaging system - 8 endpoints (send, receive, conversations, unread, etc.)
│       ├── wishlist_routes.py  # Wishlist management - 8 endpoints (add, remove, list, check, statistics, etc.)
│       └── address_routes.py   # Address management - 9 endpoints (CRUD, default address management, etc.)
├── backend-new/            # Alternative backend structure (experimental, not currently in use)
├── frontend-vue/           # Vue 3 SPA
│   ├── src/
│   │   ├── views/          # 16 core pages (Home, ItemDetail, Orders, etc.)
│   │   ├── components/     # Reusable components (ItemCard, UserAvatar, etc.)
│   │   ├── stores/         # Pinia stores (user, cart, message)
│   │   ├── router/         # Vue Router configuration
│   │   └── api/            # API client with axios interceptors
│   └── package.json        # Frontend dependencies and scripts
├── database/
│   └── database_schema.sql # Complete DDL with constraints, indexes, triggers
├── docs/                   # Project documentation (Chinese)
│   ├── 功能模块定义.md      # Detailed functional requirements (6 modules)
│   ├── 前端设计文档.md      # Frontend design specs (16 pages, API mapping)
│   └── 数据流图.md          # Data flow diagrams (DFD 0-2 layers)
├── test/
│   └── try_api.py          # API testing script
├── config.ini              # Database credentials (gitignored)
├── config.ini.example      # Config template
└── pem/
    └── ca-bundle.pem       # SSL certificate for GaussDB
```

## Common Commands

### Frontend Development
```bash
cd frontend-vue
npm install                  # Install dependencies
npm run dev                  # Start dev server (localhost:5173)
npm run build                # Production build with type checking
npm run type-check           # TypeScript type checking only
npm run lint                 # ESLint with auto-fix
npm run format               # Prettier formatting
npm run test:unit            # Run Vitest unit tests
npm run test:e2e             # Run Playwright E2E tests
```

### Backend Development
```bash
cd backend
python3 app.py               # Start Flask server (localhost:5001)
# The backend has no requirements.txt - manually install:
pip3 install flask flask-cors pymysql

# When started, you'll see:
# API文档: http://localhost:5001/
# 健康检查: http://localhost:5001/api/health
```

### Database Setup
1. Copy `config.ini.example` to `config.ini` and fill in GaussDB credentials
2. Ensure `pem/ca-bundle.pem` exists for SSL connection
3. Execute `database/database_schema.sql` on GaussDB to create tables

### Testing
```bash
# Test backend API
cd test
python3 try_api.py

# Test frontend in isolation
cd frontend-vue
npm run test:unit -- <test-file>  # Run specific test
npm run test:e2e -- --debug       # Debug E2E tests
```

## Architecture & Key Design Patterns

### Backend Architecture (Flask + Raw SQL)

**Database Manager Pattern** ([backend/db.py](backend/db.py)):
- `DatabaseManager` class handles connection pooling with context managers
- Three execution methods:
  - `execute_query(sql, params)` - SELECT queries returning dict list
  - `execute_update(sql, params)` - UPDATE/DELETE returning row count
  - `execute_insert(sql, params)` - INSERT returning last insert ID
- Built-in utilities: `hash_password()`, `generate_order_number()`
- SSL connection to GaussDB with certificate validation

**Blueprint-based Routes** ([backend/app.py](backend/app.py)):
- All routes organized into 6 blueprints with `/api/<resource>` prefix (47 total endpoints)
- CORS enabled for frontend communication (localhost:5173 and localhost:3001)
- Health check endpoint: `GET /api/health`
- Server runs on port 5001 (configured in [app.py:81](backend/app.py#L81))

**Raw SQL Enforcement**:
```python
# CORRECT - Use db_manager with raw SQL
sql = "SELECT * FROM user WHERE user_id = %s"
result = db_manager.execute_query(sql, (user_id,))

# WRONG - No ORM methods allowed
user = User.objects.filter(user_id=user_id)  # NOT ALLOWED
```

### Frontend Architecture (Vue 3 Composition API)

**16 Core Pages** (see [docs/前端设计文档.md](docs/前端设计文档.md:50-577)):
1. Home (`/`) - Item grid with infinite scroll
2. Search (`/search`) - Multi-filter search with sidebar
3. ItemDetail (`/item/:id`) - Full item info, seller card, recommendations
4. Checkout (`/checkout`) - Order confirmation, address/payment selection
5. Orders (`/orders`) - Order list with status tabs (buyer/seller views)
6. OrderDetail (`/order/:id`) - Order timeline, logistics tracking
7. Messages (`/messages`) - Split-pane chat interface
8. Wishlist (`/wishlist`) - Favorited items with batch operations
9. Addresses (`/addresses`) - Address CRUD with default management
10. Profile (`/profile`) - User dashboard with statistics
11. ProfileEdit (`/profile/edit`) - Avatar upload, info update
12. Publish (`/publish`) - Item creation with image upload (max 9)
13. MyItems (`/my-items`) - Seller's item management
14. Login (`/login`) - Multi-method login (username/student_id/phone)
15. Register (`/register`) - Student registration with validation
16. UserProfile (`/user/:id`) - Public profile view

**State Management** (Pinia stores in [frontend-vue/src/stores/](frontend-vue/src/stores/)):
- `user.ts` - Authentication state, login/logout actions
- `cart.ts` - Checkout flow state (item, address, payment method)
- `message.ts` - Conversations, unread count, real-time updates

**API Client** ([frontend-vue/src/api/index.ts](docs/前端设计文档.md:703-784)):
- Axios instance with base URL: `http://localhost:5001/api`
- Request/response interceptors for token injection and error handling
- JWT token auto-injection from localStorage
- Centralized error handling with Element Plus messages
- 6 API modules: `userAPI`, `itemAPI`, `orderAPI`, `messageAPI`, `wishlistAPI`, `addressAPI`

### Database Schema Design

**7 Core Tables** ([database/database_schema.sql](database/database_schema.sql)):
1. `user` - Student accounts with credit scoring system
2. `category` - Two-level hierarchy (parent_category_id self-reference)
3. `item` - Items with JSON images array, condition levels (5 enums)
4. `order` - Orders with status flow: pending → paid → shipped → completed
5. `message` - User-to-user messaging with item context
6. `wishlist` - Many-to-many user-item relationship with notes
7. `address` - User addresses with default flag

**Key Constraints**:
- Credit score CHECK: 0-100 range
- Phone regex: `^1[3-9][0-9]{9}$`
- Email regex validation
- Foreign keys with ON DELETE CASCADE/SET NULL
- Indexes on high-frequency query columns

**Status Enums**:
- User status: active, frozen, deleted
- Item status: available, sold, deleted
- Item condition: brand_new, like_new, very_good, good, acceptable
- Order status: pending, paid, shipped, completed, cancelled

## Development Workflow

### Adding a New API Endpoint

1. **Database Layer** - Write raw SQL in appropriate route file:
   ```python
   # In backend/routes/user_routes.py
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
     getStats: (id) => api.get(`/users/${id}/stats`)
   }
   ```

3. **Frontend Component** - Call API in Vue component:
   ```vue
   <script setup lang="ts">
   import { userAPI } from '@/api'
   const stats = await userAPI.getStats(userId)
   </script>
   ```

### Modifying Database Schema

1. Update `database/database_schema.sql` with ALTER statements
2. Document changes in project report (required for course)
3. Test with `test/try_api.py` to verify data integrity
4. Update corresponding route handlers if columns changed

### Testing API Endpoints

Use the health check as a template:
```bash
curl http://localhost:5001/api/health
```

For authenticated endpoints, include JWT token:
```bash
curl -H "Authorization: Bearer <token>" http://localhost:5001/api/users/1
```

Test specific endpoints by category:
```bash
# User endpoints (7 endpoints)
curl -X POST http://localhost:5001/api/users/register -H "Content-Type: application/json" -d '{...}'
curl -X POST http://localhost:5001/api/users/login -H "Content-Type: application/json" -d '{...}'

# Item endpoints (8 endpoints)
curl http://localhost:5001/api/items/
curl http://localhost:5001/api/items/categories

# Order endpoints (7 endpoints)
curl http://localhost:5001/api/orders/user/1

# Message endpoints (8 endpoints)
curl http://localhost:5001/api/messages/conversations/1

# Wishlist endpoints (8 endpoints)
curl http://localhost:5001/api/wishlist/1

# Address endpoints (9 endpoints)
curl http://localhost:5001/api/addresses/user/1
```

## Academic Requirements Checklist

This project must fulfill specific course requirements:

**Database Design**:
- ✅ 6-8 entities implemented (7 tables)
- ✅ ER diagram provided in docs
- ✅ Normalized to 3NF (documented in project report)
- ✅ Indexes defined for performance

**Functionality**:
- ✅ Query (SELECT with JOIN, WHERE, ORDER BY)
- ✅ Insert (user registration, item publishing)
- ✅ Delete (soft delete with status update)
- ✅ Update (item editing, order status changes)

**SQL Constraints**:
- ✅ Raw SQL only - NO ORM query builders
- ✅ Stored procedures in database_schema.sql
- ✅ Triggers for auto-updates (credit score, timestamps)

**Project Artifacts**:
- System design report (功能设计 + 数据库设计)
- Implementation report (SQL statements + running results)
- Source code with database dump
- Live demo presentation

## Important Notes

### Security
- Passwords hashed with SHA256 via `db_manager.hash_password()`
- SQL injection prevention through parameterized queries (`%s` placeholders)
- JWT tokens for session management
- SSL/TLS for database connections

### Performance Optimization
- Database: Indexes on user_id, item_id, category_id, order_id
- Frontend: Image lazy loading, route lazy loading, skeleton screens
- API: Pagination for list endpoints (default 20 items per page)

### Common Pitfalls
1. **DO NOT** use Django ORM or SQLAlchemy query methods - violates course rules
2. **DO NOT** commit `config.ini` with credentials to git
3. **ALWAYS** use parameterized queries, never string concatenation for SQL
4. **REMEMBER** to update both buyer and seller views when modifying order logic
5. **CHECK** credit score constraints before updates (0-100 range)
6. **VERIFY** API base URL - backend runs on port **5001**, not 5000 (common mistake when copying examples)

### File References in Code
When discussing code locations, use markdown links:
- Files: [app.py](backend/app.py)
- Specific lines: [db.py:53-58](backend/db.py#L53-L58)
- Ranges: [user_routes.py:10-25](backend/routes/user_routes.py#L10-L25)

## Contact & Documentation

- Frontend design details: [docs/前端设计文档.md](docs/前端设计文档.md)
- Data flow diagrams: [docs/数据流图.md](docs/数据流图.md)
- Functional requirements: [docs/功能模块定义.md](docs/功能模块定义.md)
- Project objectives: [docs/作业目标.md](docs/作业目标.md)

For course-specific questions, refer to [docs/作业目标.md](docs/作业目标.md) which contains the complete assignment specifications from the Database Systems course.
