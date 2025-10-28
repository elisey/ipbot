# Production Deployment Guide

This guide covers deploying the IP Bot to a Linux server using Docker Compose.

## Prerequisites

### Server Requirements

- Linux server (Ubuntu 20.04+ recommended)
- Docker Engine 20.10+
- Docker Compose v2.0+
- Network access to Telegram API
- At least 512MB RAM
- 1GB disk space

### Install Docker and Docker Compose

```bash
# Update package index
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add current user to docker group (optional, for non-root usage)
sudo usermod -aG docker $USER

# Install Docker Compose plugin
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

## Deployment Steps

### 1. Set Up Project Directory

```bash
# Create application directory
sudo mkdir -p /opt/ipbot
cd /opt/ipbot

# Download production docker-compose file
curl -O https://raw.githubusercontent.com/elisey/ipbot/main/docker-compose.prod.yml

# Or if you have the repository cloned
cp docker-compose.prod.yml /opt/ipbot/
```

### 2. Configure Environment Variables

Create a `.env` file with your credentials:

```bash
# Create .env file
nano .env
```

Add the following configuration:

```bash
TELEGRAM_TOKEN=your_bot_token_from_botfather
TELEGRAM_OWNER_ID=your_telegram_user_id
FETCHER_STRATEGY_ORDER=ipify
SERVER_REPLY_FORMAT=🌐 Your public IP is: {ip}
```

**Security:** Set proper file permissions:

```bash
chmod 600 .env
```

### 3. Pull the Latest Image

```bash
docker compose -f docker-compose.prod.yml pull
```

### 4. Start the Service

```bash
# Start in detached mode
docker compose -f docker-compose.prod.yml up -d

# Verify the container is running
docker compose -f docker-compose.prod.yml ps
```

### 5. Verify Deployment

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs -f

# You should see messages like:
# INFO - Bot started and polling for updates
```

Test by sending `/ip` command to your bot in Telegram.

## Service Management

### View Logs

```bash
# Follow logs in real-time
docker compose -f docker-compose.prod.yml logs -f

# View last 100 lines
docker compose -f docker-compose.prod.yml logs --tail 100

# View logs for specific time range
docker compose -f docker-compose.prod.yml logs --since 1h
```

### Restart Service

```bash
docker compose -f docker-compose.prod.yml restart
```

### Stop Service

```bash
docker compose -f docker-compose.prod.yml down
```

### Update to Latest Version

```bash
# Pull latest image
docker compose -f docker-compose.prod.yml pull

# Recreate container with new image
docker compose -f docker-compose.prod.yml up -d

# Clean up old images
docker image prune -f
```

### Update to Specific Version

```bash
# Edit docker-compose.prod.yml and change:
# image: ghcr.io/elisey/ipbot:0.1.1

# Then update
docker compose -f docker-compose.prod.yml up -d
```

## System Integration

### Run as Systemd Service

For automatic startup on boot, create a systemd service:

```bash
sudo nano /etc/systemd/system/ipbot.service
```

Add the following content:

```ini
[Unit]
Description=IP Bot Telegram Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/ipbot
ExecStart=/usr/bin/docker compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable on boot
sudo systemctl enable ipbot

# Start service
sudo systemctl start ipbot

# Check status
sudo systemctl status ipbot
```

## Monitoring

### Health Checks

The production compose file includes health checks. View health status:

```bash
docker inspect ipbot --format='{{.State.Health.Status}}'
```

### Resource Usage

Monitor container resource consumption:

```bash
# Real-time stats
docker stats ipbot

# One-time snapshot
docker stats --no-stream ipbot
```

### Check Container Status

```bash
# Detailed container info
docker inspect ipbot

# Check if container is running
docker compose -f docker-compose.prod.yml ps
```

## Backup and Recovery

### Backup Configuration

```bash
# Backup .env file
sudo cp /opt/ipbot/.env /opt/ipbot/.env.backup

# Or backup to remote location
scp /opt/ipbot/.env user@backup-server:/backups/ipbot/
```

### Restore from Backup

```bash
# Stop service
docker compose -f docker-compose.prod.yml down

# Restore configuration
sudo cp /opt/ipbot/.env.backup /opt/ipbot/.env

# Start service
docker compose -f docker-compose.prod.yml up -d
```

## Security Best Practices

1. **File Permissions:**
   ```bash
   # Restrict .env file access
   chmod 600 /opt/ipbot/.env
   chown root:root /opt/ipbot/.env
   ```

2. **Regular Updates:**
   ```bash
   # Check for updates weekly
   docker compose -f docker-compose.prod.yml pull
   docker compose -f docker-compose.prod.yml up -d
   ```

3. **Firewall Configuration:**
   ```bash
   # The bot only makes outbound connections
   # No inbound ports need to be opened
   # Ensure outbound HTTPS (443) is allowed
   ```

4. **Log Rotation:**
   Logs are automatically rotated (max 3 files of 10MB each).

## Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker compose -f docker-compose.prod.yml logs

# Verify .env file exists and has correct permissions
ls -la /opt/ipbot/.env

# Verify Docker daemon is running
sudo systemctl status docker
```

### Bot Not Responding

```bash
# Check if container is healthy
docker inspect ipbot --format='{{.State.Health.Status}}'

# Verify network connectivity
docker exec ipbot ping -c 3 api.telegram.org

# Check configuration
docker exec ipbot env | grep TELEGRAM
```

### High Memory Usage

```bash
# Check current usage
docker stats --no-stream ipbot

# Restart container to clear memory
docker compose -f docker-compose.prod.yml restart
```

### View Health Check Logs

```bash
# Check health check status
docker inspect ipbot | grep -A 10 Health
```

## Performance Tuning

### Adjust Resource Limits

Edit `docker-compose.prod.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'      # Increase CPU limit
      memory: 512M     # Increase memory limit
```

Then restart:

```bash
docker compose -f docker-compose.prod.yml up -d
```

## Uninstall

```bash
# Stop and remove containers
docker compose -f docker-compose.prod.yml down

# Remove images
docker rmi ghcr.io/elisey/ipbot:latest

# Remove project directory
sudo rm -rf /opt/ipbot

# Remove systemd service (if configured)
sudo systemctl disable ipbot
sudo rm /etc/systemd/system/ipbot.service
sudo systemctl daemon-reload
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/elisey/ipbot/issues
- Documentation: https://github.com/elisey/ipbot
