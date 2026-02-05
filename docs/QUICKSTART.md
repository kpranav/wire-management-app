# Quick Start Guide

Get the Wire Management application running in under 10 minutes.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Git

## 5-Minute Setup

### 1. Clone and Navigate

```bash
git clone <your-repo-url>
cd wire-management-app
```

### 2. Install Dependencies

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cd ..

# Frontend
cd frontend
npm install
cd ..
```

### 3. Start Services

```bash
# Start PostgreSQL and Redis
docker compose -f docker-compose.dev.yml up -d postgres-dev redis-dev

# Run database migrations
cd backend
source venv/bin/activate
alembic upgrade head
cd ..
```

### 4. Start Application

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 5. Access Application

- Open browser: http://localhost:5173
- Register a new account
- Create your first wire transfer!

## Next Steps

- Read [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) for detailed dev workflow
- Read [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
- Read [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions

## Testing the Full Stack

```bash
# Run all tests and checks
make all-checks
```

## Using Docker (Full Stack)

Alternative to running backend/frontend separately:

```bash
# Build and start everything
docker compose -f docker-compose.dev.yml up --build

# Access at:
# - Frontend: http://localhost:3001
# - Backend: http://localhost:8001
# - API Docs: http://localhost:8001/docs
```

## Common Issues

**Backend fails to start:**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check connection
psql postgresql://wireuser:devpass123@localhost:5432/wire_dev
```

**Frontend fails to start:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Port already in use:**
```bash
# Find and kill process using port 8000
lsof -i :8000
kill -9 <PID>
```
