# Setup & Deployment Guide

## 📋 Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [OpenAI API Configuration](#openai-api-configuration)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Security Checklist](#security-checklist)

## 🛠️ Local Development Setup

### 1. Environment Setup

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Streamlit Secrets

```bash
# Copy example secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit with your OpenAI API key
# Windows: notepad .streamlit\secrets.toml
# macOS/Linux: nano .streamlit/secrets.toml
```

**secrets.toml content:**
```toml
OPENAI_API_KEY = "sk-your-actual-key-here"
```

### 3. Run Development Server

```bash
streamlit run app.py
```

Access at: http://localhost:8501

### 4. Development Workflow

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Format code
black . 
isort .

# Lint code
flake8 utils/ app.py

# Run tests
pytest tests/ -v
```

## 🔑 OpenAI API Configuration

### Getting Your API Key

1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (you won't see it again!)
4. Add to `.streamlit/secrets.toml`

### Cost Management

**Monitor Usage:**
```
https://platform.openai.com/account/billing/overview
```

**Set Rate Limits:**
```
https://platform.openai.com/account/billing/limits
```

**Estimated Costs:**
- GPT-4: $0.03 per 1K input tokens, $0.06 per 1K output tokens
- GPT-3.5-turbo: $0.0005 per 1K input, $0.0015 per 1K output
- Typical claim analysis: 500-1000 tokens = $0.02-$0.05

### Best Practices

✅ Use GPT-3.5-turbo for high-volume screening
✅ Cache common prompts to save costs
✅ Batch analyses during off-peak hours
✅ Monitor token usage regularly
✅ Set spending limits in API dashboard

## 🚀 Production Deployment

### Option 1: Streamlit Cloud (Recommended for Small Teams)

1. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Connect to Streamlit Cloud**
- Go to https://share.streamlit.io
- Click "Create app"
- Connect your GitHub repo
- Select main/app.py

3. **Configure Secrets in Cloud**
- Go to app settings
- Copy content of `.streamlit/secrets.toml`
- Paste into cloud secrets manager

**Deployment URL Example:**
```
https://healthcare-claim-hub.streamlit.app
```

### Option 2: AWS EC2

```bash
# Launch EC2 instance (Ubuntu 22.04, t3.medium or larger)

# SSH into instance
ssh -i key.pem ubuntu@your-instance-ip

# Install dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-venv

# Clone repository
git clone <your-repo-url>
cd python-streamlit-gpt-dataviz-agent

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create secrets file
nano .streamlit/secrets.toml
# Add: OPENAI_API_KEY = "sk-..."

# Create systemd service
sudo nano /etc/systemd/system/healthclaim.service
```

**healthclaim.service:**
```ini
[Unit]
Description=HealthClaim Analytics Hub
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/python-streamlit-gpt-dataviz-agent
Environment="PATH=/home/ubuntu/python-streamlit-gpt-dataviz-agent/venv/bin"
ExecStart=/home/ubuntu/python-streamlit-gpt-dataviz-agent/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --logger.level=warning
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable healthclaim
sudo systemctl start healthclaim
sudo systemctl status healthclaim

# View logs
sudo journalctl -u healthclaim -f
```

### Option 3: Heroku (Deprecated - Use Streamlit Cloud Instead)

### Option 4: Azure App Service

```bash
# Create resource group
az group create --name rg-healthclaim --location eastus

# Create App Service Plan
az appservice plan create --name plan-healthclaim --resource-group rg-healthclaim --sku B1 --is-linux

# Create Web App
az webapp create --resource-group rg-healthclaim \
  --plan plan-healthclaim --name healthclaim-hub \
  --runtime "PYTHON:3.10"

# Deploy from GitHub
az webapp deployment source config-zip \
  --resource-group rg-healthclaim \
  --name healthclaim-hub \
  --src deploy.zip

# Configure secrets
az webapp config appsettings set \
  --resource-group rg-healthclaim \
  --name healthclaim-hub \
  --settings OPENAI_API_KEY="sk-..."
```

## 🐳 Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create .streamlit config
RUN mkdir -p .streamlit

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Create .streamlit/config.toml for Docker

```toml
[logger]
level = "warning"

[client]
showErrorDetails = false

[server]
port = 8501
headless = true
runOnSave = true
maxUploadSize = 200
enableXsrfProtection = true
```

### Build and Run Docker Container

```bash
# Build image
docker build -t healthclaim-hub:latest .

# Run container with secrets
docker run -d \
  --name healthclaim \
  -p 8501:8501 \
  -e OPENAI_API_KEY="sk-your-key" \
  healthclaim-hub:latest

# View logs
docker logs -f healthclaim

# Stop container
docker stop healthclaim
```

### Docker Compose (Multi-container Setup)

```yaml
version: '3.8'

services:
  streamlit:
    build: .
    ports:
      - "8501:8501"
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:latest
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - streamlit
    restart: unless-stopped
```

## 🔒 Security Checklist

### Before Deployment

- [ ] Remove all hardcoded secrets from code
- [ ] Use `.streamlit/secrets.toml` for API keys
- [ ] Add `.streamlit/secrets.toml` to `.gitignore`
- [ ] Enable HTTPS/TLS for all connections
- [ ] Set up authentication (OAuth, SSO, or basic auth)
- [ ] Configure rate limiting
- [ ] Enable CORS properly
- [ ] Use environment-specific configurations
- [ ] Review data validation in `utils/data.py`
- [ ] Test with sample non-sensitive data first

### Network Security

- [ ] Deploy behind firewall
- [ ] Use VPN for internal access
- [ ] Implement IP whitelisting
- [ ] Use Web Application Firewall (WAF)
- [ ] Enable DDoS protection
- [ ] Use reverse proxy (nginx, CloudFlare)
- [ ] Require HTTPS only (no HTTP)

### Access Control

- [ ] Implement user authentication
- [ ] Use role-based access control (RBAC)
- [ ] Audit all access logs
- [ ] Limit API rate by user
- [ ] Implement session timeouts
- [ ] Require strong passwords
- [ ] Use multi-factor authentication (MFA)

### Data Security

- [ ] Encrypt data in transit (TLS 1.3+)
- [ ] Encrypt data at rest (if storing)
- [ ] Sanitize all user inputs
- [ ] Avoid logging PII
- [ ] Implement data retention policies
- [ ] Regular backups
- [ ] Data access logging

### Compliance

- [ ] HIPAA compliance verified
- [ ] GDPR compliance for EU data
- [ ] Regular security audits
- [ ] Incident response plan
- [ ] Data breach notification plan
- [ ] Third-party risk assessment

## 📊 Monitoring & Maintenance

### Application Monitoring

```bash
# Watch logs
streamlit run app.py --logger.level=debug

# Monitor performance
# Use New Relic, DataDog, or similar
```

### API Usage Monitoring

Check dashboard: https://platform.openai.com/account/billing/overview

Set up alerts for:
- High API costs
- Rate limit errors
- Authentication failures

### Regular Maintenance

- Weekly: Check API usage and costs
- Monthly: Update dependencies (`pip list --outdated`)
- Quarterly: Security audit
- Annually: Compliance review

## 🆘 Troubleshooting

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8501 | xargs kill -9
```

### Module Import Errors

```bash
# Reinstall dependencies
pip install --upgrade --force-reinstall -r requirements.txt

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
```

### Streamlit Cache Issues

```bash
# Clear cache
rm -rf ~/.streamlit/cache/*

# Or in app:
import streamlit as st
st.cache_data.clear()
```

### API Connection Issues

```bash
# Test connection
python -c "import openai; openai.api_key='sk-...'; print(openai.Model.list())"
```

---

**For more help, see README.md and .github/copilot-instructions.md**
