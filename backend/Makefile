lint:
	ruff check .
	black --check .

format:
	black .
	ruff check . --fix

type-check:
	mypy app

test:
	pytest tests -v --cov=app --cov-report=term-missing

test-fast:
	pytest tests -v -x

all-checks: lint type-check test

.PHONY: lint format type-check test test-fast all-checks
