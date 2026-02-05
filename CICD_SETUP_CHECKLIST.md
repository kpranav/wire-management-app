# CI/CD Setup Checklist

This guide walks you through setting up the complete CI/CD pipeline for your Wire Management application.

## ✅ Prerequisites (Already Done)
- [x] Code pushed to GitHub: https://github.com/kpranav/wire-management-app
- [x] Branches created: `main`, `develop`, `qa`, `uat`
- [x] GitHub Actions workflows in `.github/workflows/`
- [x] EC2 instance available

## 🔧 Step 1: Configure GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**

### Required Secrets (Click "New repository secret" for each):

#### Docker Hub Credentials
1. **`DOCKERHUB_USERNAME`**
   - Value: Your Docker Hub username
   - Used for: Pushing Docker images

2. **`DOCKERHUB_TOKEN`**
   - Value: Your Docker Hub access token
   - How to get it:
     - Go to https://hub.docker.com/settings/security
     - Click "New Access Token"
     - Name it "GitHub Actions"
     - Copy the token (save it securely!)

#### EC2 Deployment Credentials
3. **`EC2_HOST`**
   - Value: Your EC2 public IP or hostname
   - Example: `54.123.45.67` or `ec2-54-123-45-67.compute-1.amazonaws.com`

4. **`EC2_USERNAME`**
   - Value: `ec2-user` (for Amazon Linux) or `ubuntu` (for Ubuntu)

5. **`EC2_SSH_KEY`**
   - Value: Contents of your SSH private key
   - From: `/Users/pranav/source/aws/kpranav_keypair_01.pem`
   - How to get it:
     ```bash
     cat /Users/pranav/source/aws/kpranav_keypair_01.pem
     ```
   - Copy the entire output including `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----`

#### AI Code Review
6. **`OPENAI_API_KEY`**
   - Value: Your OpenAI API key
   - How to get it:
     - Go to https://platform.openai.com/api-keys
     - Click "Create new secret key"
     - Name it "Wire App CI/CD"
     - Copy the key (save it securely!)
   - Note: This is optional - if not provided, AI code review will be skipped

#### GitHub Token (Already Available)
7. **`GITHUB_TOKEN`**
   - This is automatically provided by GitHub Actions
   - No action needed

## 🌍 Step 2: Configure GitHub Environments

Go to your repository → **Settings** → **Environments**

**Important:** Only UAT and Production need GitHub Environments (for manual approvals). Dev and QA auto-deploy using defaults from their docker-compose files.

### Environment Configuration Summary

| Environment | Branch | GitHub Environment? | Secrets Source | Approvals | Auto-Deploy |
|-------------|--------|---------------------|----------------|-----------|-------------|
| **Dev** | `develop` | ❌ No | docker-compose.dev.yml | 0 | ✅ Yes |
| **QA** | `qa` | ❌ No | docker-compose.qa.yml | 0 | ✅ Yes |
| **UAT** | `uat` | ✅ Yes | GitHub Environment `uat` | 1 | ❌ Manual |
| **Production** | `main` | ✅ Yes | GitHub Environment `production` | 2 | ❌ Manual |

### Create Environments (Click "New environment" for each):

#### 1. `uat` Environment
- Click "New environment"
- Name: `uat`
- Click "Configure environment"
- **Protection rules**:
  - ✅ Enable "Required reviewers"
  - Add 1 reviewer (yourself or team member)
  - ✅ Enable "Deployment branches and tags"
    - Selected branches: `uat` only
- **Environment secrets** (Click "Add secret" for each):
  - Name: `UAT_DATABASE_URL`  
    Value: `postgresql+asyncpg://wireuser:uatpass789@postgres-uat:5432/wire_uat`
  - Name: `UAT_REDIS_URL`  
    Value: `redis://redis-uat:6379/0`
  - Name: `UAT_JWT_SECRET`  
    Value: Generate using: `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`
- Click "Save protection rules"

#### 2. `production` Environment
- Click "New environment"
- Name: `production`
- Click "Configure environment"
- **Protection rules**:
  - ✅ Enable "Required reviewers"
  - Add 2 reviewers (yourself and/or team members)
  - ✅ Enable "Wait timer": 5 minutes (gives time to cancel if needed)
  - ✅ Enable "Deployment branches and tags"
    - Selected branches: `main` only
- **Environment secrets** (Click "Add secret" for each):
  - Name: `PROD_DATABASE_URL`  
    Value: `postgresql+asyncpg://wireuser:<STRONG_PROD_PASSWORD>@postgres-prod:5432/wire_prod`
  - Name: `PROD_REDIS_URL`  
    Value: `redis://redis-prod:6379/0`
  - Name: `PROD_JWT_SECRET`  
    Value: Generate using: `python3 -c "import secrets; print(secrets.token_urlsafe(96))"`
- Click "Save protection rules"

### What About Dev and QA?

**Dev and QA environments DO NOT need GitHub Environments** because:
- They auto-deploy without approvals
- They use default credentials from `docker-compose.dev.yml` and `docker-compose.qa.yml`
- No additional secrets needed

### Complete Environment Credentials Reference

Here's what credentials each environment uses:

#### Dev Environment (from docker-compose.dev.yml)
```
Database: postgresql+asyncpg://wireuser:devpass123@postgres-dev:5432/wire_dev
Redis: redis://redis-dev:6379/0
JWT_SECRET: dev-secret-key-change-in-production
Ports: 8001 (API), 3001 (UI)
```

#### QA Environment (from docker-compose.qa.yml)
```
Database: postgresql+asyncpg://wireuser:qapass456@postgres-qa:5432/wire_qa
Redis: redis://redis-qa:6379/0
JWT_SECRET: qa-secret-key-change-in-production
Ports: 8002 (API), 3002 (UI)
```

#### UAT Environment (from GitHub Environment secrets)
```
UAT_DATABASE_URL: postgresql+asyncpg://wireuser:uatpass789@postgres-uat:5432/wire_uat
UAT_REDIS_URL: redis://redis-uat:6379/0
UAT_JWT_SECRET: <Generate 64-char random string>
Ports: 8003 (API), 3003 (UI)
```

#### Production Environment (from GitHub Environment secrets)
```
PROD_DATABASE_URL: postgresql+asyncpg://wireuser:<STRONG_PASSWORD>@postgres-prod:5432/wire_prod
PROD_REDIS_URL: redis://redis-prod:6379/0
PROD_JWT_SECRET: <Generate 128-char random string>
Ports: 8000 (API), 3000 (UI)
```

**Note:** Generate secure secrets using:
```bash
# For UAT JWT secret (64 characters)
python3 -c "import secrets; print(secrets.token_urlsafe(48))"

# For Production JWT secret (128 characters)
python3 -c "import secrets; print(secrets.token_urlsafe(96))"

# For Production database password (32 characters)
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

## 🖥️ Step 3: Set Up EC2 Instance

SSH into your EC2 instance and follow the setup:

```bash
# SSH into EC2
ssh -i /Users/pranav/source/aws/kpranav_keypair_01.pem ec2-user@YOUR_EC2_IP
```

### Install Docker (if not already done)

```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install docker -y

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker ec2-user

# Log out and log back in
exit
# SSH back in
```

### Install Docker Compose

```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

### Create Application Directories

```bash
# Create directories for each environment
mkdir -p ~/wire-app-dev
mkdir -p ~/wire-app-qa
mkdir -p ~/wire-app-uat
mkdir -p ~/wire-app-prod

# Create directory for Docker Compose files
mkdir -p ~/wire-app-compose
```

### Configure EC2 Security Groups

Make sure your EC2 security group allows inbound traffic on these ports:

| Port | Service | Source | Purpose |
|------|---------|--------|---------|
| 22 | SSH | Your IP | SSH access |
| 8000 | API (Prod) | 0.0.0.0/0 | Production API |
| 3000 | UI (Prod) | 0.0.0.0/0 | Production UI |
| 8001 | API (Dev) | Your IP | Development API |
| 3001 | UI (Dev) | Your IP | Development UI |
| 8002 | API (QA) | Your IP | QA API |
| 3002 | UI (QA) | Your IP | QA UI |
| 8003 | API (UAT) | Your IP | UAT API |
| 3003 | UI (UAT) | Your IP | UAT UI |

To configure:
1. Go to AWS Console → EC2 → Security Groups
2. Find your instance's security group
3. Edit inbound rules
4. Add the ports above

## 🧪 Step 4: Test the CI/CD Pipeline

### Test 1: Run CI Checks

The CI checks will run automatically on every push/PR. To trigger manually:

```bash
# Make a small change
cd /Users/pranav/source/wire-management-app
echo "# CI/CD Pipeline Active" >> README.md

# Commit and push to develop
git checkout develop
git add README.md
git commit -m "Test CI/CD pipeline"
git push origin develop
```

Then go to GitHub → **Actions** tab and watch the workflow run:
- ✅ Backend checks (lint, type-check, test)
- ✅ Frontend checks (lint, type-check, test)
- ✅ Build Docker images
- ✅ Deploy to Dev environment

### Test 2: Deploy to QA

```bash
# Merge develop to qa
git checkout qa
git merge develop
git push origin qa
```

Watch in GitHub Actions - should auto-deploy to QA.

### Test 3: Deploy to UAT (Requires Approval)

```bash
# Merge qa to uat
git checkout uat
git merge qa
git push origin uat
```

- Go to GitHub → Actions
- Find the workflow run
- Click "Review deployments"
- Approve the UAT deployment

### Test 4: Deploy to Production (Requires 2 Approvals + Wait Timer)

```bash
# Merge uat to main
git checkout main
git merge uat
git push origin main
```

- Wait for CI checks to pass
- Approve deployment (requires 2 reviewers)
- Wait 5 minutes (wait timer)
- Production deployment starts

## 🔍 Step 5: Verify Deployments on EC2

After a deployment runs, SSH into EC2 and check:

```bash
# Check running containers
docker ps

# Check Dev environment
curl http://localhost:8001/health  # API
curl http://localhost:3001         # UI

# Check logs
cd ~/wire-app-dev
docker-compose logs -f
```

## 🚨 Step 6: Set Up Branch Protection Rules

Go to GitHub → **Settings** → **Branches** → **Add branch protection rule**

### Protect `main` (Production)
- Branch name pattern: `main`
- ✅ Require pull request before merging
- ✅ Require approvals: 2
- ✅ Require status checks to pass:
  - `backend-checks`
  - `frontend-checks`
  - `build-images`
- ✅ Require branches to be up to date before merging
- ✅ Include administrators
- ✅ Require linear history
- Click "Create"

### Protect `uat`
- Branch name pattern: `uat`
- ✅ Require pull request before merging
- ✅ Require approvals: 1
- ✅ Require status checks to pass
- Click "Create"

### Protect `qa`
- Branch name pattern: `qa`
- ✅ Require pull request before merging
- ✅ Require approvals: 1
- Click "Create"

### Protect `develop`
- Branch name pattern: `develop`
- ✅ Require pull request before merging
- ✅ Require status checks to pass
- Click "Create"

## 📋 Quick Reference: Required GitHub Secrets

Copy this checklist for GitHub Secrets configuration:

```
Repository Secrets (Settings → Secrets and variables → Actions):
☐ DOCKERHUB_USERNAME - Your Docker Hub username
☐ DOCKERHUB_TOKEN - Docker Hub token with Read/Write permissions
☐ EC2_HOST - EC2 public IP address
☐ EC2_USERNAME - ec2-user (Amazon Linux) or ubuntu
☐ EC2_SSH_KEY - Contents of your .pem file
☐ OPENAI_API_KEY - OpenAI API key (optional, for AI code review)

Environment: uat (Settings → Environments → uat):
☐ UAT_DATABASE_URL - Database connection string for UAT
☐ UAT_REDIS_URL - Redis connection string for UAT
☐ UAT_JWT_SECRET - Secure random string (64+ chars)
☐ Required reviewers: 1 person
☐ Deployment branches: uat only

Environment: production (Settings → Environments → production):
☐ PROD_DATABASE_URL - Database connection string for Production
☐ PROD_REDIS_URL - Redis connection string for Production
☐ PROD_JWT_SECRET - Very secure random string (128+ chars)
☐ Required reviewers: 2 people
☐ Wait timer: 5 minutes
☐ Deployment branches: main only

Note: Dev and QA environments don't need GitHub Environments - they use
defaults from docker-compose.dev.yml and docker-compose.qa.yml
```

## 🎯 Next Steps

1. **Configure GitHub Secrets** (15 minutes)
2. **Set up GitHub Environments** (10 minutes)
3. **Configure EC2 Security Groups** (5 minutes)
4. **Set up Branch Protection Rules** (10 minutes)
5. **Test CI/CD with a push to develop** (5 minutes)
6. **Verify deployment on EC2** (5 minutes)

Total time: ~50 minutes

## 🆘 Troubleshooting

### CI/CD workflow fails
- Check GitHub Actions logs for specific error
- Verify all secrets are correctly set
- Ensure EC2 is accessible via SSH

### Deployment fails
- Check EC2 has Docker and Docker Compose installed
- Verify security groups allow SSH (port 22)
- Check EC2 has enough disk space: `df -h`
- Check EC2 has enough memory: `free -h`

### Docker image build fails
- Check Docker Hub credentials are correct
- Verify you're logged into Docker Hub
- Check repository name in docker-compose files

## 📚 Additional Resources

- Full EC2 Setup: `docs/EC2_SETUP.md`
- Deployment Guide: `docs/DEPLOYMENT.md`
- Architecture Overview: `docs/ARCHITECTURE.md`
- API Documentation: `docs/API_DOCUMENTATION.md`

---

**Once setup is complete, your CI/CD pipeline will be fully operational!** 🚀
