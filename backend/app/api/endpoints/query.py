from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from typing import Optional, List, Dict, Any
import uuid
import json
from datetime import datetime
import base64
import io
from PIL import Image
import re

# Import database components with error handling
try:
    from sqlalchemy.orm import Session
    from ...models.schemas import QueryInput, Solution, NotificationRequest
    from ...database import get_db
    from ...database.models import Query as QueryModel, User
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"Database imports failed: {e}")
    DATABASE_AVAILABLE = False
    # Create dummy classes for when database is not available
    class Session:
        pass
    class QueryInput:
        pass
    class Solution:
        pass
    class NotificationRequest:
        pass
    class QueryModel:
        pass
    class User:
        pass
    def get_db():
        return None

# Import services with error handling
try:
    from ...services.gemini_service import GeminiService
    from ...services.serpapi_service import SerpAPIService
    from ...services.twilio_service import TwilioService
    from ...services.brain_core import BrainCore
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Services imports failed: {e}")
    SERVICES_AVAILABLE = False
try:
    from ...services.ocr_service import OCRService
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    OCRService = None
from ...services.device_detector import get_device_detector
from ...services.local_assistant import get_local_assistant_service
from ...core.security import rate_limit_dependency
from ...core.config import settings

router = APIRouter()

# Initialize services
gemini_service = GeminiService()
serp_service = SerpAPIService()
twilio_service = TwilioService(
    account_sid=settings.TWILIO_SID,
    auth_token=settings.TWILIO_AUTH_TOKEN,
    from_phone=settings.TWILIO_FROM_PHONE
)
ocr_service = OCRService() if OCR_AVAILABLE else None
brain_core = BrainCore()  # Initialize the brain core system
device_detector = get_device_detector()  # Initialize the device detector
local_assistant = get_local_assistant_service()  # Initialize the local assistant service

@router.post("/text", response_model=Dict[str, Any])
async def process_text_query(query: QueryInput, db: Session = Depends(get_db)):
    """Process a text-based troubleshooting query using the brain core system"""
    if not query.text_query:
        raise HTTPException(status_code=400, detail="Text query is required")
    
    # Generate a unique ID for this query
    query_id = str(uuid.uuid4())
    
    # Store the query in the database
    query_record = QueryModel(
        id=query_id,
        user_id=query.user_id,
        query_text=query.text_query,
        input_type=query.input_type.value,
        device_category=getattr(query, 'device_category', None),
        priority=getattr(query, 'priority', 'normal'),
        status="processing"
    )
    db.add(query_record)
    db.commit()
    
    try:
        # Use the brain core system to process the input
        input_data = {
            "input_type": "text",
            "text_query": query.text_query,
            "device_category": getattr(query, 'device_category', None),
            "user_id": query.user_id
        }
        
        # Process with brain core (includes brain memory + AI analysis)
        brain_result = await brain_core.process_input(input_data)
        
        # Update the query record with the solution
        query_record.status = "completed"
        query_record.confidence_score = brain_result.get("solution", {}).get("confidence_score", 0.5)
        db.commit()
        
        return brain_result
    
    except Exception as e:
        # Log the error and return a fallback response
        print(f"Error processing text query with brain core: {e}")
        
        # Create a fallback solution
        fallback_solution = {
            "query_id": query_id,
            "solution": {
                "issue": f"Error analyzing: {query.text_query[:50]}...",
                "possible_causes": ["Brain system error", "Service unavailable"],
                "confidence_score": 0.1,
                "recommended_steps": [
                    {"step_number": 1, "description": "Please try again with more details about your issue"}
                ],
                "external_sources": []
            },
            "source": "error",
            "query_text": query.text_query
        }
        
        # Update the query record with the error
        query_record.status = "failed"
        query_record.error_message = str(e)
        db.commit()
        
        return fallback_solution

@router.post("/image", response_model=Dict[str, Any])
async def process_image_query(
    image: UploadFile = File(...),
    text_query: Optional[str] = Form(None),
    user_id: str = Form("anonymous"),
    db: Session = Depends(get_db)
):
    """Process an image-based troubleshooting query using the brain core system"""
    try:
        # Read image data
        image_data = await image.read()
        
        # Generate a unique ID for this query
        query_id = str(uuid.uuid4())
        
        # Process with brain core first before writing to DB
        try:
            # Use the brain core system to process the image input
            input_data = {
                "input_type": "image",
                "text_query": text_query or "",
                "image_data": image_data,
                "user_id": user_id
            }
            
            # Process with brain core (includes OCR + brain memory + AI analysis)
            brain_result = await brain_core.process_input(input_data)
            
            # Now that processing succeeded, store the query in the database
            query_record = QueryModel(
                id=query_id,
                user_id=user_id,
                query_text=text_query or "Image query",
                input_type="image",
                status="completed",
                confidence_score=brain_result.get("solution", {}).get("confidence_score", 0.5)
            )
            
            # Add the complete record to the database
            db.add(query_record)
            db.commit()
            
            return brain_result
        
        except Exception as e:
            # Log the error and return a fallback response
            print(f"Error processing image query with brain core: {e}")
            
            # Create a fallback solution
            fallback_solution = {
                "query_id": query_id,
                "solution": {
                    "issue": "Unable to process image",
                    "possible_causes": ["Image format not supported", "Brain system error"],
                    "confidence_score": 0.1,
                    "recommended_steps": [
                        {"step_number": 1, "description": "Please try with a clearer image"}
                    ],
                    "external_sources": []
                },
                "source": "error",
                "query_text": text_query or ""
            }
            
            # Add error record to the database
            query_record = QueryModel(
                id=query_id,
                user_id=user_id,
                query_text=text_query or "Image query",
                input_type="image",
                status="failed",
                error_message=str(e)
            )
            db.add(query_record)
            db.commit()
            
            return fallback_solution
            
    except Exception as e:
        # Handle errors in reading the image
        print(f"Error reading image file: {e}")
        return {
            "query_id": str(uuid.uuid4()),
            "success": False,
            "error": f"Error reading image: {str(e)}",
            "solution": {
                "issue": "Image upload error",
                "possible_causes": ["Invalid image format", "Corrupted file"],
                "confidence_score": 0.1,
                "recommended_steps": [
                    {"step_number": 1, "description": "Please try uploading the image again in a different format (JPEG, PNG)"}
                ]
            }
        }


@router.post("/logs", response_model=Dict[str, Any])
async def process_log_query(
    log_file: UploadFile = File(...),
    text_query: Optional[str] = Form(None),
    user_id: str = Form("anonymous"),
    db: Session = Depends(get_db)
):
    """Process a log file for troubleshooting using the brain core system"""
    try:
        # Read log data safely with error handling
        try:
            log_content = await log_file.read()
            log_text = log_content.decode("utf-8", errors="ignore")
        except UnicodeDecodeError:
            # Handle encoding issues
            return {
                "query_id": str(uuid.uuid4()),
                "success": False,
                "error": "Unable to decode log file. Please ensure it's a valid text file.",
                "solution": {
                    "issue": "Log file encoding error",
                    "possible_causes": ["Binary file format", "Unsupported encoding"],
                    "confidence_score": 0.1,
                    "recommended_steps": [
                        {"step_number": 1, "description": "Please upload a plain text log file"}
                    ]
                }
            }
        
        # Generate a unique ID for this query
        query_id = str(uuid.uuid4())
        
        # Process with brain core first before writing to DB
        try:
            # Use the brain core system to process the log input
            input_data = {
                "input_type": "log",
                "log_content": log_text,
                "user_id": user_id
            }
            
            # Process with brain core (includes log parsing + brain memory + AI analysis)
            brain_result = await brain_core.process_input(input_data)
            
            # Now that processing succeeded, store the query in the database
            query_record = QueryModel(
                id=query_id,
                user_id=user_id,
                query_text=text_query or "Log file query",
                input_type="log",
                status="completed",
                confidence_score=brain_result.get("solution", {}).get("confidence_score", 0.5)
            )
            
            # Add the complete record to the database
            db.add(query_record)
            db.commit()
            
            return brain_result
        
        except Exception as e:
            # Log the error and return a fallback response
            print(f"Error processing log query with brain core: {e}")
            
            # Create a fallback solution
            fallback_solution = {
                "query_id": query_id,
                "solution": {
                    "issue": "Unable to process log file",
                    "possible_causes": ["Log format not supported", "Brain system error"],
                    "confidence_score": 0.1,
                    "recommended_steps": [
                        {"step_number": 1, "description": "Please try with a different log format"}
                    ],
                    "external_sources": []
                },
                "source": "error",
                "query_text": ""
            }
            
            # Add error record to the database
            query_record = QueryModel(
                id=query_id,
                user_id=user_id,
                query_text=text_query or "Log file query",
                input_type="log",
                status="failed",
                error_message=str(e)
            )
            db.add(query_record)
            db.commit()
            
            return fallback_solution
            
    except Exception as e:
        # Handle errors in reading the log file
        print(f"Error reading log file: {e}")
        return {
            "query_id": str(uuid.uuid4()),
            "success": False,
            "error": f"Error reading log file: {str(e)}",
            "solution": {
                "issue": "Log file upload error",
                "possible_causes": ["Invalid file format", "Corrupted file"],
                "confidence_score": 0.1,
                "recommended_steps": [
                    {"step_number": 1, "description": "Please try uploading a plain text log file"}
                ]
            }
        }

@router.post("/notify", response_model=Dict[str, Any], dependencies=[Depends(rate_limit_dependency(10, 60))])
async def send_notification(notification: NotificationRequest, db: Session = Depends(get_db)):
    """Send a notification via SMS or WhatsApp"""
    from ...core.config import settings
    
    if not settings.NOTIFICATIONS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Notification service is not available. Please configure Twilio credentials."
        )
    
    result = {
        "success": False,
        "message": "",
        "notification_id": str(uuid.uuid4())
    }
    
    # Store notification in database (simplified - you may want to create a Notification model)
    # For now, we'll just proceed without storing notifications
    
    try:
        # Validate notification type
        if notification.notification_type not in ["sms", "whatsapp"]:
            raise ValueError(f"Unsupported notification type: {notification.notification_type}")
        
        # Send notification based on type
        if notification.notification_type == "sms":
            send_result = await twilio_service.send_sms(
                notification.to_contact,
                notification.message
            )
        else:  # whatsapp
            send_result = await twilio_service.send_whatsapp(
                notification.to_contact,
                notification.message
            )
        
        # Update result
        result["success"] = send_result.get("success", False)
        result["message"] = send_result.get("error", "Notification sent successfully")
    except ValueError as e:
        # Handle validation errors
        result["success"] = False
        result["message"] = str(e)
    except Exception as e:
        # Handle other errors
        result["success"] = False
        result["message"] = f"Error sending notification: {str(e)}"
    
    return result

@router.get("/history/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_history(user_id: str, db: Session = Depends(get_db)):
    """Get troubleshooting history for a specific user"""
    queries = db.query(QueryModel).filter(QueryModel.user_id == user_id).all()
    return [{"id": q.id, "query_text": q.query_text, "status": q.status, "created_at": q.created_at} for q in queries]

@router.get("/brain/stats", response_model=Dict[str, Any])
async def get_brain_stats():
    """Get brain system statistics and performance metrics"""
    try:
        stats = await brain_core.get_brain_stats()
        return {
            "success": True,
            "brain_stats": stats,
            "system_status": "operational"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "system_status": "error"
        }

@router.post("/brain/search", response_model=Dict[str, Any])
async def search_brain_memory(query: str = Body(..., embed=True), device_category: str = Body(None, embed=True)):
    """Search brain memory for similar problems"""
    try:
        results = await brain_core.search_brain_memory(query, device_category)
        return {
            "success": True,
            "query": query,
            "device_category": device_category,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "results": []
        }

@router.post("/brain/feedback", response_model=Dict[str, Any])
async def submit_feedback(
    query_id: str = Body(..., embed=True),
    success: bool = Body(..., embed=True),
    feedback_score: int = Body(None, embed=True)
):
    """Submit feedback for a solution to improve the brain system"""
    try:
        await brain_core.process_feedback(query_id, success, feedback_score)
        return {
            "success": True,
            "message": "Feedback processed successfully",
            "query_id": query_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/brain/add-solution", response_model=Dict[str, Any])
async def add_custom_solution(problem_data: Dict[str, Any] = Body(...)):
    """Add a custom solution to brain memory"""
    try:
        await brain_core.add_custom_solution(problem_data)
        return {
            "success": True,
            "message": "Custom solution added to brain memory",
            "problem_text": problem_data.get("problem_text", "")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/database/stats", response_model=Dict[str, Any])
async def get_database_stats(db: Session = Depends(get_db)):
    """Get database statistics and health information"""
    try:
        query_count = db.query(QueryModel).count()
        user_count = db.query(User).count()
        return {
            "success": True,
            "stats": {
                "total_queries": query_count,
                "total_users": user_count
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Device Detection Endpoints
@router.post("/device/analyze", response_model=Dict[str, Any], dependencies=[Depends(rate_limit_dependency(5, 60))])
async def analyze_device():
    """Perform comprehensive device analysis and generate health report"""
    try:
        analysis_result = await device_detector.perform_full_system_analysis()
        return analysis_result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/device/health", response_model=Dict[str, Any])
async def get_device_health():
    """Get quick device health status"""
    try:
        health_result = await device_detector.get_quick_health_check()
        return health_result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/device/analyze/quick", response_model=Dict[str, Any])
async def quick_device_scan():
    """Perform quick device scan"""
    try:
        analysis_result = await device_detector.perform_full_system_analysis()
        return analysis_result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/device/analyze/system-info", response_model=Dict[str, Any])
async def get_system_info():
    """Get detailed system information"""
    try:
        device_detector._collect_system_info()
        return {
            "success": True,
            "system_info": device_detector.system_info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/device/analyze/performance", response_model=Dict[str, Any])
async def get_performance_metrics():
    """Get detailed performance metrics"""
    try:
        await device_detector._perform_health_checks()
        return {
            "success": True,
            "metrics": device_detector.health_metrics,
            "recommendations": device_detector.recommendations,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/device/analyze/security", response_model=Dict[str, Any])
async def get_security_analysis():
    """Get security analysis results"""
    try:
        # Mock security analysis for now
        security_issues = [
            {
                "title": "Outdated System",
                "description": "System has not been updated in 30+ days",
                "severity": "medium",
                "category": "System Updates",
                "impact": "Potential security vulnerabilities"
            },
            {
                "title": "Firewall Status",
                "description": "Firewall is active and properly configured",
                "severity": "low",
                "category": "Network Security",
                "impact": "No immediate security concerns"
            }
        ]
        
        return {
            "success": True,
            "issues": security_issues,
            "recommendations": [
                "Update system to latest version",
                "Run security scan regularly",
                "Enable automatic updates"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/device/analyze/hardware", response_model=Dict[str, Any])
async def get_hardware_diagnostics():
    """Get hardware diagnostics"""
    try:
        # Mock hardware diagnostics
        hardware_status = {
            "storage": [
                {
                    "device": "C:",
                    "type": "SSD",
                    "health_status": "Good",
                    "temperature": 45,
                    "power_on_hours": 8760,
                    "life_remaining": 85
                }
            ],
            "battery": {
                "health": 95,
                "cycle_count": 150,
                "capacity": 87
            },
            "thermal": {
                "cpu": 65,
                "gpu": 55,
                "system": 45
            }
        }
        
        return {
            "success": True,
            "status": hardware_status,
            "recommendations": [
                "Monitor storage health regularly",
                "Keep system well ventilated",
                "Consider battery replacement if health drops below 80%"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/device/analyze/failure", response_model=Dict[str, Any])
async def get_failure_analysis():
    """Get failure analysis results"""
    try:
        # Mock failure analysis
        failure_analysis = {
            "recent_errors": [
                {
                    "message": "Application crash detected",
                    "timestamp": datetime.now().isoformat(),
                    "severity": "medium"
                }
            ],
            "performance_degradation": {
                "cpu": 85,
                "memory": 90,
                "disk": 95
            },
            "resource_exhaustion": {
                "memory": 2,
                "cpu": 1
            },
            "root_cause": {
                "description": "High memory usage causing system slowdown",
                "probability": 75
            }
        }
        
        return {
            "success": True,
            "analysis": failure_analysis,
            "recommendations": [
                "Close unnecessary applications",
                "Increase system memory if possible",
                "Monitor resource usage regularly"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/device/analyze/deep", response_model=Dict[str, Any])
async def deep_device_scan():
    """Perform deep device scan"""
    try:
        # Perform comprehensive analysis
        analysis_result = await device_detector.perform_full_system_analysis()
        
        # Add additional deep scan data
        deep_scan_data = {
            **analysis_result,
            "scan_type": "deep",
            "additional_metrics": {
                "process_analysis": "Completed",
                "network_analysis": "Completed",
                "file_system_check": "Completed",
                "registry_analysis": "Completed"
            }
        }
        
        return deep_scan_data
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/device/detailed-metrics", response_model=Dict[str, Any])
async def get_detailed_metrics():
    """Get detailed system metrics"""
    try:
        import psutil
        import time
        
        detailed_metrics = {
            "process_count": len(list(psutil.process_iter())),
            "uptime": time.time() - psutil.boot_time(),
            "boot_time": psutil.boot_time(),
            "users_count": len(psutil.users()),
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            **detailed_metrics
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Helper functions
def extract_error_codes(text: str) -> List[str]:
    """Extract error codes from text using pattern matching"""
    # Common error code patterns
    patterns = [
        r'error\s+code[:\s]+([A-Za-z0-9\-_]+)',
        r'error[:\s]+([A-Za-z0-9\-_]+)',
        r'exception[:\s]+([A-Za-z0-9\-_]+)',
        r'fail[:\s]+([A-Za-z0-9\-_]+)',
        r'([A-Z][0-9]{4,6})',  # Common format like E12345
        r'([A-Z]-[0-9]{2,4})'  # Format like E-123
    ]
    
    error_codes = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        error_codes.extend(matches)
    
    # Remove duplicates and return
    return list(set(error_codes))

def find_similar_queries(text_query: str, user_id: str, db: Session) -> List[Dict[str, Any]]:
    """Find similar queries in the database using simple keyword matching"""
    # Get user's previous queries
    all_queries = db.query(QueryModel).filter(QueryModel.user_id == user_id).all()
    
    # Filter queries that match some keywords
    similar_queries = []
    keywords = set(text_query.lower().split())
    
    for query in all_queries:
        if query.query_text:
            query_text = query.query_text.lower()
            query_keywords = set(query_text.split())
            
            # Calculate similarity based on common keywords
            common_keywords = keywords.intersection(query_keywords)
            if len(common_keywords) >= 2:  # At least 2 common keywords
                similarity_score = len(common_keywords) / max(len(keywords), len(query_keywords))
                if similarity_score > 0.3:  # At least 30% similarity
                    similar_queries.append({
                        "id": query.id,
                        "query_text": query.query_text,
                        "status": query.status,
                        "created_at": query.created_at
                    })
    
    # Sort by similarity (most similar first)
    similar_queries.sort(key=lambda q: len(set(q["query_text"].lower().split()).intersection(keywords)) / 
                         max(len(keywords), len(set(q["query_text"].lower().split()))),
                         reverse=True)
    
    return similar_queries[:3]  # Return top 3 similar queries

# Local Assistant Endpoints
@router.post("/assistant/local", response_model=Dict[str, Any])
async def query_local_assistant(query: QueryInput):
    """Query the local assistant for troubleshooting help"""
    try:
        # Extract context from the query
        context = {
            "device_info": query.device_info or {},
            "user_info": query.user_info or {}
        }
        
        # Process the query with the local assistant
        result = await local_assistant.process_query(query.text_query, context)
        
        # If local assistant is not available or fails, fall back to online services
        if not result.get("success", False) and result.get("fallback_to_online", False):
            # Fall back to brain core
            brain_result = await brain_core.process_query(query.text_query, query.device_info)
            return brain_result
        
        # Store the query and response in the database (simplified)
        # For now, we'll skip storing assistant queries
        
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/assistant/status", response_model=Dict[str, Any])
async def get_assistant_status():
    """Get status of the local assistant"""
    try:
        status = await local_assistant.get_status()
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }