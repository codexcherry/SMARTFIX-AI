# SmartFix-AI Backend

A comprehensive AI-powered troubleshooting assistant backend built with FastAPI.

## 🚀 Features

- **Multi-modal Input Processing**: Text, image, and log file analysis
- **AI-Powered Solutions**: Integration with Gemini AI and HuggingFace models
- **Brain Memory System**: Intelligent problem-solving with learning capabilities
- **Real-time Notifications**: SMS and WhatsApp integration via Twilio
- **Device Analysis**: Comprehensive system diagnostics and health monitoring
- **Offline Mode**: Local AI model support for offline operation

## 📁 Project Structure

```
backend/
├── app/                    # Main application package
│   ├── api/               # API routes and endpoints
│   │   ├── endpoints/     # Individual endpoint modules
│   │   └── api.py         # Main API router
│   ├── core/              # Core configuration and utilities
│   │   ├── config.py      # Application settings
│   │   ├── cache.py       # Caching utilities
│   │   ├── security.py    # Authentication & security
│   │   └── monitoring.py  # Health monitoring
│   ├── services/          # Business logic services
│   │   ├── brain_core.py  # Main AI processing engine
│   │   ├── database.py    # Database operations
│   │   ├── gemini_service.py    # Gemini AI integration
│   │   ├── huggingface_service.py # HuggingFace models
│   │   ├── twilio_service.py     # SMS/WhatsApp notifications
│   │   └── ocr_service.py        # Image text extraction
│   ├── models/            # Data models and schemas
│   ├── nlp/               # Natural language processing
│   └── main.py            # FastAPI application
├── models/                # AI model storage
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
└── Dockerfile            # Container configuration
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SmartFix-AI/backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   # Create .env file with your API keys (REQUIRED)
   HUGGINGFACE_API_KEY=your_huggingface_key
   GEMINI_API_KEY=your_gemini_key
   SERPAPI_KEY=your_serpapi_key
   TWILIO_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_FROM_PHONE=+1234567890
   TWILIO_TO_PHONE=+1234567890
   SECRET_KEY=your-secret-key-here
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

   **Note**: The application will fail to start if required environment variables are missing.

## 🔧 Configuration

The application uses environment variables for configuration. Key settings:

- `DEBUG`: Enable debug mode (default: False)
- `ENVIRONMENT`: Environment name (default: development)
- `DB_FILE`: Database file path (default: ./smartfix_ai.db)
- `CORS_ORIGINS`: Allowed CORS origins
- `OFFLINE_MODE_ENABLED`: Enable offline AI processing

## 📡 API Endpoints

### Core Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - API documentation

### Query Processing
- `POST /api/v1/query/text` - Process text queries
- `POST /api/v1/query/image` - Process image queries
- `POST /api/v1/query/voice` - Process voice queries
- `POST /api/v1/query/log` - Process log files

### Brain System
- `GET /api/v1/query/brain/stats` - Brain system statistics
- `POST /api/v1/query/brain/search` - Search brain memory
- `POST /api/v1/query/brain/feedback` - Submit feedback

### Notifications
- `POST /api/v1/query/notify` - Send SMS/WhatsApp notifications

### Database Management
- `GET /api/v1/query/database/stats` - Database statistics
- `POST /api/v1/query/database/cleanup` - Clean old data

### Device Analysis
- `GET /api/v1/query/device/health` - Device health status
- `POST /api/v1/query/device/analyze` - Full system analysis

## 🧠 AI Services

### Brain Core System
The brain core system processes all inputs through multiple stages:
1. **Input Processing**: Convert all inputs to text
2. **Brain Memory Search**: Check for similar problems
3. **AI Analysis**: Use Gemini AI for complex problems
4. **Solution Generation**: Generate step-by-step solutions
5. **Learning**: Update brain memory with new solutions

### Supported AI Models
- **Gemini AI**: Primary AI reasoning engine
- **HuggingFace Models**: Offline text processing
- **OCR**: Image text extraction
- **Speech-to-Text**: Voice processing

## 🗄️ Database

The application uses a JSON-based database with:
- **Thread-safe operations** with automatic locking
- **Automatic backups** before write operations
- **Data retention policies** for cleanup
- **Statistics and monitoring** capabilities

## 🔒 Security

- **API Key Management**: Secure environment variable storage (no hardcoded secrets)
- **Rate Limiting**: Built-in rate limiting for sensitive endpoints
- **Authentication**: JWT-based authentication with role-based access control
- **CORS Configuration**: Configurable cross-origin policies
- **Input Validation**: Pydantic model validation
- **Error Handling**: Comprehensive error management

## 📊 Monitoring

- **Health Checks**: Built-in health monitoring
- **Database Statistics**: Real-time database metrics
- **Performance Metrics**: Response time monitoring
- **Error Tracking**: Comprehensive error logging

## 🚀 Deployment

### Docker Deployment
```bash
docker build -t smartfix-ai-backend .
docker run -p 8000:8000 smartfix-ai-backend
```

### Production Deployment
1. Set `ENVIRONMENT=production`
2. Configure proper CORS origins
3. Set up monitoring and logging
4. Configure backup strategies

## 🧪 Testing

The application includes comprehensive testing:
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Performance Tests**: Response time validation

## 📈 Performance

- **Response Time**: < 100ms for most endpoints
- **Concurrent Users**: Supports multiple simultaneous users
- **Memory Usage**: Optimized for efficient operation
- **Database**: Thread-safe with automatic cleanup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request


## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the health status at `/health`

---

**SmartFix-AI Backend** - Intelligent troubleshooting made simple.

