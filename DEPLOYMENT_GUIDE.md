# 🚀 SmartFix-AI Deployment Guide

## ⚠️ **IMPORTANT SECURITY NOTICE**

**Before deploying to GitHub, ensure you have:**

1. ✅ **Removed all API keys** from `config.py` (already done)
2. ✅ **Created `.env` file** with your actual credentials
3. ✅ **Never commit `.env` file** to version control
4. ✅ **Use environment variables** for all sensitive data

## 📋 **Pre-Deployment Checklist**

### 1. Environment Setup
- [ ] Copy `env.example` to `.env`
- [ ] Fill in your actual API keys in `.env`
- [ ] Verify `.env` is in `.gitignore`
- [ ] Test local setup works

### 2. API Keys Required
You need to obtain these API keys:

- **HuggingFace**: https://huggingface.co/settings/tokens
- **Google Gemini**: https://ai.google.dev/
- **SerpAPI**: https://serpapi.com/
- **Twilio**: https://console.twilio.com/

### 3. System Requirements
- **Python 3.8+**
- **Node.js 16+**
- **Tesseract OCR** (for image processing)
- **Redis** (optional, for caching)

## 🛠️ **Installation Steps**

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR (Windows)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki

# Install Tesseract OCR (Linux)
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# Install Tesseract OCR (macOS)
brew install tesseract tesseract-lang

# Create .env file
cp ../env.example .env
# Edit .env with your API keys

# Run the application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > .env

# Start development server
npm start
```

## 🔧 **Configuration**

### Environment Variables (.env)
```bash
# Required API Keys
HUGGINGFACE_API_KEY=your_huggingface_key_here
GEMINI_API_KEY=your_gemini_key_here
SERPAPI_KEY=your_serpapi_key_here

# Twilio (for notifications)
TWILIO_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_FROM_PHONE=your_twilio_number

# Security
SECRET_KEY=your_secure_secret_key_here

# Database
DATABASE_URL=sqlite:///./smartfix_ai.db

# Frontend
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## 🐳 **Docker Deployment (Optional)**

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./smartfix_ai.db
    volumes:
      - ./backend:/app
      - ./data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api/v1
    depends_on:
      - backend
```

## 🌐 **Production Deployment**

### 1. Environment Variables
Set these in your production environment:
```bash
export ENVIRONMENT=production
export DEBUG=false
export SECRET_KEY=your_production_secret_key
export DATABASE_URL=postgresql://user:pass@host:port/db
export REDIS_URL=redis://your-redis-host:6379
```

### 2. Database Migration
```bash
# For PostgreSQL
pip install psycopg2-binary
alembic upgrade head
```

### 3. Static Files
```bash
# Build frontend
cd frontend
npm run build

# Serve static files with nginx or similar
```

## 🔒 **Security Best Practices**

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive data
3. **Enable HTTPS** in production
4. **Set up proper CORS** origins
5. **Use strong secret keys**
6. **Enable rate limiting**
7. **Monitor logs** for suspicious activity

## 🚨 **Troubleshooting**

### Common Issues

1. **Tesseract not found**
   ```bash
   # Verify installation
   tesseract --version
   
   # Set path in Python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

2. **API key errors**
   - Check `.env` file exists
   - Verify API keys are correct
   - Check API quotas and limits

3. **Database connection issues**
   - Verify database URL
   - Check database permissions
   - Ensure database exists

4. **CORS errors**
   - Update `CORS_ORIGINS` in config
   - Check frontend API URL

## 📊 **Monitoring**

### Health Checks
- Backend: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

### Logs
- Backend logs: Check console output
- Frontend logs: Browser developer tools

## 🎯 **Next Steps**

1. **Test locally** with your API keys
2. **Deploy to staging** environment
3. **Set up monitoring** and logging
4. **Configure backups**
5. **Deploy to production**

## 📞 **Support**

If you encounter issues:
1. Check the logs
2. Verify environment variables
3. Test API endpoints individually
4. Check system requirements

---

## Important Concept Clarification

**Galaxy Autopilot is a conceptual system software design** intended to operate as **phone backend system software**, not as a webpage or web application. The Galaxy Autopilot concept represents an innovative approach to autonomous device maintenance that would be integrated directly into Samsung Galaxy devices as system-level software, similar to how Device Care or Knox Security operates within the Android framework.

**Note**: The current implementation includes a web-based demonstration interface solely for concept visualization and hackathon presentation purposes. In actual deployment, Galaxy Autopilot would function as native Android system software integrated into Samsung Galaxy devices.

---

## From CodexCoders Team

We are honored to present SmartFix-AI to Samsung Electronics, a company that has consistently demonstrated visionary leadership in consumer electronics innovation. Samsung's commitment to pushing technological boundaries and creating devices that enhance human experiences aligns perfectly with our vision of autonomous device intelligence.

Samsung's legacy of innovation, from pioneering smartphone technology to advancing AI and semiconductor capabilities, inspires us to contribute to the next chapter of intelligent device management. We believe SmartFix-AI represents the future of device maintenance that Samsung can lead, transforming how users interact with technology and ensuring Galaxy devices remain at the forefront of innovation.

**Remember**: Always test in a development environment before deploying to production!

*Prepared by CodexCoders Team for Samsung PRISM GenAI Hackathon 2025*
