# Local Development Guide

This guide covers running linting, type checks, and tests locally before pushing to GitHub.

## Prerequisites

- Python 3.11+ (backend)
- Node.js 18+ (frontend)
- Docker & Docker Compose

## Backend Development

### Initial Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running Checks Locally

Using Make commands:

```bash
# Lint code
make lint

# Auto-fix linting issues
make format

# Type check
make type-check

# Run tests
make test

# Run all checks (lint + type-check + test)
make all-checks
```

Using direct commands:

```bash
# Activate virtual environment first
source venv/bin/activate

# Lint with Ruff
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Format with Black
black .

# Type check with Mypy
mypy app

# Run tests with pytest
pytest tests -v --cov=app --cov-report=term-missing
```

## Frontend Development

### Initial Setup

```bash
cd frontend
npm install
```

### Running Checks Locally

Using Make commands:

```bash
# Lint code
make lint

# Auto-fix linting issues
make format

# Type check
make type-check

# Run tests
make test

# Run all checks
make all-checks
```

Using npm scripts:

```bash
# Lint with ESLint
npm run lint

# Auto-fix linting issues
npm run lint -- --fix

# Type check with TypeScript
npm run type-check

# Run tests with Vitest
npm run test
```

## Running the Application Locally

### Using Docker Compose (Recommended)

```bash
# From project root
docker compose -f docker-compose.dev.yml up --build
```

Access:
- Frontend: http://localhost:3001
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

### Manual Setup (Without Docker)

#### Backend

```bash
cd backend
source venv/bin/activate

# Ensure PostgreSQL and Redis are running locally
# Update .env with local database URLs

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8001
```

#### Frontend

```bash
cd frontend
npm run dev
```

## Pre-Commit Checks

**IMPORTANT**: Before pushing to GitHub, always format your code first, then run all checks:

```bash
# Backend - Format first, then check
cd backend
make format        # Auto-fixes Ruff + Black formatting
make all-checks    # Runs lint + type-check + test

# Frontend - Format first, then check
cd frontend
make format        # Auto-fixes ESLint
make all-checks    # Runs lint + type-check + test
```

**Quick one-liner for each:**
```bash
# Backend
cd backend && make format && make all-checks

# Frontend
cd frontend && make format && make all-checks
```

## CI/CD Pipeline

The GitHub Actions workflow automatically runs:
1. **Lint**: Ruff (Python), ESLint (TypeScript)
2. **Format Check**: Black (Python) - will fail if code isn't formatted
3. **Type Check**: Mypy (Python), tsc (TypeScript)
4. **Test**: Pytest (Python), Vitest (React)
5. **Build**: Docker images
6. **Deploy**: To appropriate environment based on branch

**⚠️ CI/CD will fail if code isn't formatted with Black!** Always run `make format` before pushing.

Running these checks locally before pushing ensures your code passes CI/CD.

## Common Issues

### Ruff "Import block is un-sorted"
```bash
# Auto-fix with:
ruff check --fix .
```

### ESLint unused variable errors
- Remove unused imports/variables
- Or prefix with underscore if intentionally unused: `_variable`

### TypeScript type errors
```bash
# Check errors:
npm run type-check

# Often fixed by ensuring correct types are imported
```

### Pytest failures
```bash
# Run specific test:
pytest tests/test_auth.py::test_register -v

# Run with print output:
pytest tests/test_auth.py -v -s
```

## Tips

1. **Use Make commands** - They're simpler and consistent across the team
2. **Run checks frequently** - Don't wait until before commit
3. **Fix linting first** - It's usually the quickest to fix
4. **Type errors are your friend** - They catch bugs before runtime
5. **Write tests as you code** - Not after everything is done
