# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**校内二手物品交易平台** (Campus Second-hand Trading Platform) - A full-stack web application for students to buy and sell second-hand items on campus. This is a database course project at Beihang University that emphasizes native SQL operations over ORM abstractions.

**Tech Stack:**
- **Backend:** Flask (Python) with PyMySQL
- **Frontend:** Vue 3 + TypeScript + Vite + Pinia
- **Database:** Huawei Cloud GaussDB (MySQL-compatible)

## Project Structure

```
.
├── backend/              # Flask REST API server
│   ├── app.py           # Main application entry point
│   ├── db.py            # Database connection manager
│   └── routes/          # API route blueprints (user, item, order, message, wishlist, address)
├── frontend-vue/        # Vue 3 frontend application
│   ├── src/
│   │   ├── api/         # API client with axios
│   │   ├── views/       # Page components
│   │   ├── components/  # Reusable components
│   │   ├── router/      # Vue Router configuration
│   │   └── stores/      # Pinia state management
│   └── package.json
├── database/            # SQL schema and migrations
│   └── database_schema.sql  # Complete database schema with 8 tables
├── docs/                # Project documentation (in Chinese)
├── test/                # API testing scripts
└── config.ini.example   # Database configuration template
```

## Critical Constraints

### Database Operations Requirement
**IMPORTANT:** This is a database course project with strict requirements:
- **All database operations MUST use native SQL statements** - no ORM query builders allowed
- DO NOT use high-level frameworks like Django ORM's `filter()`, SQLAlchemy query builders, etc.
- Raw SQL is enforced for: SELECT, INSERT, UPDATE, DELETE, stored procedures, and triggers
- The only exception: High-level frameworks can be used for initial table creation (e.g., Django models)

### Current Implementation Pattern
The codebase uses PyMySQL with raw SQL via the `DatabaseManager` class in [db.py](backend/db.py):
- `execute_query()` - for SELECT operations (returns list of dicts)
- `execute_insert()` - for INSERT operations (returns lastrowid)
- `execute_update()` - for UPDATE/DELETE operations (returns rowcount)
- All SQL uses parameterized queries with `%s` placeholders for security
- A singleton instance `db_manager` is exported from [db.py](backend/db.py) and imported by all route modules

## Database Architecture

The system manages **8 core entities** (as required by the project):

1. **user** - User accounts with student ID, credentials, credit scoring
2. **category** - Two-level hierarchical product categories
3. **item** - Product listings with pricing, images (JSON), condition levels
4. **address** - User shipping addresses with default address support
5. **order** - Transaction records with payment/delivery tracking
6. **message** - User-to-user messaging tied to items
7. **wishlist** - User favorites (many-to-many relationship)
8. **review** - Post-transaction ratings (1-5 stars)

**Key relationships:**
- Orders link buyer, seller, item, and address
- Messages create conversations between users about specific items
- Credit scores update based on transaction completion (+5) or violations (-10)

**See:** [database_schema.sql](database/database_schema.sql) for complete schema including indexes, constraints, and initial category data.

## Development Commands

### Backend Setup & Execution
```bash
# Setup (first time)
cp config.ini.example config.ini
# Edit config.ini with your GaussDB credentials

# Install dependencies
pip install flask flask-cors pymysql configparser

# Run development server (http://localhost:5000)
cd backend
python app.py

# Test database connection
curl http://localhost:5000/api/health
```

### Frontend Setup & Execution
```bash
cd frontend-vue

# Install dependencies
npm install

# Development server with hot reload (http://localhost:5173)
npm run dev

# Type checking
npm run type-check

# Production build
npm run build

# Lint and auto-fix
npm run lint

# Format code with Prettier
npm run format

# Run unit tests (Vitest)
npm run test:unit

# Run E2E tests (Playwright)
npx playwright install  # First time only
npm run test:e2e
npm run test:e2e -- --project=chromium  # Specific browser
npm run test:e2e -- tests/example.spec.ts  # Specific file
```

### Testing
```bash
# Backend API testing
cd test
python try_api.py
```

## Backend Architecture

### Request Flow
1. Client request → Flask route (in `routes/`)
2. Route validates input and extracts parameters
3. Raw SQL query constructed with parameterized placeholders
4. `db_manager` executes query via PyMySQL
5. Results formatted as JSON response

### Route Blueprints
All routes registered in [app.py](backend/app.py) with `/api/` prefix:
- `/api/users/*` - Registration, login, profile, credit scoring ([user_routes.py](backend/routes/user_routes.py))
- `/api/items/*` - CRUD, search, categories, user's items ([item_routes.py](backend/routes/item_routes.py))
- `/api/orders/*` - Create, status updates, payment, statistics ([order_routes.py](backend/routes/order_routes.py))
- `/api/messages/*` - Send, conversations, mark read, unread counts ([message_routes.py](backend/routes/message_routes.py))
- `/api/wishlist/*` - Add/remove favorites, statistics ([wishlist_routes.py](backend/routes/wishlist_routes.py))
- `/api/addresses/*` - CRUD, default address management ([address_routes.py](backend/routes/address_routes.py))

**Blueprint Naming Convention:**
- Blueprint variable: `{feature}_bp` (e.g., `user_bp`, `item_bp`)
- Blueprint name parameter: `'{feature}'` (e.g., `'user'`, `'item'`)
- Example: `user_bp = Blueprint('user', __name__)`

### Security Patterns
- Passwords hashed with SHA-256 via `db_manager.hash_password()`
- SQL injection prevention via parameterized queries
- Input validation (email regex, phone regex, password strength)
  - Helper functions in route files: `validate_email()`, `validate_phone()`, `validate_password()`
- Soft deletes for users (status='deleted')
- Account locking after 5 failed login attempts
- Route guards in frontend for authenticated routes

### Error Handling Pattern
All route endpoints follow a consistent error handling pattern:
```python
try:
    # 1. Extract and validate request data
    data = request.get_json()

    # 2. Validate required fields
    if not data.get('required_field'):
        return jsonify({'error': 'Error message'}), 400

    # 3. Execute SQL operations
    result = db_manager.execute_query(sql, params)

    # 4. Return success response
    return jsonify({'data': result}), 200

except Exception as e:
    # 5. Catch-all error handler
    return jsonify({'error': str(e)}), 500
```

## Frontend Architecture

### State Management
- **Pinia stores** in [src/stores/](frontend-vue/src/stores/): Global state for user auth, cart, etc.
- **Local storage**: Persists user session and token

### API Client
Centralized axios instance in [src/api/index.ts](frontend-vue/src/api/index.ts):
- Base URL: `http://localhost:5000/api`
- Request interceptor: Adds `Authorization: Bearer <token>` from localStorage
- Response interceptor: Extracts `response.data`, handles errors
- Organized by feature: `userAPI`, `itemAPI`, `orderAPI`, `messageAPI`, `wishlistAPI`, `addressAPI`

### Routing
[src/router/index.ts](frontend-vue/src/router/index.ts) defines routes with:
- `meta.requiresAuth` for protected routes
- `beforeEach` guard redirects unauthenticated users to `/login`
- Lazy loading for non-critical routes

### Key Views
- `/` - Home page with featured items
- `/login`, `/register` - Authentication
- `/items` - Product listing with search/filters
- `/items/:id` - Product detail page
- `/publish` - Create new listing (auth required)
- `/orders`, `/messages`, `/wishlist`, `/profile` - User dashboard features

## Common Development Patterns

### Adding a New API Endpoint

**Backend** ([backend/routes/](backend/routes/)):
```python
@blueprint_name.route('/example', methods=['POST'])
def example_endpoint():
    try:
        data = request.get_json()

        # Validate input
        if not data.get('required_field'):
            return jsonify({'error': 'Field required'}), 400

        # Execute raw SQL (REQUIRED - no ORM!)
        sql = """
        SELECT column1, column2
        FROM table_name
        WHERE condition = %s
        """
        result = db_manager.execute_query(sql, (data['param'],))

        return jsonify({'data': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**Frontend** ([frontend-vue/src/api/index.ts](frontend-vue/src/api/index.ts)):
```typescript
export const featureAPI = {
  exampleMethod: (data: any) => api.post('/endpoint', data),
  // GET with query params
  getExample: (params: any) => api.get('/endpoint', { params })
}
```

### Working with the Database

**Configuration:**
1. Copy `config.ini.example` to `config.ini`
2. Update `[database]` section with GaussDB credentials
3. Update `[ssl]` section - ca_file path points to `pem/ca-bundle.pem`

**Connection Pattern:**
```python
# Preferred: Use helper methods on db_manager singleton
result = db_manager.execute_query(sql, params)  # For SELECT
user_id = db_manager.execute_insert(sql, params)  # For INSERT
rows_affected = db_manager.execute_update(sql, params)  # For UPDATE/DELETE

# Alternative: Direct context manager (for complex transactions)
with db_manager.get_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        conn.commit()  # For INSERT/UPDATE/DELETE
        return cursor.fetchall()  # For SELECT
```

**Always use parameterized queries:**
```python
# CORRECT - parameterized with tuple
sql = "SELECT * FROM user WHERE user_id = %s"
result = db_manager.execute_query(sql, (user_id,))

# CORRECT - multiple parameters
sql = "SELECT * FROM user WHERE username = %s OR phone = %s"
result = db_manager.execute_query(sql, (username, phone))

# WRONG - SQL injection vulnerability!
sql = f"SELECT * FROM user WHERE user_id = {user_id}"

# WRONG - String formatting (vulnerable)
sql = "SELECT * FROM user WHERE user_id = {}".format(user_id)
```

**Database Manager Utilities:**
```python
# Password hashing
hashed = db_manager.hash_password(plain_password)

# Order number generation (32-char UUID without dashes)
order_num = db_manager.generate_order_number()
```

## Project Documentation

Detailed Chinese documentation in [docs/](docs/):
- [功能模块定义.md](docs/功能模块定义.md) - Complete feature specifications for all 6 modules
- [作业目标.md](docs/作业目标.md) - Project requirements and grading criteria
- [数据流图.md](docs/数据流图.md) - Data flow diagrams
- [任务流程.md](docs/任务流程.md) - Development workflow

## Node Version Requirement

**Frontend requires Node.js:** `^20.19.0 || >=22.12.0` (specified in [frontend-vue/package.json](frontend-vue/package.json))

Use `nvm` or `fnm` to switch Node versions if needed:
```bash
nvm use 22  # or nvm use 20.19
```

## Important Notes

- **SSL Configuration:** Database connection uses SSL with CA certificate in `pem/ca-bundle.pem`
- **CORS:** Enabled in Flask backend to allow frontend requests from different origin
- **JSON Support:** MySQL `item.images` column uses JSON type to store image URL arrays
- **Credit System:** Automated scoring affects user privileges (initial: 100, range: 0-100)
- **Soft Deletes:** Users marked as `status='deleted'` instead of hard deletion
- **Order Numbers:** Auto-generated 32-character UUIDs via `db_manager.generate_order_number()`
- **Fulltext Search:** `item` table has fulltext index on title+description for search functionality
- **Chinese Characters:** Flask configured with `JSON_AS_ASCII=False`, database uses `utf8mb4` charset
