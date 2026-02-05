# Branching Strategy

## Overview

This project uses a **multi-environment branching strategy** to ensure code quality and controlled deployments.

## Branch Structure

```
main (production)
  ↑
uat (user acceptance testing)
  ↑
qa (quality assurance)
  ↑
develop (development/integration)
  ↑
feature/* (individual features)
```

## Branch Descriptions

### main
- **Purpose**: Production-ready code
- **Deploys to**: Production environment (ports 8000/3000)
- **Protected**: Yes (requires 2 approvals)
- **Auto-deploy**: Yes (with manual approval)
- **Merge from**: `uat` branch only

### uat
- **Purpose**: User acceptance testing
- **Deploys to**: UAT environment (ports 8003/3003)
- **Protected**: Yes (requires 1 approval)
- **Auto-deploy**: Yes (with manual approval)
- **Merge from**: `qa` branch only

### qa
- **Purpose**: Quality assurance and regression testing
- **Deploys to**: QA environment (ports 8002/3002)
- **Protected**: Yes (requires 1 approval)
- **Auto-deploy**: Yes (automatic)
- **Merge from**: `develop` branch only

### develop
- **Purpose**: Integration of all features
- **Deploys to**: Dev environment (ports 8001/3001)
- **Protected**: Yes (requires 1 approval)
- **Auto-deploy**: Yes (automatic)
- **Merge from**: `feature/*` branches

### feature/*
- **Purpose**: Individual feature development
- **Deploys to**: Nowhere (local testing only)
- **Protected**: No
- **Auto-deploy**: No
- **Merge to**: `develop` branch via Pull Request

## Workflow Examples

### Normal Feature Development

```bash
# 1. Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/add-export

# 2. Develop and test locally
# ... make changes ...
make all-checks

# 3. Commit and push
git add .
git commit -m "feat: add CSV export functionality"
git push origin feature/add-export

# 4. Create PR to develop
# ... create PR on GitHub ...

# 5. After review and approval, merge to develop
# → Auto-deploys to Dev environment

# 6. Test in Dev, then promote to QA
git checkout qa
git pull origin qa
git merge develop
git push origin qa
# → Auto-deploys to QA environment

# 7. After QA testing, promote to UAT
git checkout uat
git pull origin uat
git merge qa
git push origin uat
# → Requires approval → Deploys to UAT

# 8. After UAT approval, promote to Production
git checkout main
git pull origin main
git merge uat
git push origin main
# → Requires 2 approvals → Deploys to Production
```

### Hotfix for Production

```bash
# 1. Branch from main (not develop!)
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# 2. Fix the issue
# ... make changes ...
make all-checks

# 3. Create PR directly to main
git push origin hotfix/critical-security-fix
# → Create PR to main

# 4. After urgent review (2 approvals), merge to main
# → Deploys to Production

# 5. Backport to develop
git checkout develop
git merge main
git push origin develop
```

### Multiple Developers Working in Parallel

**Developer 1:**
```bash
git checkout -b feature/add-filters
# ... work on filters ...
git push origin feature/add-filters
# Create PR → Gets merged first
```

**Developer 2:**
```bash
git checkout -b feature/add-export
# ... work on export ...

# Before merging, sync with develop
git pull origin develop  # Gets Developer 1's changes
# Resolve any conflicts
make all-checks

git push origin feature/add-export
# Create PR → Merges second
```

## Branch Protection Rules

Configure in GitHub: Settings → Branches → Branch protection rules

### For `develop`:
- ✅ Require a pull request before merging
- ✅ Require approvals: 1
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require status checks to pass before merging:
  - `backend-checks`
  - `frontend-checks`
- ✅ Require conversation resolution before merging
- ✅ Require linear history
- ✅ Do not allow bypassing the above settings
- ❌ Allow force pushes
- ❌ Allow deletions

### For `qa`, `uat`:
- Same as `develop`
- Require approvals: 1

### For `main`:
- Same as `develop`
- ✅ Require approvals: 2
- ✅ Require deployments to succeed: `production`
- ✅ Restrict who can push to matching branches

## Commit Message Convention

Follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvement
- `test`: Adding missing tests
- `chore`: Changes to build process or auxiliary tools

### Examples

```bash
# Simple feature
git commit -m "feat: add wire status filter"

# With scope
git commit -m "feat(backend): add rate limiting to wire endpoints"

# With body
git commit -m "fix(frontend): resolve WebSocket reconnection issue

The WebSocket was not properly handling disconnections.
Added exponential backoff for reconnection attempts.

Fixes #123"

# Breaking change
git commit -m "feat(api)!: change wire status enum values

BREAKING CHANGE: Wire status values changed from uppercase to lowercase
for consistency with API standards."
```

## Release Process

### Creating a Release

```bash
# On main branch after successful UAT
git checkout main
git pull origin main

# Tag the release
git tag -a v1.0.0 -m "Release v1.0.0 - Initial production release"
git push origin v1.0.0
```

### Semantic Versioning

- **Major version** (1.0.0): Breaking changes
- **Minor version** (0.1.0): New features, backward compatible
- **Patch version** (0.0.1): Bug fixes

## Keeping Branches in Sync

### Regular Maintenance

```bash
# Weekly: Update qa from develop
git checkout qa
git merge develop
git push origin qa

# Bi-weekly: Update uat from qa
git checkout uat
git merge qa
git push origin uat

# Monthly: Release to production
git checkout main
git merge uat
git push origin main
```

This ensures all environments stay relatively in sync and reduces merge conflicts.
