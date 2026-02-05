# Wire Management Application

A production-ready wire transfer management system with FastAPI backend, React TypeScript frontend, and full CI/CD pipeline.

## Features

### Backend
- FastAPI REST API
- PostgreSQL with SQLAlchemy ORM
- JWT authentication
- Redis caching & background tasks (Celery)
- WebSocket real-time updates
- Comprehensive error handling
- 90%+ test coverage

### Frontend
- React 18 with TypeScript
- Vite build tool
- Material-UI components
- Real-time updates via WebSocket
- 80%+ test coverage

### CI/CD
- GitHub Actions pipeline
- Automated linting, type checking, testing
- Docker containerization
- Multi-environment deployment (Dev/QA/UAT/Prod)
- AI-powered code review

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7

### Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd wire-management-app

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

# Frontend setup
cd ../frontend
npm install

# Start databases
docker compose -f docker-compose.dev.yml up -d postgres-dev redis-dev

# Run migrations
cd ../backend
alembic upgrade head

# Start development servers
# Terminal 1:
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2:
cd frontend && npm run dev
```

### Running Tests

```bash
# All checks (lint + type-check + tests)
make all-checks

# Backend only
make backend-lint
make backend-test

# Frontend only
make frontend-lint
make frontend-test
```

## Project Structure

```
wire-management-app/
├── backend/          # FastAPI application
├── frontend/         # React TypeScript application
├── .github/          # CI/CD workflows
├── docker-compose.*.yml  # Environment-specific configs
└── docs/             # Documentation
```

## Environment Variables

See `.env.example` for required environment variables.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow and guidelines.

## License

MIT License
