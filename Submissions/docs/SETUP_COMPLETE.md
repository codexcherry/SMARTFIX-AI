# SmartFix-AI: Complete Setup Guide

## 🚀 Quick Start

Get SmartFix-AI running in under 10 minutes with our automated setup process.

### Prerequisites

- **Python 3.11+** (recommended: Python 3.12)
- **Node.js 18+** (for frontend)
- **5GB+ free disk space** (for AI models)
- **Internet connection** (for initial setup)
- **Git** (optional, for cloning)

### Automated Setup (Recommended)

#### Windows
```bash
# Download and run the setup script
curl -o setup.bat https://raw.githubusercontent.com/codexcherry/SMARTFIX-AI/main/setup.bat
setup.bat
```

#### Linux/macOS
```bash
# Download and run the setup script
curl -o setup.sh https://raw.githubusercontent.com/codexcherry/SMARTFIX-AI/main/setup.sh
chmod +x setup.sh
./setup.sh
```

#### Manual Python Setup
```bash
# Clone the repository
git clone https://github.com/codexcherry/SMARTFIX-AI.git
cd SmartFix-AI

# Run the Python setup script
python setup.py
```

## 📋 Manual Setup Guide

### Step 1: Environment Setup

#### 1.1 Clone Repository
```bash
git clone https://github.com/codexcherry/SMARTFIX-AI.git
cd SmartFix-AI
```

#### 1.2 Create Virtual Environment
```bash
# Backend virtual environment
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

#### 1.3 Install Backend Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install additional dependencies for offline mode
pip install -r requirements-offline.txt
```

#### 1.4 Install Frontend Dependencies
```bash
# Navigate to frontend directory
cd ../frontend

# Install Node.js dependencies
npm install

# Install additional packages for enhanced features
npm install @mui/material @emotion/react @emotion/styled
npm install framer-motion react-router-dom
```

### Step 2: Configuration

#### 2.1 Environment Variables

Create a `.env` file in the backend directory:

```bash
# Application Settings
DEBUG=true
ENVIRONMENT=development
SECRET_KEY=your_super_secret_key_change_in_production_12345
APP_NAME=SmartFix-AI
APP_VERSION=1.0.0

# Database Configuration
DATABASE_URL=sqlite:///./smartfix_ai.db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=smartfix_ai
POSTGRES_USER=smartfix_user
POSTGRES_PASSWORD=your_secure_password

# Cache Configuration
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600

# AI Service API Keys
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
SERPAPI_KEY=your_serpapi_key_here

# Twilio Configuration (Optional)
TWILIO_SID=your_twilio_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_FROM_PHONE=your_twilio_phone_number
TWILIO_TO_PHONE=your_phone_number

# Galaxy Autopilot Configuration
GALAXY_AUTOPILOT_ENABLED=true
GALAXY_AUTOPILOT_DEVICE_ID=galaxy_device_001
GALAXY_AUTOPILOT_LEARNING_RATE=0.1
GALAXY_AUTOPILOT_EPSILON=0.1
GALAXY_AUTOPILOT_DISCOUNT_FACTOR=0.9

# Samsung API Keys (Optional)
SAMSUNG_DEVICE_CARE_API_KEY=your_samsung_device_care_key
KNOX_API_KEY=your_knox_key
SAMSUNG_FOTA_API_KEY=your_fota_key
SAMSUNG_CLOUD_API_KEY=your_cloud_key
GALAXY_NPU_API_KEY=your_npu_key

# Offline Mode Configuration
OFFLINE_MODE_ENABLED=true
OFFLINE_MODELS_PATH=./offline_models
OFFLINE_MODELS_DOWNLOAD_AUTO=true

# Feature Flags
SURFACE_HEALING_ENABLED=true
DEEP_HEALING_ENABLED=true
IMMUNE_SYSTEM_ENABLED=true
REGENERATIVE_LAYER_ENABLED=true
SELF_OPTIMIZATION_ENABLED=true
NETWORK_AWARE_ASSISTANT_ENABLED=true
ENHANCED_VOICE_ASSISTANT_ENABLED=true

# Monitoring and Health Checks
HEALTH_CHECK_INTERVAL=30
METRICS_COLLECTION_INTERVAL=60
THREAT_SCAN_INTERVAL=300
PERFORMANCE_ANALYSIS_INTERVAL=120

# Retry and Rate Limiting
MAX_RETRIES=3
RETRY_DELAY=1.0
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000"]

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
REACT_APP_VERSION=1.0.0

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/smartfix_ai.log

# Security Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Upload Configuration
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif,text/plain,application/pdf

# Performance Configuration
WORKER_PROCESSES=4
WORKER_CONNECTIONS=1000
KEEP_ALIVE_TIMEOUT=65
```

#### 2.2 API Key Setup

##### Hugging Face API Key
1. Go to [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. Click "New token"
3. Give it a name (e.g., "SmartFix-AI")
4. Select "Read" role
5. Copy the token and add to `.env` file

##### Google Gemini API Key
1. Visit [Google AI Studio](https://ai.google.dev/)
2. Sign in with your Google account
3. Go to "Get API key"
4. Create a new API key
5. Copy the key and add to `.env` file

##### SerpAPI Key
1. Go to [SerpAPI](https://serpapi.com/)
2. Sign up for an account
3. Navigate to your dashboard
4. Copy your API key and add to `.env` file

##### Twilio (Optional - for SMS notifications)
1. Sign up at [Twilio](https://www.twilio.com/)
2. Get your Account SID and Auth Token from the dashboard
3. Get a Twilio phone number
4. Add these to your `.env` file

### Step 3: Database Setup

#### 3.1 SQLite (Default - No Setup Required)
SQLite database will be created automatically when you first run the application.

#### 3.2 PostgreSQL (Optional - for Production)
```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Windows:
# Download from https://www.postgresql.org/download/windows/

# Create database and user
sudo -u postgres psql
CREATE DATABASE smartfix_ai;
CREATE USER smartfix_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE smartfix_ai TO smartfix_user;
\q
```

#### 3.3 Redis (Optional - for Caching)
```bash
# Install Redis
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis

# Windows:
# Download from https://github.com/microsoftarchive/redis/releases

# Start Redis
redis-server
```

### Step 4: AI Models Setup

#### 4.1 Download Offline Models
```bash
# Navigate to backend directory
cd backend

# Download models automatically
python download_offline_models.py --download-only

# Or download models interactively
python download_offline_models.py
```

#### 4.2 Verify Model Installation
```bash
# Check model status
python -c "
from app.services.offline_service import offline_service
import asyncio

async def check_models():
    status = await offline_service.get_status()
    print('Models loaded:', status['models_loaded'])
    print('AI available:', status['ai_available'])

asyncio.run(check_models())
"
```

### Step 5: Start Services

#### 5.1 Start Backend Server
```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 5.2 Start Frontend Server
```bash
# Open new terminal and navigate to frontend directory
cd frontend

# Start the development server
npm start
```

#### 5.3 Verify Installation
```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
# Open browser and go to http://localhost:3000
```

## 🐳 Docker Setup

### Docker Compose (Recommended)

#### 5.1 Create Docker Compose File
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - DATABASE_URL=postgresql://smartfix_user:password@db:5432/smartfix_ai
      - REDIS_URL=redis://redis:6379
      - HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - SERPAPI_KEY=${SERPAPI_KEY}
    volumes:
      - ./backend:/app
      - offline_models:/app/offline_models
      - logs:/app/logs
    depends_on:
      - db
      - redis
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=smartfix_ai
      - POSTGRES_USER=smartfix_user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  offline_models:
  logs:
```

#### 5.2 Start with Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Individual Docker Containers

#### 5.3 Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p logs offline_models

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 5.4 Frontend Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Install serve for production
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Start command
CMD ["serve", "-s", "build", "-l", "3000"]
```

## 🔧 Configuration Options

### Advanced Configuration

#### 6.1 Performance Tuning
```bash
# Backend performance settings
WORKER_PROCESSES=4
WORKER_CONNECTIONS=1000
KEEP_ALIVE_TIMEOUT=65
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=100

# Database connection pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Cache settings
CACHE_TTL=3600
CACHE_MAX_SIZE=1000
CACHE_CLEANUP_INTERVAL=300
```

#### 6.2 Security Configuration
```bash
# Security headers
SECURITY_HEADERS_ENABLED=true
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=Content-Type,Authorization,X-Requested-With

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10
RATE_LIMIT_STORAGE=redis

# File upload security
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif,text/plain,application/pdf
SCAN_UPLOADS_FOR_MALWARE=true
```

#### 6.3 Monitoring Configuration
```bash
# Health checks
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10
HEALTH_CHECK_RETRIES=3

# Metrics collection
METRICS_ENABLED=true
METRICS_COLLECTION_INTERVAL=60
METRICS_RETENTION_DAYS=30
METRICS_EXPORT_FORMAT=prometheus

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/smartfix_ai.log
LOG_ROTATION_SIZE=10MB
LOG_ROTATION_COUNT=5
```

## 🧪 Testing Setup

### 7.1 Unit Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/ -v --cov=app --cov-report=html

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v
```

### 7.2 Frontend Tests
```bash
# Navigate to frontend directory
cd frontend

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

### 7.3 API Testing
```bash
# Test API endpoints
curl -X GET "http://localhost:8000/health"
curl -X POST "http://localhost:8000/api/v1/query/text" \
  -H "Content-Type: application/json" \
  -d '{"text_query": "My computer is running slowly", "user_id": "test_user"}'
```

## 🔍 Troubleshooting

### Common Issues

#### 8.1 Python Version Issues
```bash
# Check Python version
python --version

# If version is too old, install Python 3.11+
# Ubuntu/Debian:
sudo apt-get install python3.11 python3.11-venv python3.11-pip

# macOS:
brew install python@3.11

# Windows:
# Download from https://www.python.org/downloads/
```

#### 8.2 Dependency Installation Issues
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Install system dependencies first
# Ubuntu/Debian:
sudo apt-get install build-essential libffi-dev libssl-dev

# macOS:
xcode-select --install
```

#### 8.3 Port Already in Use
```bash
# Check what's using port 8000
# Windows:
netstat -ano | findstr :8000

# Linux/macOS:
lsof -i :8000

# Kill the process
# Windows:
taskkill /PID <PID> /F

# Linux/macOS:
kill -9 <PID>
```

#### 8.4 Model Download Issues
```bash
# Check internet connectivity
ping huggingface.co

# Check disk space
df -h

# Check HuggingFace API key
echo $HUGGINGFACE_API_KEY

# Try downloading models individually
python -c "
from huggingface_hub import hf_hub_download
hf_hub_download(repo_id='distilbert-base-uncased', filename='config.json')
"
```

#### 8.5 Database Connection Issues
```bash
# Check database connection
python -c "
import sqlite3
conn = sqlite3.connect('smartfix_ai.db')
print('Database connection successful')
conn.close()
"

# For PostgreSQL:
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://user:pass@localhost/smartfix_ai')
print('PostgreSQL connection successful')
conn.close()
"
```

### Debug Mode

#### 8.6 Enable Debug Logging
```python
# Add to your .env file
DEBUG=true
LOG_LEVEL=DEBUG

# Or set environment variable
export DEBUG=true
export LOG_LEVEL=DEBUG
```

#### 8.7 Check Service Status
```bash
# Check backend health
curl http://localhost:8000/health

# Check specific services
curl http://localhost:8000/api/v1/smart/status
curl http://localhost:8000/api/v1/galaxy-autopilot/status
curl http://localhost:8000/api/v1/offline/status
```

## 📊 Performance Optimization

### 9.1 Backend Optimization
```bash
# Use production WSGI server
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Enable caching
pip install redis
# Configure Redis in .env

# Use connection pooling
# Configure database pool settings
```

### 9.2 Frontend Optimization
```bash
# Build for production
npm run build

# Use production server
npm install -g serve
serve -s build -l 3000

# Enable compression
npm install compression
```

### 9.3 Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_queries_user_id ON queries(user_id);
CREATE INDEX idx_queries_created_at ON queries(created_at);
CREATE INDEX idx_brain_memory_problem_hash ON brain_memory(problem_hash);
CREATE INDEX idx_healing_actions_device_id ON healing_actions(device_id);
CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp);
```

## 🚀 Production Deployment

### 10.1 Environment Preparation
```bash
# Set production environment variables
export ENVIRONMENT=production
export DEBUG=false
export SECRET_KEY=your_very_secure_secret_key_here
export DATABASE_URL=postgresql://user:pass@db-host:5432/smartfix_ai
export REDIS_URL=redis://redis-host:6379
```

### 10.2 Security Hardening
```bash
# Use HTTPS
# Configure SSL certificates
# Enable security headers
# Set up firewall rules
# Configure rate limiting
# Enable authentication
```

### 10.3 Monitoring Setup
```bash
# Install monitoring tools
pip install prometheus-client
pip install sentry-sdk

# Configure monitoring
# Set up alerts
# Configure log aggregation
# Set up performance monitoring
```

### 10.4 Backup Strategy
```bash
# Database backups
pg_dump smartfix_ai > backup_$(date +%Y%m%d_%H%M%S).sql

# Model backups
tar -czf models_backup_$(date +%Y%m%d_%H%M%S).tar.gz offline_models/

# Configuration backups
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
```

## 📚 Additional Resources

### Documentation
- [API Reference](docs/API_REFERENCE_COMPLETE.md)
- [Architecture Guide](docs/ARCHITECTURE_COMPREHENSIVE.md)
- [Galaxy Autopilot Guide](docs/GALAXY_AUTOPILOT_COMPLETE.md)
- [Offline Mode Guide](docs/OFFLINE_MODE.md)

### Support
- [GitHub Issues](https://github.com/codexcherry/SMARTFIX-AI/issues)
- [Email Support](mailto:support@smartfix-ai.com)

### Contributing
- [Contributing Guide](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Development Setup](docs/development_setup.md)

---

## Important Concept Clarification

**Galaxy Autopilot is a conceptual system software design** intended to operate as **phone backend system software**, not as a webpage or web application. The Galaxy Autopilot concept represents an innovative approach to autonomous device maintenance that would be integrated directly into Samsung Galaxy devices as system-level software, similar to how Device Care or Knox Security operates within the Android framework.

**Note**: The current implementation includes a web-based demonstration interface solely for concept visualization and hackathon presentation purposes. In actual deployment, Galaxy Autopilot would function as native Android system software integrated into Samsung Galaxy devices.

---

This comprehensive setup guide provides everything needed to get SmartFix-AI running in any environment, from development to production. Follow the steps carefully and refer to the troubleshooting section if you encounter any issues.
