# Multi-Developer Collaboration Workflow

## Overview

This guide explains how multiple developers can work on different features simultaneously while maintaining code quality and avoiding conflicts.

## Parallel Development Model

Multiple developers work on separate feature branches in isolation, then integrate their changes through the `develop` branch.

```
Dev 1: feature/add-filters ────┐
                                ├──→ develop → Dev Environment
Dev 2: feature/export-csv  ────┤
                                │
Dev 3: feature/audit-log  ─────┘
```

## Daily Workflow

### Morning: Start with Latest Code

```bash
# Pull latest changes from develop
git checkout develop
git pull origin develop

# Create your feature branch
git checkout -b feature/your-feature
```

### During Development: Stay Synced

```bash
# Pull develop into your feature branch (at least daily)
git checkout feature/your-feature
git pull origin develop

# Resolve any conflicts
# ... edit conflicting files ...

# Run tests to ensure everything works
make all-checks

git add .
git commit -m "Merge latest develop changes"
```

### End of Day: Push Your Work

```bash
# Commit your changes
git add .
git commit -m "feat: work in progress on your feature"

# Push to remote (backs up your work)
git push origin feature/your-feature
```

## Collaboration Scenarios

### Scenario 1: Independent Features (No Conflicts)

**Developer 1** working on filters:
```bash
git checkout -b feature/add-filters
# Edit: backend/app/routers/wires.py (add filter parameter)
# Edit: frontend/src/components/WireList.tsx (add filter UI)
git commit -m "feat: add status filters"
git push origin feature/add-filters
# Create PR → Merges first
```

**Developer 2** working on export:
```bash
git checkout -b feature/export-csv
# Edit: backend/app/routers/wires.py (add export endpoint)
# Edit: frontend/src/components/WireList.tsx (add export button)
git pull origin develop  # Gets Dev 1's changes
# No conflicts - different parts of files
git commit -m "feat: add CSV export"
git push origin feature/export-csv
# Create PR → Merges second
```

**Result**: Both features in `develop`, both deployed to Dev together.

### Scenario 2: Conflicting Changes (Same File, Same Lines)

**Developer 1** adds a method:
```python
# backend/app/routers/wires.py
@router.get("/wires")
async def list_wires(status: Optional[str] = None):
    # Filter by status
    ...
```

**Developer 2** adds a different method:
```python
# backend/app/routers/wires.py
@router.get("/wires")
async def list_wires(page: int = 1):
    # Add pagination
    ...
```

**Resolution**:
```bash
# Dev 2 pulls develop after Dev 1 merges
git pull origin develop

# Git shows conflict:
# <<<<<<< HEAD
# async def list_wires(page: int = 1):
# =======
# async def list_wires(status: Optional[str] = None):
# >>>>>>> develop

# Resolve by combining both features:
async def list_wires(
    page: int = 1, 
    status: Optional[str] = None
):
    # Both features working together
    ...

git add .
git commit -m "Merge develop, combine filter and pagination"
make all-checks  # Ensure it works
git push
```

### Scenario 3: Database Migration Conflicts

**Developer 1** creates migration:
```bash
alembic revision --autogenerate -m "add status index"
# Creates: 0002_add_status_index.py
```

**Developer 2** creates migration:
```bash
alembic revision --autogenerate -m "add amount index"
# Creates: 0002_add_amount_index.py
```

**Conflict**: Both migrations numbered `0002`

**Resolution**:
```bash
# After Dev 1 merges, Dev 2 must rebase

# Delete your migration
rm alembic/versions/0002_add_amount_index.py

# Pull latest (has Dev 1's 0002)
git pull origin develop

# Regenerate your migration (becomes 0003)
alembic revision --autogenerate -m "add amount index"

# Verify migration sequence
alembic upgrade head
alembic downgrade base
alembic upgrade head

git add alembic/versions/0003_add_amount_index.py
git commit -m "Rebase migration after status index merge"
git push
```

## Testing Features Together

### Before Merging: Integration Test

If your feature depends on another feature that's not yet in `develop`:

```bash
# Checkout the other feature branch
git checkout feature/other-feature

# Temporarily merge both features locally
git checkout feature/your-feature
git merge feature/other-feature

# Test together
make all-checks
docker compose -f docker-compose.dev.yml up -d

# If it works, coordinate with other dev to merge in order
# Don't push this merge - it's just for testing
```

### After Both Merge: Verify in Dev

```bash
# Both features are now in develop
# Automatically deployed to Dev environment
# Access: http://YOUR-EC2-IP:3001

# Test the integrated features together
# Report any integration issues
```

## Communication Best Practices

### Daily Standup

Share what you're working on:
```
"I'm working on CSV export. I'll be modifying WireList.tsx and adding 
a new endpoint. Should be ready for PR tomorrow."
```

This helps others avoid conflicts.

### Before Starting a Feature

Check GitHub:
- **Issues**: Is someone already working on this?
- **PRs**: Are there related PRs in progress?
- **Slack/Teams**: Ask if anyone is working on the same area

### During Development

- Push your branch daily (even if not ready for PR)
- Others can see what you're working on: `git fetch && git branch -a`
- Comment in PR if you need feedback early: "WIP - early feedback welcome"

## Feature Flags for Partial Deployment

If Feature A is ready but Feature B isn't, use feature flags:

```python
# backend/app/config.py
FEATURE_CSV_EXPORT = False  # Feature B not ready
FEATURE_ADVANCED_FILTERS = True  # Feature A ready
```

```yaml
# docker-compose.dev.yml (test both)
environment:
  FEATURE_CSV_EXPORT: "true"
  FEATURE_ADVANCED_FILTERS: "true"

# docker-compose.qa.yml (only stable features)
environment:
  FEATURE_CSV_EXPORT: "false"  # Not ready for QA yet
  FEATURE_ADVANCED_FILTERS: "true"
```

This allows:
- Both features merged to `develop`
- Both deployed to Dev
- Only Feature A enabled in QA/UAT/Prod
- Feature B remains in codebase, tested in Dev only

## Merge Strategy

### Squash and Merge (Recommended)

When merging PR to `develop`:
- Click "Squash and merge"
- Combines all commits into one
- Clean history on `develop`
- Easier to revert if needed

### Regular Merge

When merging between environment branches:
```bash
git checkout qa
git merge develop  # Regular merge, preserves history
```

## Code Review Collaboration

### For PR Author

1. **Self-review first**: Review your own diff before requesting review
2. **Write clear description**: Explain what, why, and how to test
3. **Respond to feedback**: Address all comments or explain why not
4. **Keep PR small**: < 500 lines of changes if possible
5. **Update based on feedback**: Push additional commits

### For Reviewers

1. **Review within 24 hours**: Don't block other developers
2. **Be constructive**: Suggest improvements, don't just criticize
3. **Test locally**: Check out the branch and test if unsure
4. **Approve when satisfied**: Don't request endless changes

## Handling Long-Running Features

If a feature takes > 1 week:

### Option 1: Split into Smaller PRs

```bash
feature/user-roles-complete
  ↓
feature/user-roles-backend  ← Merge first
feature/user-roles-frontend ← Merge second
feature/user-roles-tests    ← Merge third
```

### Option 2: Keep Syncing

```bash
# Sync with develop frequently
git checkout feature/long-feature
git pull origin develop  # Do this daily

# This keeps your branch up to date
# Reduces conflict resolution at the end
```

## Coordination Tools

### GitHub Issues

- Create issues for features before starting
- Assign yourself to the issue
- Reference issue in PR: "Closes #123"

### GitHub Project Board

Move cards through workflow:
```
Backlog → In Progress → In Review → Done
```

### Slack/Teams Integration

Set up notifications:
- PR created: Notify #dev-wire-app
- PR approved: Notify team
- Deploy to Dev: Notify team
- Deploy to Prod: Notify #announcements

## Conflict Prevention Tips

1. **Communicate early**: Tell team what you're working on
2. **Keep branches short**: Merge within 2-3 days if possible
3. **Pull frequently**: Sync with `develop` at least daily
4. **Modular code**: Good separation reduces overlapping changes
5. **Coordinate migrations**: Only one dev creates migration at a time
6. **Use feature flags**: Deploy code disabled until ready

## Example: Full Collaboration Flow

**Monday Morning:**
```
Dev 1: Creates feature/add-filters (modifies WireList.tsx, wires.py)
Dev 2: Creates feature/export-csv (modifies WireList.tsx, wires.py)
Dev 3: Creates feature/audit-log (modifies new files)
```

**Tuesday:**
```
Dev 1: Opens PR for filters
    ↓
AI Review: Posts feedback automatically
    ↓
Dev 1: Addresses feedback, pushes changes
    ↓
Team Review: 1 approval
    ↓
Dev 1: Merges to develop → Deploys to Dev
```

**Wednesday:**
```
Dev 2: Pulls develop into feature/export-csv
    ↓
Dev 2: Resolves conflicts with filters feature
    ↓
Dev 2: Tests locally (both features work together)
    ↓
Dev 2: Opens PR for export
    ↓
AI Review + Team Review
    ↓
Dev 2: Merges to develop → Deploys to Dev (now has both features)
```

**Thursday:**
```
Dev 3: Pulls develop (gets filters + export)
    ↓
Dev 3: Tests audit-log with other features
    ↓
Dev 3: Opens PR
    ↓
Dev 3: Merges to develop → All 3 features in Dev
```

**Friday:**
```
Team: Tests all 3 features together in Dev
    ↓
Team: Merges develop → qa
    ↓
QA Team: Tests in QA environment over weekend
```

**Following Week:**
```
QA passes → Merge qa → uat
UAT testing by stakeholders
UAT passes → Merge uat → main (requires 2 approvals)
Production deployment (all 3 features released together)
```

This flow ensures:
- Developers work independently (isolated locally)
- Features integrate continuously (Dev environment)
- Quality gates at each stage (QA → UAT → Prod)
- Team collaboration through code review
- Automated testing and deployment
