# EC2 Setup Guide

This guide explains how to set up your EC2 instance for deploying the Wire Management application.

## Prerequisites

- AWS account
- EC2 instance launched (Amazon Linux 2 or Ubuntu recommended)
- SSH key pair (e.g., `your-key.pem`)
- EC2 instance with at least 4GB RAM (t3.medium recommended)

## 1. Initial EC2 Setup

### SSH into your EC2 instance

```bash
ssh -i /path/to/your-key.pem ec2-user@YOUR_EC2_PUBLIC_IP
```

### Update system packages

```bash
# For Amazon Linux 2
sudo yum update -y

# For Ubuntu
sudo apt-get update && sudo apt-get upgrade -y
```

## 2. Install Docker

### For Amazon Linux 2

```bash
# Install Docker
sudo yum install docker -y

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add ec2-user to docker group
sudo usermod -aG docker ec2-user

# Log out and log back in for group changes to take effect
exit
# SSH back in
```

### For Ubuntu

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in
exit
# SSH back in
```

## 3. Install Docker Compose

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

## 4. Create Application Directory

```bash
# Create app directory
mkdir -p /home/ec2-user/wire-app
cd /home/ec2-user/wire-app

# Create backups directory for database backups
mkdir -p backups
```

## 5. Copy Docker Compose Files

From your local machine:

```bash
# Copy all docker-compose files to EC2
scp -i /path/to/your-key.pem docker-compose.*.yml ec2-user@YOUR_EC2_IP:/home/ec2-user/wire-app/
```

## 6. Configure Security Group

In AWS Console, configure your EC2 Security Group with the following inbound rules:

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| SSH | TCP | 22 | Your IP | SSH access |
| Custom TCP | TCP | 8001 | 0.0.0.0/0 | Dev API |
| Custom TCP | TCP | 3001 | 0.0.0.0/0 | Dev UI |
| Custom TCP | TCP | 8002 | 0.0.0.0/0 | QA API |
| Custom TCP | TCP | 3002 | 0.0.0.0/0 | QA UI |
| Custom TCP | TCP | 8003 | 0.0.0.0/0 | UAT API |
| Custom TCP | TCP | 3003 | 0.0.0.0/0 | UAT UI |
| Custom TCP | TCP | 8000 | 0.0.0.0/0 | Prod API |
| Custom TCP | TCP | 3000 | 0.0.0.0/0 | Prod UI |

**Note:** For production, restrict sources to specific IP ranges for security.

## 7. Set Up GitHub Secrets

In your GitHub repository, go to Settings → Secrets and variables → Actions, and add:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username | `yourusername` |
| `DOCKERHUB_TOKEN` | Docker Hub access token | `dckr_pat_...` |
| `EC2_HOST` | Your EC2 public IP | `54.123.45.67` |
| `EC2_SSH_KEY` | Contents of your SSH key | `-----BEGIN RSA PRIVATE KEY-----...` |
| `QA_DB_PASSWORD` | QA database password | `secure_password_123` |
| `QA_JWT_SECRET` | QA JWT secret | `random_secret_key` |
| `UAT_DB_PASSWORD` | UAT database password | `secure_password_456` |
| `UAT_JWT_SECRET` | UAT JWT secret | `random_secret_key` |
| `PROD_DB_PASSWORD` | Production database password | `secure_password_789` |
| `PROD_JWT_SECRET` | Production JWT secret | `random_secret_key` |
| `OPENAI_API_KEY` | OpenAI API key (for AI code review) | `sk-...` |

### Generate Secure Passwords

```bash
# Generate secure random passwords
openssl rand -base64 32
```

## 8. First Deployment

### Manual test deployment

```bash
# SSH into EC2
ssh -i /path/to/your-key.pem ec2-user@YOUR_EC2_IP

cd /home/ec2-user/wire-app

# Set environment variables
export DOCKERHUB_USERNAME=yourusername
export IMAGE_TAG=latest

# Start Dev environment
docker compose -f docker-compose.dev.yml up -d

# Check logs
docker compose -f docker-compose.dev.yml logs -f

# Check running containers
docker ps
```

### Verify Deployment

Access your application:
- Dev UI: `http://YOUR-EC2-IP:3001`
- Dev API: `http://YOUR-EC2-IP:8001`
- API Docs: `http://YOUR-EC2-IP:8001/docs`

## 9. Set Up Automated Deployments

Once GitHub Actions is configured with the secrets above:

1. Push to `develop` branch → Auto-deploys to Dev
2. Push to `qa` branch → Auto-deploys to QA
3. Push to `uat` branch → Requires approval → Deploys to UAT
4. Push to `main` branch → Requires 2 approvals → Deploys to Production

## 10. Monitoring and Maintenance

### View logs

```bash
# View logs for specific environment
docker compose -f docker-compose.dev.yml logs -f api-dev

# View all logs
docker compose -f docker-compose.dev.yml logs -f
```

### Database backup

```bash
# Create backup
docker exec wire-postgres-prod pg_dump -U wireuser wire_prod > /home/ec2-user/wire-app/backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker exec -i wire-postgres-prod psql -U wireuser wire_prod < backup_file.sql
```

### Restart services

```bash
# Restart specific environment
docker compose -f docker-compose.dev.yml restart

# Restart specific service
docker compose -f docker-compose.dev.yml restart api-dev
```

### Clean up old images

```bash
# Remove unused images
docker system prune -a

# Remove old containers
docker container prune
```

## Troubleshooting

### Containers won't start

```bash
# Check logs
docker compose -f docker-compose.dev.yml logs

# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker
```

### Port already in use

```bash
# Find process using port
sudo netstat -tlnp | grep :8001

# Kill process
sudo kill -9 <PID>
```

### Out of disk space

```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a --volumes
```

## Security Best Practices

1. **Change default passwords** - Update all database and JWT secrets
2. **Restrict Security Group** - Limit access to specific IPs in production
3. **Enable SSH key only** - Disable password authentication
4. **Regular updates** - Keep EC2 and Docker updated
5. **Enable CloudWatch** - Monitor logs and metrics
6. **Set up alerts** - Configure AWS CloudWatch alarms
7. **Regular backups** - Automate database backups

## Next Steps

1. Set up domain name and SSL certificates (Let's Encrypt)
2. Configure CloudWatch for monitoring
3. Set up automated database backups
4. Configure log aggregation
5. Set up alerting for errors and downtime
