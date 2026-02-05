backend-lint:
	cd backend && ruff check . && black --check . && mypy app

backend-test:
	cd backend && pytest tests -v --cov=app

frontend-lint:
	cd frontend && npm run lint && npm run type-check

frontend-test:
	cd frontend && npm run test

all-checks: backend-lint backend-test frontend-lint frontend-test

install-backend:
	cd backend && pip install -r requirements-dev.txt

install-frontend:
	cd frontend && npm install

install: install-backend install-frontend

.PHONY: backend-lint backend-test frontend-lint frontend-test all-checks install-backend install-frontend install
