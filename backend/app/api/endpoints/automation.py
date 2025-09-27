from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

from ...services.automation_service import get_automation_service, AutomationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Pydantic models
class AutomationRequest(BaseModel):
    action: str
    parameters: Optional[Dict[str, Any]] = {}
    user_id: Optional[str] = "default_user"

class AutomationResponse(BaseModel):
    success: bool
    action: str
    message: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ScreenshotResponse(BaseModel):
    success: bool
    action: str
    message: str
    filepath: Optional[str] = None
    image_data: Optional[str] = None
    error: Optional[str] = None

class StatusResponse(BaseModel):
    status: str
    last_action: Optional[str] = None
    system: str
    available_actions: List[str]

@router.post("/execute", response_model=AutomationResponse)
async def execute_automation(
    request: AutomationRequest,
    automation_service: AutomationService = Depends(get_automation_service)
):
    """
    Execute an automation action
    """
    try:
        action = request.action.lower()
        
        if action == "brightness_up" or action == "increase_brightness":
            result = await automation_service.control_brightness("up")
        elif action == "brightness_down" or action == "decrease_brightness":
            result = await automation_service.control_brightness("down")
        elif action == "volume_up" or action == "increase_volume":
            result = await automation_service.control_volume("up")
        elif action == "volume_down" or action == "decrease_volume":
            result = await automation_service.control_volume("down")
        elif action == "volume_mute" or action == "mute":
            result = await automation_service.control_volume("mute")
        elif action.startswith("open_"):
            app_name = action.replace("open_", "")
            if not app_name and "app_name" in request.parameters:
                app_name = request.parameters["app_name"]
            result = await automation_service.open_application(app_name)
        elif action.startswith("close_"):
            app_name = action.replace("close_", "")
            if not app_name and "app_name" in request.parameters:
                app_name = request.parameters["app_name"]
            result = await automation_service.close_application(app_name)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported action: {action}"
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Error executing automation: {str(e)}")
        return {
            "success": False,
            "action": request.action,
            "message": "Failed to execute automation",
            "error": str(e)
        }

@router.post("/screenshot", response_model=ScreenshotResponse)
async def take_screenshot(
    automation_service: AutomationService = Depends(get_automation_service)
):
    """
    Take a screenshot
    """
    try:
        result = await automation_service.take_screenshot()
        return result
    
    except Exception as e:
        logger.error(f"Error taking screenshot: {str(e)}")
        return {
            "success": False,
            "action": "screenshot",
            "message": "Failed to take screenshot",
            "error": str(e)
        }

@router.get("/status", response_model=StatusResponse)
async def get_status(
    automation_service: AutomationService = Depends(get_automation_service)
):
    """
    Get the current status of the automation service
    """
    return await automation_service.get_status()
