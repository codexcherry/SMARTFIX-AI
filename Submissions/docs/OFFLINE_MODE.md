# SmartFix-AI Offline Mode

SmartFix-AI's offline mode provides local AI capabilities using HuggingFace models, ensuring the system can continue functioning even when external AI services are unavailable or when internet connectivity is limited.

## Overview

The offline mode system includes:

- **Local AI Models**: Pre-downloaded HuggingFace models for various AI tasks
- **Cached Solutions**: Previously generated solutions stored locally
- **Fallback Mechanisms**: Rule-based solutions when AI models are unavailable
- **Multimodal Support**: Text, audio, and image processing capabilities

## Supported Models

The system uses the following optimized models for offline operation:

| Model Type | Model Name | Size | Purpose |
|------------|------------|------|---------|
| **Speech-to-Text** | `faster-whisper-small` | 244MB | Audio transcription |
| **Text Analysis** | `distilbert-base-uncased` | 260MB | Problem classification |
| **Embeddings** | `all-MiniLM-L6-v2` | 90MB | Semantic similarity |
| **OCR** | `paddleocr` | 100MB | Text extraction from images |
| **Text Generation** | `llama-2-3b-chat-ggml` | ~1.8GB | Solution enhancement |
| **Summarization** | `t5-small` | 60MB | Text summarization |

**Total Size**: ~2.5GB (optimized for local deployment)

## Setup

### 1. Environment Configuration

Add the following environment variables to your `.env` file:

```bash
# Offline Mode Settings
OFFLINE_MODE_ENABLED=true
OFFLINE_MODELS_PATH=./offline_models
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

### 2. Install Dependencies

The offline mode requires additional dependencies. Install them using:

```bash
cd backend
pip install -r requirements.txt
```

Key dependencies for offline mode:
- `huggingface-hub==0.19.4`
- `faster-whisper==0.10.0`
- `paddlepaddle==2.5.2`
- `paddleocr==2.7.0.3`
- `llama-cpp-python==0.2.20`

### 3. Download Models

#### Option A: Using the Demo Script

```bash
cd backend
python download_offline_models.py --download-only
```

#### Option B: Using the API

```bash
# Start the server
uvicorn app.main:app --reload

# Trigger model download (requires authentication)
curl -X POST "http://localhost:8000/api/v1/offline/download-models" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Option C: Automatic Download

Models are automatically downloaded when the service starts if `OFFLINE_MODE_ENABLED=true`.

## Usage

### 1. Basic Offline Query Processing

```python
from app.services.offline_service import offline_service

# Generate offline solution
solution = await offline_service.generate_offline_solution(
    query_text="My WiFi is not connecting",
    device_category="laptop"
)

print(f"Confidence: {solution['confidence_score']}")
print(f"Issue: {solution['solution']['issue']}")
```

### 2. Audio Transcription

```python
# Transcribe audio file
transcription = await offline_service.transcribe_audio("audio_file.wav")
print(f"Transcription: {transcription}")
```

### 3. Image Text Extraction

```python
# Extract text from image
extracted_text = await offline_service.extract_text_from_image("screenshot.png")
print(f"Extracted text: {extracted_text}")
```

### 4. Text Summarization

```python
# Summarize long text
summary = await offline_service.summarize_text(
    "Long technical document...",
    max_length=150
)
print(f"Summary: {summary}")
```

## API Endpoints

### Offline Mode Status

```http
GET /api/v1/offline/status
```

**Response:**
```json
{
  "enabled": true,
  "models_loaded": ["text_classifier", "embeddings", "summarizer"],
  "download_progress": {
    "speech_to_text": {"status": "completed", "progress": 100},
    "text_analysis": {"status": "completed", "progress": 100}
  },
  "total_solutions": 150,
  "recent_solutions": 25,
  "ai_available": true,
  "models_path": "./offline_models"
}
```

### Download Models

```http
POST /api/v1/offline/download-models
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "success": true,
  "message": "Model download started in background",
  "data": {
    "download_status": "started",
    "models_to_download": ["speech_to_text", "text_analysis", "embeddings"]
  }
}
```

### Get Offline Solutions

```http
GET /api/v1/offline/solutions?limit=10&offset=0
Authorization: Bearer YOUR_TOKEN
```

### Audio Transcription

```http
POST /api/v1/offline/transcribe
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data

audio_file: [audio file]
```

### Image Text Extraction

```http
POST /api/v1/offline/extract-text
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data

image_file: [image file]
```

### Text Summarization

```http
POST /api/v1/offline/summarize
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "text": "Long text to summarize...",
  "max_length": 150
}
```

### Get Models Information

```http
GET /api/v1/offline/models/info
Authorization: Bearer YOUR_TOKEN
```

### Clear Cache

```http
POST /api/v1/offline/clear-cache
Authorization: Bearer YOUR_TOKEN
```

## Architecture

### Model Management

```
OfflineAIService
├── Model Download
│   ├── Concurrent downloads using asyncio
│   ├── Progress tracking
│   └── Error handling
├── Model Loading
│   ├── Lazy loading for memory efficiency
│   ├── CPU optimization
│   └── Fallback mechanisms
└── Solution Management
    ├── Query hashing
    ├── Cache integration
    └── Database storage
```

### Solution Generation Pipeline

1. **Query Processing**
   - Generate query hash
   - Check cache for existing solutions
   - Check database for stored solutions

2. **AI Analysis** (if models available)
   - Problem classification using DistilBERT
   - Solution generation using rule-based + AI enhancement
   - Confidence calculation using embeddings

3. **Fallback** (if AI unavailable)
   - Rule-based problem classification
   - Template-based solution generation
   - Default confidence scoring

4. **Storage**
   - Cache solution for quick access
   - Store in database for persistence
   - Update access statistics

## Performance Considerations

### Memory Usage

- **Lazy Loading**: Models are loaded only when needed
- **CPU Optimization**: All models configured for CPU inference
- **Quantized Models**: Using quantized versions for reduced memory footprint

### Storage Requirements

- **Models**: ~2.5GB total
- **Solutions Cache**: Varies based on usage
- **Database**: Minimal overhead

### Response Times

- **Cached Solutions**: < 100ms
- **AI-Generated Solutions**: 1-5 seconds
- **Rule-Based Solutions**: < 500ms

## Troubleshooting

### Common Issues

1. **Model Download Failures**
   ```bash
   # Check internet connectivity
   # Verify HuggingFace API key
   # Check available disk space
   ```

2. **Memory Issues**
   ```bash
   # Reduce concurrent model loading
   # Use smaller model variants
   # Increase system memory
   ```

3. **Performance Issues**
   ```bash
   # Enable lazy loading
   # Use CPU-optimized models
   # Implement caching strategies
   ```

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('app.services.offline_service').setLevel(logging.DEBUG)
```

### Health Checks

Monitor offline mode health:

```bash
curl http://localhost:8000/api/v1/offline/status
```

## Integration with Main System

The offline mode integrates seamlessly with the main SmartFix-AI system:

1. **Automatic Fallback**: When online AI services fail, the system automatically switches to offline mode
2. **Hybrid Processing**: Combines online and offline capabilities for optimal results
3. **Unified API**: Same endpoints work for both online and offline processing
4. **Consistent Data**: Solutions are stored in the same format regardless of source

## Security Considerations

- **Local Processing**: All AI processing happens locally
- **No External Calls**: Offline mode doesn't require internet connectivity
- **Data Privacy**: User data never leaves the local system
- **Model Verification**: Downloaded models are verified for integrity

## Future Enhancements

- **Model Updates**: Automatic model version management
- **Custom Models**: Support for user-provided models
- **Edge Deployment**: Optimized for edge computing devices
- **Federated Learning**: Collaborative model improvement

---

## Important Concept Clarification

**Galaxy Autopilot is a conceptual system software design** intended to operate as **phone backend system software**, not as a webpage or web application. The Galaxy Autopilot concept represents an innovative approach to autonomous device maintenance that would be integrated directly into Samsung Galaxy devices as system-level software, similar to how Device Care or Knox Security operates within the Android framework.

**Note**: The current implementation includes a web-based demonstration interface solely for concept visualization and hackathon presentation purposes. In actual deployment, Galaxy Autopilot would function as native Android system software integrated into Samsung Galaxy devices.
