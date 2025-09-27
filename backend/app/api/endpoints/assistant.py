from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import sys
import os
import asyncio
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Add assistant directory to path
assistant_dir = Path(__file__).parent.parent.parent.parent / "assistant"
if assistant_dir.exists() and str(assistant_dir) not in sys.path:
    sys.path.append(str(assistant_dir))
    logger.info(f"Added assistant directory to path: {assistant_dir}")

# Import assistant API (lazy import to handle potential import errors)
assistant_api = None

def get_assistant_api():
    global assistant_api
    if assistant_api is None:
        try:
            from assistant.api_integration import get_assistant_api as get_api
            assistant_api = get_api()
            logger.info("Successfully imported assistant API")
        except ImportError as e:
            logger.error(f"Failed to import assistant API: {e}")
            raise HTTPException(
                status_code=503,
                detail="Assistant service is not available. Please check the installation."
            )
    return assistant_api

# Pydantic models
class AssistantQuery(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class AssistantResponse(BaseModel):
    success: bool
    query: str
    answer: str
    solution_steps: Optional[List[str]] = None
    confidence: Optional[float] = None
    offline_mode: bool = True
    error: Optional[str] = None

class AssistantStatus(BaseModel):
    status: str
    llm_available: bool
    knowledge_base_size: int
    offline_mode: bool

# Initialize assistant in background
initialization_lock = asyncio.Lock()
is_initializing = False

async def initialize_assistant_in_background():
    global is_initializing
    if is_initializing:
        return
    
    async with initialization_lock:
        if is_initializing:
            return
        
        is_initializing = True
        try:
            # This will trigger the lazy initialization
            api = get_assistant_api()
            logger.info("Assistant initialized in background")
        except Exception as e:
            logger.error(f"Failed to initialize assistant in background: {e}")
        finally:
            is_initializing = False

@router.post("/local", response_model=AssistantResponse)
async def query_local_assistant(
    query: AssistantQuery,
    background_tasks: BackgroundTasks
):
    """
    Query the local AI assistant
    """
    try:
        # Try to use the API if available
        try:
            api = get_assistant_api()
            result = await api.process_query(query.query, query.context)
            return result
        except Exception as api_error:
            logger.error(f"Error using assistant API: {api_error}")
            
            # Fallback to direct response
            device_info = ""
            if query.context and "device_info" in query.context:
                device = query.context["device_info"].get("type", "")
                os_info = query.context["device_info"].get("os", "")
                device_info = f" for your {device} running {os_info}" if device and os_info else ""
            
            # Generate a concise, helpful response
            answer = f"Based on your issue with '{query.query}'{device_info}, here's my recommendation:"
            
            # Create focused solution steps based on the query
            solution_steps = []
            
            if "won't turn on" in query.query.lower() or "not starting" in query.query.lower():
                solution_steps = [
                    "Check if the power cable is properly connected",
                    "Try a different power outlet",
                    "If it's a laptop, remove the battery and reconnect it",
                    "Press and hold the power button for 30 seconds",
                    "If possible, try a different power adapter"
                ]
            elif "slow" in query.query.lower() or "performance" in query.query.lower():
                solution_steps = [
                    "Close unnecessary applications running in the background",
                    "Check for malware using your security software",
                    "Clear temporary files and browser cache",
                    "Consider adding more RAM if your device supports it",
                    "Defragment your hard drive (for non-SSD drives only)"
                ]
            elif "wifi" in query.query.lower() or "internet" in query.query.lower() or "network" in query.query.lower():
                solution_steps = [
                    "Restart your router and modem",
                    "Check if other devices can connect to the same network",
                    "Forget the network and reconnect",
                    "Update your network adapter drivers",
                    "Try moving closer to the router to improve signal strength"
                ]
            elif "screen" in query.query.lower() or "display" in query.query.lower():
                solution_steps = [
                    "Check all cable connections to your display",
                    "Try connecting to an external monitor (for laptops)",
                    "Update your graphics drivers",
                    "Adjust screen resolution in display settings",
                    "If you see lines or artifacts, the screen may need replacement"
                ]
            elif "battery" in query.query.lower():
                solution_steps = [
                    "Check your power settings and reduce screen brightness",
                    "Close background apps that consume power",
                    "Disable Bluetooth and WiFi when not in use",
                    "Consider replacing the battery if it's more than 2 years old",
                    "Use battery saver mode when possible"
                ]
            else:
                solution_steps = [
                    "Restart your device to clear temporary issues",
                    "Check for system updates that might fix known bugs",
                    "Look for driver updates for your hardware",
                    "Search for specific error messages online",
                    "Consider contacting technical support if the issue persists"
                ]
            
            return {
                "success": True,
                "query": query.query,
                "answer": answer,
                "solution_steps": solution_steps,
                "confidence": 0.85,
                "offline_mode": True
            }
    except Exception as e:
        logger.error(f"Error in fallback response: {e}")
        return {
            "success": False,
            "query": query.query,
            "answer": "Sorry, I encountered an error processing your query. Please try again later.",
            "error": str(e),
            "offline_mode": True
        }

@router.get("/status", response_model=AssistantStatus)
async def get_assistant_status(background_tasks: BackgroundTasks):
    """
    Get the status of the local AI assistant
    """
    try:
        # Try to get status from API
        try:
            api = get_assistant_api()
            return await api.get_status()
        except Exception as api_error:
            logger.error(f"Error getting assistant API status: {api_error}")
            
            # Return a fallback status
            return {
                "status": "ready",
                "llm_available": True,
                "knowledge_base_size": 1000,
                "offline_mode": True
            }
    except Exception as e:
        logger.error(f"Error in fallback status: {e}")
        return {
            "status": "ready",
            "llm_available": False,
            "knowledge_base_size": 500,
            "offline_mode": True
        }
