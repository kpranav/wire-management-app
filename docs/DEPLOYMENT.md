# Deployment Guide

## Deployment Strategy

The Wire Management application uses a **branch-based deployment** strategy with four environments:

```
feature/* → develop → qa → uat → main
   (local)    (Dev)    (QA)  (UAT)  (Prod)
```

## Environment Overview

| Environment | Branch | Deploy Method | Purpose | Approvals |
|-------------|--------|---------------|---------|-----------|
| Dev | develop | Auto on push | Integration testing | None |
| QA | qa | Auto on push | Quality assurance | None |
| UAT | uat | Manual approval | User acceptance | 1 reviewer |
| Production | main | Manual approval | Live system | 2 reviewers + wait timer |

## Deployment Process

### 1. Deploy to Dev

**Trigger**: Push or merge to `develop` branch

```bash
git checkout develop
git pull origin develop
git merge feature/your-feature
git push origin develop
```

GitHub Actions will:
1. Run lint, type checks, and tests
2. Build Docker images
3. Push images to Docker Hub
4. SSH to EC2 and deploy to Dev environment

**Access**: http://YOUR-EC2-IP:3001

### 2. Deploy to QA

**Trigger**: Push or merge to `qa` branch

```bash
git checkout qa
git pull origin qa
git merge develop
git push origin qa
```

GitHub Actions will:
1. Run all checks
2. Build Docker images
3. Deploy to QA environment

**Access**: http://YOUR-EC2-IP:3002

### 3. Deploy to UAT

**Trigger**: Push to `uat` branch + manual approval

```bash
git checkout uat
git pull origin uat
git merge qa
git push origin uat
```

GitHub Actions will:
1. Run all checks
2. Build Docker images
3. **Wait for 1 reviewer approval** in GitHub UI
4. Deploy to UAT environment after approval

**Access**: http://YOUR-EC2-IP:3003

### 4. Deploy to Production

**Trigger**: Push to `main` branch + manual approval

```bash
git checkout main
git pull origin main
git merge uat
git push origin main
```

GitHub Actions will:
1. Run all checks
2. Build Docker images
3. **Wait for 2 reviewer approvals + 30-minute wait timer**
4. Deploy to Production after approval

**Access**: http://YOUR-EC2-IP:3000

## Manual Deployment (Emergency)

If CI/CD is down, you can deploy manually:

```bash
# SSH to EC2
ssh -i ~/.aws/kpranav_keypair_01.pem ec2-user@YOUR-EC2-IP

cd /home/ec2-user/wire-app

# Pull latest images
export DOCKERHUB_USERNAME=your-username
export IMAGE_TAG=latest

docker compose -f docker-compose.prod.yml pull

# Deploy
docker compose -f docker-compose.prod.yml up -d

# Verify deployment
docker ps
docker compose -f docker-compose.prod.yml logs -f
```

## Rollback Procedure

### Option 1: Deploy Previous Image

```bash
# SSH to EC2
ssh -i ~/.aws/kpranav_keypair_01.pem ec2-user@YOUR-EC2-IP

cd /home/ec2-user/wire-app

# Use previous git SHA
export IMAGE_TAG=<previous-git-sha>
export DOCKERHUB_USERNAME=your-username

docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### Option 2: Revert Git Commit

```bash
# Locally
git checkout main
git revert HEAD
git push origin main

# CI/CD will deploy the reverted version
```

## Database Migrations in Production

### Before Deploying Schema Changes

1. **Test migration locally**:
   ```bash
   cd backend
   alembic upgrade head
   alembic downgrade -1
   alembic upgrade head
   ```

2. **Test on Dev/QA/UAT** first

3. **Backup production database**:
   ```bash
   ssh ec2-user@YOUR-EC2-IP
   docker exec wire-postgres-prod pg_dump -U wireuser wire_prod > backup_$(date +%Y%m%d).sql
   ```

4. **Deploy to production** (migrations run automatically on container start)

### If Migration Fails

```bash
# SSH to EC2
docker exec -it wire-api-prod bash

# Check migration status
alembic current

# Manually run migration
alembic upgrade head

# Or rollback
alembic downgrade -1
```

## Monitoring Deployment

### Check Deployment Status

```bash
# View GitHub Actions
# Go to: https://github.com/your-org/wire-management-app/actions

# Check deployment logs in Actions UI
```

### Verify on EC2

```bash
ssh -i ~/.aws/kpranav_keypair_01.pem ec2-user@YOUR-EC2-IP

# Check running containers
docker ps

# Check container logs
docker logs wire-api-prod -f
docker logs wire-ui-prod -f

# Check container health
docker inspect wire-api-prod | grep Health
```

### Health Checks

```bash
# Check API health
curl http://YOUR-EC2-IP:8000/health

# Check frontend
curl http://YOUR-EC2-IP:3000

# Check specific environment
curl http://YOUR-EC2-IP:8001/health  # Dev
curl http://YOUR-EC2-IP:8002/health  # QA
curl http://YOUR-EC2-IP:8003/health  # UAT
```

## Deployment Checklist

Before deploying to production:

- [ ] All tests passing in CI
- [ ] Code reviewed by at least 2 team members
- [ ] AI code review feedback addressed
- [ ] Tested in Dev environment
- [ ] QA team signed off
- [ ] UAT testing completed
- [ ] Database backup created
- [ ] Migration tested (if applicable)
- [ ] Environment variables configured
- [ ] Monitoring alerts configured
- [ ] Rollback plan prepared
- [ ] Stakeholders notified
- [ ] Documentation updated

## Hotfix Deployment

For critical production bugs:

```bash
# Branch from main (not develop)
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug-description

# Fix the bug
# ... make changes ...

# Test thoroughly
make all-checks

# Push and create PR directly to main
git push origin hotfix/critical-bug-description

# Create PR to main branch
# Mark as urgent/hotfix
# Requires immediate review from 2 senior devs
```

After hotfix:
```bash
# Merge hotfix back to develop
git checkout develop
git merge main
git push origin develop
```

## Blue-Green Deployment (Future Enhancement)

For zero-downtime deployments, consider:

1. Run old version on ports 8000/3000
2. Deploy new version on ports 8100/3100
3. Test new version
4. Switch traffic (update nginx/load balancer)
5. Keep old version running for quick rollback
6. After verification, stop old version

## Environment-Specific Configuration

Each environment has its own:
- Database (separate PostgreSQL instance)
- Redis instance
- JWT secret
- Feature flags
- Docker Compose file

Configuration is managed via:
- Environment variables in docker-compose files
- GitHub Secrets for sensitive data
- `.env` files for local development
