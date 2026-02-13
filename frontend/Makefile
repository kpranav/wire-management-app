lint:
	npm run lint

format:
	npm run format
	npm run lint -- --fix

type-check:
	npm run type-check

test:
	npm run test

format-check:
	npm run format:check

all-checks: lint format-check type-check test

.PHONY: lint format type-check test all-checks
