# SRM Softclub - Production Deployment Guide

## 📋 Prerequisites

Server: `157.180.29.248`
User: `soft`
Password: `soft@2025`

## 🚀 Deployment Steps

### 1. Upload Project to Server

**Option A: Using rsync (recommended)**
```bash
# From your local machine
rsync -avz --exclude '.venv' --exclude '__pycache__' --exclude '.git' \
  /Users/nodir/Desktop/srm-softclub/ \
  soft@157.180.29.248:/opt/srm-softclub/
```

**Option B: Using Git**
```bash
# On server
ssh soft@157.180.29.248
cd /opt
git clone <your-repo-url> srm-softclub
```

### 2. Run Deployment Script

```bash
# On server
ssh soft@157.180.29.248
cd /opt/srm-softclub
chmod +x deploy.sh setup_service.sh
./deploy.sh
```

This will:
- ✅ Install Python, PostgreSQL, Git
- ✅ Create database `softclub_crm`
- ✅ Setup virtual environment
- ✅ Install all dependencies
- ✅ Run migrations
- ✅ Load 50 demo students

### 3. Configure Environment

```bash
# Edit .env file
nano /opt/srm-softclub/.env

# Update GROQ_API_KEY:
GROQ_API_KEY=gsk_your_actual_key_here
```

### 4. Setup Systemd Service

```bash
sudo ./setup_service.sh
```

### 5. Verify Deployment

```bash
# Check service status
sudo systemctl status srm-softclub

# Test API
curl http://localhost:8000/api/students | jq

# View logs
sudo journalctl -u srm-softclub -f
```

## 🌐 Access

- **API Base:** http://157.180.29.248:8000
- **Swagger Docs:** http://157.180.29.248:8000/docs
- **Students List:** http://157.180.29.248:8000/api/students
- **Analysis:** http://157.180.29.248:8000/api/students/2006/analysis

## 🔧 Useful Commands

```bash
# Restart service
sudo systemctl restart srm-softclub

# Stop service
sudo systemctl stop srm-softclub

# View logs
sudo journalctl -u srm-softclub -f

# Check if API is running
curl http://localhost:8000/health

# PostgreSQL access
sudo -u postgres psql softclub_crm
```

## 🐛 Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u srm-softclub -n 50

# Check .env file
cat /opt/srm-softclub/.env

# Test manually
cd /opt/srm-softclub
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Database connection error
```bash
# Verify PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U softclub -d softclub_crm -h localhost

# Check database exists
sudo -u postgres psql -l | grep softclub
```

### Model not loading
```bash
# Verify model file exists
ls -lh /opt/srm-softclub/models/trained/churn_model.json

# If missing, copy from local:
scp models/trained/churn_model.json soft@157.180.29.248:/opt/srm-softclub/models/trained/
```

## 📊 Quick Test

```bash
# Get all students
curl http://157.180.29.248:8000/api/students

# Analyze student (ID 2006 - high risk)
curl http://157.180.29.248:8000/api/students/2006/analysis | jq

# Analyze student (ID 2036 - low risk)
curl http://157.180.29.248:8000/api/students/2036/analysis | jq
```

## ✅ Success Criteria

- [ ] API responds on port 8000
- [ ] 50 students in database
- [ ] Model predictions working
- [ ] LLM explanations generating
- [ ] Service auto-starts on reboot
