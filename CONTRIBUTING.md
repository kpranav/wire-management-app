# Contributing to Wire Management App

## Development Workflow

### 1. Pick Up a Task
- Check the project board for available tasks
- Assign yourself to the task
- Move task to "In Progress"

### 2. Create Feature Branch
```bash
# Always branch from latest develop
git checkout develop
git pull origin develop

# Branch naming convention:
# feature/description-of-feature
# fix/description-of-bug
# refactor/description-of-refactor
git checkout -b feature/add-wire-filters
```

### 3. Develop Locally

```bash
# Start local environment
docker compose -f docker-compose.dev.yml up -d postgres-dev redis-dev

# Run backend (Terminal 1)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Run frontend (Terminal 2)
cd frontend
npm run dev  # Runs on port 5173
```

### 4. Stay Synced with Develop

Pull `develop` into your branch frequently (at least daily):

```bash
git checkout feature/your-feature
git pull origin develop
# Resolve any conflicts
make all-checks  # Ensure everything still works
```

### 5. Write Tests
- Backend: Add tests in `backend/tests/`
- Frontend: Add tests in `frontend/tests/`
- Target: 90%+ backend coverage, 80%+ frontend coverage

### 6. Run Quality Checks

```bash
# Run all checks locally before pushing
make all-checks

# Or individual checks:
make backend-lint
make backend-test
make frontend-lint
make frontend-test
```

### 7. Commit Your Changes

```bash
git add .
git commit -m "feat: add wire status filters

- Add status filter dropdown to WireList component
- Add query parameter support in backend API
- Add tests for filter functionality"

# Commit message format:
# <type>: <subject>
#
# <body>
#
# Types: feat, fix, refactor, test, docs, chore, style
```

### 8. Push and Create PR

```bash
git push origin feature/your-feature
```

Then open a PR in GitHub:
- Use the PR template (auto-populated)
- Fill in all sections
- Add relevant labels
- Request reviews from appropriate CODEOWNERS

### 9. Address Review Feedback
- AI reviewer will comment automatically
- Team members will review within 24 hours
- Address all comments
- Push new commits (don't force push)
- Mark conversations as resolved

### 10. Merge and Deploy

Once approved:
- Squash and merge to `develop`
- CI will automatically deploy to Dev environment
- Monitor Dev for issues
- Delete feature branch

## Database Migrations

If you modify database models:

```bash
cd backend

# Generate migration
alembic revision --autogenerate -m "add wire status field"

# Review the generated migration in alembic/versions/
# Edit if needed

# Test migration
alembic upgrade head

# Test rollback
alembic downgrade -1
alembic upgrade head
```

## Handling Merge Conflicts

If your feature branch has conflicts with `develop`:

```bash
git checkout feature/your-feature
git pull origin develop

# Resolve conflicts in your editor
# Run tests to ensure everything works
make all-checks

git add .
git commit -m "Merge develop and resolve conflicts"
git push
```

## Testing Features Together

If your feature depends on another developer's feature:

```bash
# Check out the other feature branch
git checkout feature/other-feature

# Merge it into your branch (locally only)
git checkout feature/your-feature
git merge feature/other-feature

# Test together
make all-checks
```

## Code Style Guidelines

### Python (Backend)
- Use type hints for all functions
- Follow PEP 8 (enforced by Ruff and Black)
- Line length: 100 characters
- Use async/await for database operations
- Write docstrings for public functions

### TypeScript (Frontend)
- Use strict TypeScript mode
- Define interfaces for all data structures
- Use functional components with hooks
- Follow Material-UI design patterns
- Keep components small and focused

## Questions?
- Ask in #dev-wire-app Slack channel
- Check existing PRs for examples
- Reach out to team leads
