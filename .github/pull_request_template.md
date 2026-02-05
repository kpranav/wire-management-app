## Description
Brief description of what this PR does and why.

## Type of Change
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Related Issues
Closes #(issue number)

## Changes Made
- Change 1
- Change 2
- Change 3

## How to Test Locally
1. Checkout this branch: `git checkout feature/branch-name`
2. Install dependencies: `make install` (if new deps added)
3. Run local stack: `docker compose -f docker-compose.dev.yml up -d`
4. Test the feature:
   - Navigate to http://localhost:3001
   - [Specific test steps]
5. Run tests: `make all-checks`

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Integration Testing
- [ ] Tested locally with latest `develop` branch merged in
- [ ] No conflicts with other recent features
- [ ] Database migrations work correctly (if applicable)
- [ ] Backward compatible (or breaking changes documented)

## Checklist Before Requesting Review
- [ ] Code follows project style guidelines (lint passes)
- [ ] Self-review performed
- [ ] Comments added for complex logic
- [ ] Tests added/updated (unit + integration)
- [ ] All tests pass locally
- [ ] Documentation updated (if needed)
- [ ] No console errors or warnings
- [ ] Pulled latest `develop` and resolved conflicts
- [ ] Database migrations created (if schema changes)
- [ ] Environment variables documented (if new vars added)

## Post-Merge Tasks
- [ ] Monitor Dev environment after merge
- [ ] Update related documentation
- [ ] Notify team in Slack
