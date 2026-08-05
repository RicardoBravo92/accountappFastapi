# AccountApp Backend

[![Build](https://img.shields.io/github/actions/workflow/status/org/accountapp/ci.yml)](https://github.com/org/accountapp)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-blue)](https://fastapi.tiangolo.com/)

> A full-featured accounting backend API with JWT authentication, role-based access control, and comprehensive CRUD operations for companies, contacts, accounts, transactions, invoices, and bills.

## Quick Start

```bash
# Clone and setup
git clone git@github.com:RicardoBravo92/accountappFastapi.git
cd accountappFastapi
cp .env.example .env
uv sync

# Run server
uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Verify it's working
curl http://localhost:8000/health
# Expected: {"status": "ok", "version": "0.1.0", "environment": "development", "database": "connected"}
```

## Usage

### User Registration & Login

```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user1","password":"secure_pass123","first_name":"John","last_name":"Doe"}'

# Login and get JWT tokens
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secure_pass123"

# Response: {"access_token": "...", "refresh_token": "...", "token_type": "bearer", "expires_at": "..."}
```

### Using the Access Token

```bash
# All API routes under /api/v1 require authentication
TOKEN="your_access_token_here"

# Get current user profile
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Create a company
curl -X POST http://localhost:8000/api/v1/companies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Acme Corp","slug":"acme-corp","currency_code":"USD"}'

# List all companies
curl http://localhost:8000/api/v1/companies \
  -H "Authorization: Bearer $TOKEN"
```

## Configuration

Create a `.env` file based on `.env.example`:

| Variable                      | Description                                       | Default                                             | Required |
| ----------------------------- | ------------------------------------------------- | --------------------------------------------------- | -------- |
| `DATABASE_URL`                | Database connection string (PostgreSQL or SQLite) | `sqlite:///./accountapp.db`                         | No       |
| `SECRET_KEY`                  | Key for signing JWT tokens                        | `change-me-in-production`                           | **Yes**  |
| `ALGORITHM`                   | JWT signing algorithm                             | `HS256`                                             | No       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration (minutes)                 | `30`                                                | No       |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | Refresh token expiration (days)                   | `7`                                                 | No       |
| `CORS_ORIGINS`                | Allowed CORS origins                              | `["http://localhost:3000","http://localhost:5173"]` | No       |
| `UPLOAD_DIR`                  | Directory for file uploads                        | `uploads`                                           | No       |
| `MAX_UPLOAD_SIZE`             | Max upload size in bytes                          | `10 * 1024 * 1024` (10MB)                           | No       |

### Example `.env`

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/accountapp

# Security - CHANGE THIS IN PRODUCTION
SECRET_KEY=your-super-secret-key-change-this

# CORS - add your frontend URL
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Environment
ENVIRONMENT=production
DEBUG=false
```

## API Endpoints

### Authentication (`/api/v1/auth`)

| Method | Endpoint         | Description              |
| ------ | ---------------- | ------------------------ |
| POST   | `/auth/register` | Register a new user      |
| POST   | `/auth/login`    | Login and receive tokens |
| POST   | `/auth/refresh`  | Refresh access token     |
| GET    | `/auth/me`       | Get current user info    |

### Business Entities (`/api/v1`)

| Entity           | Methods Supported                                             |
| ---------------- | ------------------------------------------------------------- |
| **Companies**    | Create, Read, Update, Delete (soft), List                     |
| **Contacts**     | CRUD + type filtering (customer/vendor/both)                  |
| **Accounts**     | CRUD + type filtering (asset/liability/equity/income/expense) |
| **Transactions** | CRUD + reconciliation status                                  |
| **Invoices**     | CRUD + items with tax calculation                             |
| **Bills**        | CRUD + items with tax calculation                             |
| **Items**        | CRUD for inventory/product items                              |
| **Categories**   | CRUD for transaction categorization                           |
| **Currencies**   | CRUD with conversion rates                                    |
| **Transfers**    | Between accounts                                              |
| **Reports**      | Profit-loss, Income-expense, Tax summary                      |
| **Uploads**      | File upload/download with size limits                         |

### System Endpoints

| Method | Endpoint  | Description                   |
| ------ | --------- | ----------------------------- |
| GET    | `/health` | Health check                  |
| GET    | `/`       | API information               |
| GET    | `/docs`   | Swagger UI (interactive docs) |
| GET    | `/redoc`  | ReDoc documentation           |

## Testing

```bash
# Run all tests (unit + feature)
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/feature/auth/test_auth.py

# Run with coverage
uv run pytest --cov=app tests/
```

> **37 tests** covering authentication, companies, contacts, accounts, and health checks.

## Security

- **Password Hashing**: bcrypt with salt rounds
- **JWT Tokens**: Access tokens (30 min) + refresh tokens (7 days)
- **Role-Based Access Control**: `admin`, `viewer`, and `manager` roles
- **CORS**: Configurable per environment
- **Rate Limiting**: Ready for implementation
- **Security Headers**:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Strict-Transport-Security` (HSTS)
  - `Content-Security-Policy`

## Architecture

```
accountappBack/
├── app/
│   ├── api/                    # API endpoints and routing
│   │   ├── v1/router.py        # API v1 router aggregation
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── companies.py        # Company CRUD
│   │   ├── contacts.py         # Contact CRUD
│   │   ├── accounts.py         # Account CRUD
│   │   ├── transactions.py     # Transaction CRUD
│   │   ├── invoices.py         # Invoice CRUD
│   │   ├── bills.py            # Bill CRUD
│   │   ├── reports.py          # Financial reports
│   │   └── uploads.py          # File upload/download
│   ├── core/
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   ├── auth.py             # JWT + bcrypt utilities
│   │   └── database.py         # SQLAlchemy setup
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic models (DTOs)
│   ├── repositories/           # Data access layer
│   └── services/               # Business logic
├── tests/
│   ├── unit/                   # Unit tests
│   └── feature/                # Integration/API tests
└── pyproject.toml
```

## Docker

```bash
# Build and run
docker build -t accountapp-backend .
docker run -p 8000:8000 --env-file .env accountapp-backend

# Or with docker-compose
docker-compose up --build
```

## Development

### Using uv (recommended)

```bash
# Sync dependencies
uv sync

# Install dev dependencies
uv sync --extra dev

# Run in development mode
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Lint
uv run ruff check app/

# Format
uv run black app/

# Type check
uv run mypy app/
```

### Database Migrations

```bash
# Initialize (if not already done)
uv run alembic init -t app/database.py alembic

# Create a migration
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1
```

## Docker

```bash
# Build and run with docker-compose (includes PostgreSQL and Redis)
docker-compose up --build -d

# Run in development mode with hot reload
docker-compose -f docker-compose.yml up --build

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Run tests in container
docker-compose exec app uv run pytest
```

### Production Deployment

For production deployments, use the pre-built image:

```bash
# Pull and run
docker build -t accountapp/backend .
docker run -d \
  --name accountapp-backend \
  -p 8000:8000 \
  --env-file .env \
  accountapp/backend
```

Ensure your `.env` file has production settings:
```bash
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://user:pass@db:5432/accountapp
SECRET_KEY=your-secure-32-char-min-secret
CORS_ORIGINS=https://yourdomain.com
```

## License

MIT
