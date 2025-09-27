# SmartFix-AI: Complete API Reference

## 🌐 API Overview

SmartFix-AI provides a comprehensive REST API for multi-modal troubleshooting, autonomous system healing, and intelligent assistance. The API is built on FastAPI and provides automatic OpenAPI documentation.

**Base URL**: `http://localhost:8000/api/v1`  
**Documentation**: `http://localhost:8000/docs`  
**ReDoc**: `http://localhost:8000/redoc`

## 🔐 Authentication

Currently, the API operates without authentication for development purposes. Production deployments should implement JWT-based authentication.

```http
Authorization: Bearer <jwt_token>
```

## 📋 Core Query Endpoints

### Text Query Processing

Process text-based troubleshooting queries with AI analysis.

```http
POST /api/v1/query/text
Content-Type: application/json
```

**Request Body:**
```json
{
  "text_query": "My laptop is running very slowly",
  "user_id": "user_1234567890",
  "input_type": "text",
  "device_category": "laptop",
  "priority": "normal"
}
```

**Response:**
```json
{
  "query_id": "query_550e8400-e29b-41d4-a716-446655440000",
  "solution": {
    "issue": "System Performance Degradation",
    "possible_causes": [
      "High CPU usage from background processes",
      "Insufficient RAM causing memory pressure",
      "Disk fragmentation or low storage space",
      "Malware or resource-intensive applications"
    ],
    "confidence_score": 0.87,
    "recommended_steps": [
      {
        "step_number": 1,
        "description": "Check Task Manager for high CPU/memory usage processes",
        "details": "Press Ctrl+Shift+Esc to open Task Manager and sort by CPU usage"
      },
      {
        "step_number": 2,
        "description": "Close unnecessary applications and background processes",
        "details": "End processes that are using excessive resources"
      },
      {
        "step_number": 3,
        "description": "Run disk cleanup and defragmentation",
        "details": "Use built-in Windows Disk Cleanup tool"
      },
      {
        "step_number": 4,
        "description": "Update drivers and run Windows Update",
        "details": "Ensure all drivers and system updates are current"
      }
    ],
    "external_sources": [
      {
        "title": "How to Fix Slow Computer Performance",
        "snippet": "Comprehensive guide to improving computer speed...",
        "url": "https://smartfix-ai.com/fix-slow-computer"
      }
    ],
    "additional_info": "Based on your description, this appears to be a performance optimization issue. The steps above should resolve most common causes of slow performance."
  },
  "source": "ai_analysis",
  "query_text": "My laptop is running very slowly",
  "processing_time": 2.34,
  "models_used": ["gemini", "huggingface"],
  "timestamp": "2024-01-15T10:30:00Z",
  "confidence_score": 0.87
}
```

### Image Query Processing

Process image-based queries with OCR and visual analysis.

```http
POST /api/v1/query/image
Content-Type: multipart/form-data
```

**Form Fields:**
- `image`: Image file (required) - PNG, JPG, JPEG, GIF, BMP
- `text_query`: Additional text description (optional)
- `user_id`: User identifier (optional, defaults to "anonymous")

**Response:** Same format as text query with additional OCR data:

```json
{
  "query_id": "query_550e8400-e29b-41d4-a716-446655440001",
  "solution": {
    "issue": "SQL Server Connection Error",
    "possible_causes": [
      "SQL Server service not running",
      "Incorrect connection string",
      "Network connectivity issues",
      "Authentication problems"
    ],
    "confidence_score": 0.92,
    "recommended_steps": [
      {
        "step_number": 1,
        "description": "Check if SQL Server service is running",
        "details": "Open Services.msc and verify SQL Server service status"
      },
      {
        "step_number": 2,
        "description": "Verify connection string parameters",
        "details": "Check server name, database name, and authentication method"
      }
    ],
    "ocr_data": {
      "extracted_text": "Cannot connect to SQL Server. Network-related or instance-specific error...",
      "error_codes": ["SQL Server Error 2", "Network Error"],
      "confidence": 0.95
    }
  },
  "source": "image_analysis",
  "query_text": "Getting this SQL error",
  "processing_time": 3.21,
  "models_used": ["gemini", "ocr"],
  "timestamp": "2024-01-15T10:35:00Z",
  "confidence_score": 0.92
}
```

### Log File Processing

Analyze system or application log files for error patterns.

```http
POST /api/v1/query/logs
Content-Type: multipart/form-data
```

**Form Fields:**
- `log_file`: Log file (required) - TXT, LOG, CSV
- `user_id`: User identifier (optional)

**Response:** Same format as text query with log analysis:

```json
{
  "query_id": "query_550e8400-e29b-41d4-a716-446655440002",
  "solution": {
    "issue": "Application Crash Analysis",
    "possible_causes": [
      "Memory leak causing out-of-memory errors",
      "Unhandled exception in application code",
      "Dependency conflict or version mismatch"
    ],
    "confidence_score": 0.89,
    "recommended_steps": [
      {
        "step_number": 1,
        "description": "Update application to latest version",
        "details": "Check for available updates and install them"
      },
      {
        "step_number": 2,
        "description": "Check system memory usage",
        "details": "Monitor memory consumption during application use"
      }
    ],
    "log_analysis": {
      "error_count": 15,
      "critical_errors": 3,
      "warning_count": 8,
      "most_common_error": "OutOfMemoryException",
      "time_range": "2024-01-15 09:00:00 to 2024-01-15 10:30:00"
    }
  },
  "source": "log_analysis",
  "query_text": "Application keeps crashing",
  "processing_time": 4.12,
  "models_used": ["gemini", "log_parser"],
  "timestamp": "2024-01-15T10:40:00Z",
  "confidence_score": 0.89
}
```

## 🤖 Smart Assistant Endpoints

### Network-Aware Assistant Query

Intelligent assistant that automatically switches between online and offline modes.

```http
POST /api/v1/smart/query
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "My internet connection is unstable",
  "user_id": "user_1234567890",
  "collect_system_data": true,
  "context": {
    "device_type": "laptop",
    "os": "Windows 11"
  }
}
```

**Response:**
```json
{
  "success": true,
  "response": "I've analyzed your network connectivity issue. Based on your system data showing intermittent connection drops, here are the most effective solutions:",
  "solution": {
    "issue": "Network Connectivity Instability",
    "possible_causes": [
      "Router/modem hardware issues",
      "ISP service disruption",
      "Network adapter driver problems",
      "WiFi interference or signal strength issues"
    ],
    "confidence_score": 0.85,
    "recommended_steps": [
      {
        "step_number": 1,
        "description": "Restart your router and modem",
        "details": "Power cycle both devices and wait 30 seconds before reconnecting"
      },
      {
        "step_number": 2,
        "description": "Check network adapter drivers",
        "details": "Update WiFi adapter drivers through Device Manager"
      }
    ]
  },
  "type": "technical_solution",
  "confidence_score": 85,
  "source": "gemini_online",
  "network_status": "online",
  "system_data": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "network_quality": 0.3,
    "active_processes": 89
  }
}
```

### Smart Assistant Status

Check the status of the network-aware assistant.

```http
GET /api/v1/smart/status
```

**Response:**
```json
{
  "network_status": "online",
  "preferred_mode": "online",
  "offline_assistant": {
    "available": true,
    "status": "ready",
    "llm_available": true,
    "templates_available": true
  },
  "services_available": {
    "network_aware_assistant": true,
    "device_logs_collector": true,
    "enhanced_offline_assistant": true,
    "gemini_service": true,
    "huggingface_service": true
  },
  "last_check": "2024-01-15T10:45:00Z"
}
```

## 🚀 Galaxy Autopilot Endpoints

### System Status

Get comprehensive Galaxy Autopilot system status.

```http
GET /api/v1/galaxy-autopilot/status
```

**Response:**
```json
{
  "system_status": "active",
  "overall_health": 92,
  "layers": {
    "surface": {
      "status": "active",
      "health": 95,
      "last_action": "2024-01-15T10:30:00Z",
      "actions_today": 12
    },
    "deep": {
      "status": "active",
      "health": 88,
      "last_action": "2024-01-15T09:15:00Z",
      "actions_today": 3
    },
    "immune": {
      "status": "active",
      "health": 96,
      "last_action": "2024-01-15T08:45:00Z",
      "actions_today": 1
    },
    "regenerative": {
      "status": "active",
      "health": 90,
      "last_action": "2024-01-15T10:00:00Z",
      "actions_today": 5
    },
    "optimization": {
      "status": "active",
      "health": 94,
      "last_action": "2024-01-15T10:20:00Z",
      "actions_today": 8
    }
  },
  "last_updated": "2024-01-15T10:45:00Z",
  "uptime_hours": 24.5
}
```

### Process Healing Request

Trigger Galaxy Autopilot healing for specific issues.

```http
POST /api/v1/galaxy-autopilot/heal
Content-Type: application/json
```

**Request Body:**
```json
{
  "issue_type": "performance",
  "severity": "medium",
  "context": {
    "cpu_usage": 85.2,
    "memory_usage": 92.1,
    "disk_usage": 78.5,
    "temperature": 72.3,
    "proactive": false
  }
}
```

**Response:**
```json
{
  "success": true,
  "action_taken": "memory_optimization",
  "layer_used": "surface",
  "details": {
    "processes_killed": 3,
    "memory_freed": "2.1GB",
    "cache_cleared": true,
    "services_restarted": 1
  },
  "timestamp": "2024-01-15T10:45:00Z",
  "estimated_improvement": 15.2
}
```

### System Health Metrics

Get detailed system health metrics.

```http
GET /api/v1/galaxy-autopilot/health
```

**Response:**
```json
{
  "battery_level": 87.5,
  "memory_usage": 68.2,
  "cpu_usage": 45.8,
  "storage_usage": 72.1,
  "temperature": 68.5,
  "system_health_score": 92,
  "timestamp": "2024-01-15T10:45:00Z",
  "recommendations": [
    "Consider clearing browser cache to free up memory",
    "Update system drivers for optimal performance",
    "Run disk cleanup to free up storage space"
  ]
}
```

### Healing Action History

Get history of healing actions performed.

```http
GET /api/v1/galaxy-autopilot/actions/history?limit=20&offset=0
```

**Response:**
```json
{
  "actions": [
    {
      "action_id": "action_001",
      "action_type": "memory_optimization",
      "layer": "surface",
      "timestamp": "2024-01-15T10:30:00Z",
      "success": true,
      "details": {
        "memory_freed": "1.8GB",
        "processes_optimized": 5
      }
    },
    {
      "action_id": "action_002",
      "action_type": "cache_clearing",
      "layer": "surface",
      "timestamp": "2024-01-15T09:45:00Z",
      "success": true,
      "details": {
        "cache_size": "500MB",
        "files_cleared": 1250
      }
    }
  ],
  "total_count": 45,
  "success_rate": 96.7
}
```

## 🎤 Enhanced Voice Assistant Endpoints

### Voice Command Processing

Process voice commands with multi-modal analysis.

```http
POST /api/v1/enhanced/voice/process
Content-Type: application/json
```

**Request Body:**
```json
{
  "voice_input": "My screen display is not working properly",
  "context": {
    "device_type": "laptop",
    "take_screenshot": true,
    "collect_system_data": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "transcription": "My screen display is not working properly",
  "confidence": 0.95,
  "analysis": {
    "intent": "display_issue",
    "entities": ["screen", "display"],
    "urgency": "medium"
  },
  "solution": {
    "issue": "Display Configuration Problem",
    "possible_causes": [
      "Display driver issues",
      "Resolution settings incorrect",
      "External monitor connection problems"
    ],
    "confidence_score": 0.88,
    "recommended_steps": [
      {
        "step_number": 1,
        "description": "Check display settings and resolution",
        "details": "Right-click desktop > Display Settings > Adjust resolution"
      },
      {
        "step_number": 2,
        "description": "Update display drivers",
        "details": "Device Manager > Display adapters > Update driver"
      }
    ]
  },
  "screenshot_analysis": {
    "taken": true,
    "resolution": "1920x1080",
    "ui_elements_detected": ["taskbar", "desktop_icons", "system_tray"]
  },
  "system_data": {
    "cpu_usage": 35.2,
    "memory_usage": 58.7,
    "gpu_usage": 12.3
  },
  "timestamp": "2024-01-15T10:50:00Z"
}
```

### Screen Analysis

Analyze current screen state for troubleshooting.

```http
POST /api/v1/enhanced/voice/screen-analysis
Content-Type: application/json
```

**Request Body:**
```json
{
  "voice_input": "Analyze my current screen for any issues"
}
```

**Response:**
```json
{
  "success": true,
  "screenshot_taken": true,
  "analysis": {
    "screen_resolution": "1920x1080",
    "ui_elements": [
      {
        "type": "error_dialog",
        "text": "Application Error",
        "position": {"x": 400, "y": 300},
        "confidence": 0.92
      },
      {
        "type": "button",
        "text": "OK",
        "position": {"x": 500, "y": 400},
        "confidence": 0.95
      }
    ],
    "issues_detected": [
      "Error dialog visible on screen",
      "Application appears to be in error state"
    ]
  },
  "recommendations": [
    "Close the error dialog and restart the application",
    "Check application logs for detailed error information"
  ],
  "timestamp": "2024-01-15T10:55:00Z"
}
```

## 🔧 System Diagnostics Endpoints

### Network Diagnostics

Comprehensive network connectivity testing.

```http
POST /api/v1/enhanced/voice/network-diagnostic
Content-Type: application/json
```

**Request Body:**
```json
{
  "voice_input": "Test my internet connection"
}
```

**Response:**
```json
{
  "success": true,
  "network_tests": {
    "connectivity": {
      "status": "failed",
      "ping_google": "timeout",
      "ping_cloudflare": "timeout",
      "ping_opendns": "timeout"
    },
    "dns_resolution": {
      "status": "failed",
      "google_dns": "failed",
      "cloudflare_dns": "failed",
      "opendns": "failed"
    },
    "network_interfaces": [
      {
        "name": "WiFi",
        "status": "connected",
        "ip_address": "192.168.1.100",
        "signal_strength": -45
      }
    ],
    "port_tests": {
      "http_80": "closed",
      "https_443": "closed",
      "dns_53": "closed"
    }
  },
  "summary": {
    "overall_status": "offline",
    "issues_found": [
      "No internet connectivity",
      "DNS resolution failing",
      "All external connections blocked"
    ],
    "recommendations": [
      "Check router/modem connection",
      "Verify ISP service status",
      "Restart network equipment"
    ]
  },
  "timestamp": "2024-01-15T11:00:00Z"
}
```

### System Performance Diagnostics

Comprehensive system performance analysis.

```http
POST /api/v1/enhanced/voice/system-diagnostic
Content-Type: application/json
```

**Request Body:**
```json
{
  "voice_input": "Check my computer performance"
}
```

**Response:**
```json
{
  "success": true,
  "system_metrics": {
    "cpu": {
      "usage_percent": 78.5,
      "cores": 8,
      "frequency": 2.4,
      "temperature": 72.3
    },
    "memory": {
      "usage_percent": 85.2,
      "total_gb": 16,
      "available_gb": 2.4,
      "swap_usage": 12.1
    },
    "disk": {
      "usage_percent": 78.9,
      "free_space_gb": 45.2,
      "read_speed": 120.5,
      "write_speed": 98.3
    },
    "processes": {
      "total": 156,
      "high_cpu": 3,
      "high_memory": 2,
      "suspicious": 0
    }
  },
  "health_score": 72,
  "bottlenecks": [
    "High memory usage (85.2%)",
    "CPU usage elevated (78.5%)",
    "Low available disk space (45.2GB)"
  ],
  "recommendations": [
    "Close unnecessary applications to free memory",
    "Check for resource-intensive background processes",
    "Consider upgrading RAM for better performance",
    "Run disk cleanup to free up storage space"
  ],
  "timestamp": "2024-01-15T11:05:00Z"
}
```

## 📱 Notification Endpoints

### Send SMS Notification

Send troubleshooting solutions via SMS.

```http
POST /api/v1/query/notify
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": "user_1234567890",
  "notification_type": "sms",
  "message": "Your laptop performance issue has been diagnosed. Here's the solution: 1) Check Task Manager for high CPU processes 2) Close unnecessary applications 3) Run disk cleanup",
  "to_contact": "+1234567890",
  "priority": "normal"
}
```

**Response:**
```json
{
  "success": true,
  "notification_id": "notif_550e8400-e29b-41d4-a716-446655440003",
  "status": "sent",
  "sent_at": "2024-01-15T11:10:00Z",
  "delivery_status": "delivered"
}
```

## 📊 User History Endpoints

### Get User Query History

Retrieve user's troubleshooting history.

```http
GET /api/v1/query/history/{user_id}?limit=10&offset=0
```

**Response:**
```json
{
  "queries": [
    {
      "id": "query_550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user_1234567890",
      "query_text": "My laptop is running very slowly",
      "input_type": "text",
      "solution": {
        "issue": "System Performance Degradation",
        "confidence_score": 0.87
      },
      "status": "completed",
      "created_at": "2024-01-15T10:30:00Z",
      "processing_time": 2.34,
      "confidence_score": 0.87
    }
  ],
  "total_count": 25,
  "success_rate": 92.0
}
```

## 🔍 Health Check Endpoints

### System Health Check

Check overall system health and service availability.

```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T11:15:00Z",
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "database": {
      "status": "healthy",
      "response_time": 0.05,
      "last_check": "2024-01-15T11:15:00Z"
    },
    "gemini_service": {
      "status": "healthy",
      "response_time": 1.23,
      "last_check": "2024-01-15T11:15:00Z"
    },
    "huggingface_service": {
      "status": "healthy",
      "response_time": 0.89,
      "last_check": "2024-01-15T11:15:00Z"
    },
    "galaxy_autopilot": {
      "status": "healthy",
      "response_time": 0.12,
      "last_check": "2024-01-15T11:15:00Z"
    }
  },
  "system_metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 72.1,
    "active_connections": 12
  }
}
```

## 📝 Error Handling

### Error Response Format

All API endpoints return consistent error responses:

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid input parameters",
  "details": {
    "field": "text_query",
    "issue": "Field is required and cannot be empty"
  },
  "timestamp": "2024-01-15T11:20:00Z",
  "request_id": "req_550e8400-e29b-41d4-a716-446655440004"
}
```

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing authentication |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `SERVICE_UNAVAILABLE` | 503 | External service unavailable |
| `INTERNAL_ERROR` | 500 | Internal server error |

## 🔄 Rate Limiting

API requests are rate-limited to prevent abuse:

- **Default Limit**: 60 requests per minute per IP
- **Burst Limit**: 10 requests per second
- **Headers**: Rate limit information included in response headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1642248000
```

## 📚 SDK Examples

### Python SDK Example

```python
import requests

# Text query example
response = requests.post(
    "http://localhost:8000/api/v1/query/text",
    json={
        "text_query": "My computer is running slowly",
        "user_id": "user_123",
        "device_category": "laptop"
    }
)

result = response.json()
print(f"Issue: {result['solution']['issue']}")
print(f"Confidence: {result['confidence_score']}")
```

### JavaScript SDK Example

```javascript
// Text query example
const response = await fetch('http://localhost:8000/api/v1/query/text', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text_query: 'My computer is running slowly',
    user_id: 'user_123',
    device_category: 'laptop'
  })
});

const result = await response.json();
console.log('Issue:', result.solution.issue);
console.log('Confidence:', result.confidence_score);
```

### cURL Examples

```bash
# Text query
curl -X POST "http://localhost:8000/api/v1/query/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text_query": "My WiFi keeps disconnecting",
    "user_id": "user_123",
    "device_category": "laptop"
  }'

# Image query
curl -X POST "http://localhost:8000/api/v1/query/image" \
  -F "image=@screenshot.png" \
  -F "text_query=Getting this error message"

# Galaxy Autopilot status
curl -X GET "http://localhost:8000/api/v1/galaxy-autopilot/status"

# System health check
curl -X GET "http://localhost:8000/api/v1/health"
```

## 🚀 WebSocket Support

Real-time updates via WebSocket connections:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};

// Subscribe to Galaxy Autopilot updates
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'galaxy_autopilot'
}));
```

---

## Important Concept Clarification

**Galaxy Autopilot is a conceptual system software design** intended to operate as **phone backend system software**, not as a webpage or web application. The Galaxy Autopilot concept represents an innovative approach to autonomous device maintenance that would be integrated directly into Samsung Galaxy devices as system-level software, similar to how Device Care or Knox Security operates within the Android framework.

**Note**: The current implementation includes a web-based demonstration interface solely for concept visualization and hackathon presentation purposes. In actual deployment, Galaxy Autopilot would function as native Android system software integrated into Samsung Galaxy devices.

---

This comprehensive API reference covers all available endpoints, request/response formats, error handling, and usage examples for the SmartFix-AI system. For interactive testing, visit the automatic OpenAPI documentation at `http://localhost:8000/docs`.
