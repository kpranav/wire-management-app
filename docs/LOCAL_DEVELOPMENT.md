# Local Development Guide

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker and Docker Compose
- Git
- pip and npm

## First-Time Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd wire-management-app
```

### 2. Install Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

This will run linting and formatting checks before each commit.

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Copy environment file
cp .env.example .env
# Edit .env with your local settings if needed
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env
# Edit .env with your local settings if needed
```

### 5. Start Local Services

```bash
# From project root
docker compose -f docker-compose.dev.yml up -d postgres-dev redis-dev
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379

### 6. Run Database Migrations

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### 7. Start Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Celery Worker (optional):**
```bash
cd backend
source venv/bin/activate
celery -A app.services.background_tasks.celery_app worker --loglevel=info
```

### 8. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Interactive Swagger UI)
- **Redoc**: http://localhost:8000/redoc

## Daily Development Workflow

### 1. Start Your Day

```bash
# Pull latest changes
git checkout develop
git pull origin develop

# Update dependencies if needed
cd backend && pip install -r requirements-dev.txt
cd frontend && npm install

# Start services
docker compose -f docker-compose.dev.yml up -d postgres-dev redis-dev
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

Edit code, add features, fix bugs...

### 4. Run Quality Checks

```bash
# Run all checks (from project root)
make all-checks

# Or run individually:
make backend-lint    # Lint backend code
make backend-test    # Run backend tests
make frontend-lint   # Lint frontend code
make frontend-test   # Run frontend tests
```

### 5. Run Tests Continuously

```bash
# Backend - run tests on file changes
cd backend
pytest tests -v --watch

# Frontend - run tests in watch mode
cd frontend
npm run test
```

### 6. Commit Changes

```bash
git add .
git commit -m "feat: add your feature description"

# Pre-commit hooks will run automatically
# If they fail, fix the issues and commit again
```

### 7. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a PR on GitHub targeting the `develop` branch.

## Common Tasks

### Create a New Database Migration

```bash
cd backend
source venv/bin/activate

# Auto-generate migration from model changes
alembic revision --autogenerate -m "add new field to wire model"

# Review the generated file in alembic/versions/
# Edit if necessary

# Apply migration
alembic upgrade head

# Test rollback
alembic downgrade -1
alembic upgrade head
```

### Reset Local Database

```bash
# Stop containers
docker compose -f docker-compose.dev.yml down

# Remove volumes (WARNING: This deletes all data)
docker compose -f docker-compose.dev.yml down -v

# Restart
docker compose -f docker-compose.dev.yml up -d postgres-dev redis-dev

# Re-run migrations
cd backend
alembic upgrade head
```

### Test with Docker Compose (Full Stack)

```bash
# Build and start all services
docker compose -f docker-compose.dev.yml up --build

# View logs
docker compose -f docker-compose.dev.yml logs -f

# Stop services
docker compose -f docker-compose.dev.yml down
```

### Add a New Python Dependency

```bash
cd backend
source venv/bin/activate

# Install the package
pip install package-name

# Update requirements
pip freeze > requirements.txt

# Or manually add to requirements.txt:
echo "package-name>=1.0.0" >> requirements.txt
```

### Add a New npm Dependency

```bash
cd frontend

# Install package
npm install package-name

# Package.json and package-lock.json will be updated automatically
```

### Debug Backend

```bash
# Run with debugger
cd backend
python -m debugpy --listen 5678 --wait-for-client -m uvicorn app.main:app --reload

# Or use VS Code debugger with launch.json
```

### Debug Frontend

Use browser DevTools:
- React DevTools extension
- Network tab for API calls
- Console for errors
- Sources for breakpoints

## Running Tests

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest tests -v

# Run specific test file
pytest tests/test_wires.py -v

# Run specific test
pytest tests/test_wires.py::test_create_wire -v

# Run with coverage
pytest tests -v --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm run test

# Run with UI
npm run test:ui

# Run specific test
npm run test -- WireList.test.tsx

# Generate coverage
npm run test -- --coverage
```

## Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Check database connection
cd backend
python -c "from app.database import engine; print('DB connected')"

# Check Redis connection
redis-cli ping
```

### Frontend won't start

```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check for port conflicts
lsof -i :5173
```

### Database connection errors

```bash
# Ensure PostgreSQL is running
docker ps | grep postgres

# Check PostgreSQL logs
docker logs wire-postgres-dev

# Test connection
psql postgresql://wireuser:devpass123@localhost:5432/wire_dev
```

### Migration errors

```bash
# Check current migration status
alembic current

# See migration history
alembic history

# Manually downgrade
alembic downgrade -1

# Force upgrade
alembic upgrade head
```

## Code Quality Tools

### Linting

```bash
# Backend
cd backend
ruff check .              # Check for issues
ruff check . --fix        # Auto-fix issues
black .                   # Format code

# Frontend
cd frontend
npm run lint              # Check for issues
npm run lint -- --fix     # Auto-fix issues
npm run format            # Format code
```

### Type Checking

```bash
# Backend
cd backend
mypy app

# Frontend
cd frontend
npm run type-check
```

## Environment Variables

### Backend (.env)
See `backend/.env.example` for all available environment variables.

### Frontend (.env)
- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)
- `VITE_WS_URL`: WebSocket URL (default: ws://localhost:8000)
- `VITE_FEATURE_*`: Feature flags

## Tips for Productive Development

1. **Use hot reload**: Both backend and frontend support hot reload
2. **Run tests in watch mode**: Get immediate feedback on changes
3. **Use API docs**: Visit `/docs` for interactive API testing
4. **Check logs**: Use `docker compose logs -f` to monitor services
5. **Keep branches short**: Merge to develop frequently to avoid conflicts
6. **Run checks before committing**: Use `make all-checks`
