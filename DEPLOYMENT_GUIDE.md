# 🚀 PRD QC Table Transformer - Deployment Guide

## 🐳 Docker Deployment (PRODUCTION READY)

### Quick Start - Production Server
```bash
# Clone or upload project to your server
git clone <your-repo> && cd table_to_json

# Deploy to production (runs on port 80)
./deploy-production.sh

# Access your app
http://YOUR_SERVER_IP
```

### Development Deployment
```bash
# Deploy for development/testing (port 5000)
./docker-deploy.sh

# Access locally
http://localhost:5000
```

## 📋 All Available Scripts

### Docker Scripts
| Script | Purpose | Port | Usage |
|--------|---------|------|-------|
| `docker-build.sh` | Build Docker image | - | `./docker-build.sh` |
| `docker-deploy.sh` | Development deployment | 5000 | `./docker-deploy.sh` |
| `deploy-production.sh` | **Production deployment** | 80 | `./deploy-production.sh` |
| `docker-stop.sh` | Stop all containers | - | `./docker-stop.sh` |

### Test & Debug Scripts  
| Script | Purpose | Usage |
|--------|---------|-------|
| `test_docker.py` | Test Docker deployment | `python3 test_docker.py` |
| `fix_port_issue.py` | Fix port 5000 conflicts | `python3 fix_port_issue.py` |
| `test_web_app.py` | Test web functionality | `python3 test_web_app.py` |

### Local Development Scripts
| Script | Purpose | Usage |
|--------|---------|-------|
| `start_web_app.py` | Local web app | `python3 start_web_app.py` |
| `quick_test.py` | Test transformation | `python3 quick_test.py` |
| `transform_prd_to_template.py` | CLI transformation | `python3 transform_prd_to_template.py input.xlsx output.xlsx` |

## 🌐 Server Deployment Steps

### 1. Prepare Server
```bash
# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Upload Project
```bash
# Upload all files to server
scp -r table_to_json/ user@your-server-ip:/home/user/

# Or use git
git clone your-repo-url
cd table_to_json
```

### 3. Deploy
```bash
# Make scripts executable
chmod +x *.sh

# Deploy to production
./deploy-production.sh
```

### 4. Configure Firewall
```bash
# Open port 80 (production)
sudo ufw allow 80/tcp

# Or port 5000 (development)
sudo ufw allow 5000/tcp
```

## 🔧 Management Commands

### Docker Compose Commands
```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check status
docker-compose -f docker-compose.prod.yml ps

# Restart service
docker-compose -f docker-compose.prod.yml restart

# Stop service
docker-compose -f docker-compose.prod.yml down

# Update deployment
docker-compose -f docker-compose.prod.yml up --build -d
```

### Container Management
```bash
# View running containers
docker ps

# View resource usage
docker stats

# Access container shell
docker exec -it table_to_json_prd-transformer_1 /bin/bash

# View container logs
docker logs table_to_json_prd-transformer_1
```

## 📊 Monitoring & Troubleshooting

### Health Checks
```bash
# Check if service is running
curl http://localhost/
curl http://YOUR_SERVER_IP/

# Check container health
docker ps
docker inspect <container_id> | grep Health
```

### Common Issues
| Problem | Solution |
|---------|----------|
| Port 80 in use | `sudo lsof -ti:80 \| xargs kill -9` |
| Container won't start | Check logs: `docker-compose logs` |
| Permission denied | `sudo usermod -aG docker $USER` |
| Can't access from outside | Check firewall: `sudo ufw status` |

### Log Locations
- **Container logs**: `docker-compose logs`
- **Application logs**: `./logs/` directory (production)
- **Upload files**: `./uploads/` directory

## 🔒 Security Considerations

### Production Security
```bash
# Enable firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp  # For HTTPS

# Regular updates
sudo apt update && sudo apt upgrade
docker-compose pull && docker-compose up -d
```

### SSL Certificate (Optional)
```bash
# Install certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Update docker-compose.prod.yml to use SSL
# (uncomment nginx section and configure)
```

## 📈 Performance Optimization

### Resource Limits
Edit `docker-compose.prod.yml`:
```yaml
services:
  prd-transformer:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

### Scaling
```bash
# Scale to multiple instances
docker-compose -f docker-compose.prod.yml up -d --scale prd-transformer=3

# Add load balancer (nginx)
# (uncomment nginx section in docker-compose.prod.yml)
```

## ✅ Verification Checklist

- [ ] Docker & Docker Compose installed
- [ ] Project uploaded to server
- [ ] Scripts executable (`chmod +x *.sh`)
- [ ] Production deployed (`./deploy-production.sh`)
- [ ] Firewall configured (port 80 open)
- [ ] Service accessible via browser
- [ ] File upload/download working
- [ ] Container auto-restart enabled

## 🆘 Support

### Get Help
```bash
# Test deployment
python3 test_docker.py

# Check port issues  
python3 fix_port_issue.py

# View all available commands
ls -la *.sh
```

**Your PRD QC Table Transformer is now ready for production! 🎉** 