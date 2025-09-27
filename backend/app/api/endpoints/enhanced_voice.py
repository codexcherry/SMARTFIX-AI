"""
Enhanced Voice Assistant API Endpoints
Provides advanced voice processing with multi-modal analysis
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging

from ...services.enhanced_voice_assistant import get_enhanced_voice_assistant
from ...services.validation_service import get_validation_service
from ...models.schemas import QueryInput
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

class VoiceQueryRequest(BaseModel):
    voice_input: str
    context: Optional[Dict[str, Any]] = None
    user_id: str = "anonymous"

class VoiceCommandRequest(BaseModel):
    command: str
    parameters: Optional[Dict[str, Any]] = None
    user_id: str = "anonymous"

@router.post("/voice/process", response_model=Dict[str, Any])
async def process_voice_command(request: VoiceQueryRequest):
    """
    Process voice commands with intelligent analysis and multi-modal integration
    """
    try:
        enhanced_voice_assistant = get_enhanced_voice_assistant()
        
        # Process the voice command
        result = await enhanced_voice_assistant.process_voice_command(
            voice_input=request.voice_input,
            context=request.context
        )
        
        return {
            "success": result["success"],
            "response": result["response"],
            "type": result.get("type", "unknown"),
            "details": result.get("details", {}),
            "recommendations": result.get("recommendations", []),
            "user_id": request.user_id
        }
        
    except Exception as e:
        logger.error(f"Error processing voice command: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing voice command: {str(e)}"
        )

@router.post("/voice/screen-analysis", response_model=Dict[str, Any])
async def analyze_screen_with_voice(request: VoiceQueryRequest):
    """
    Analyze screen issues using voice input with screenshot + OCR integration
    """
    try:
        enhanced_voice_assistant = get_enhanced_voice_assistant()
        
        # Force screen analysis mode
        result = await enhanced_voice_assistant._handle_screen_analysis(
            voice_input=request.voice_input,
            context=request.context
        )
        
        return {
            "success": result["success"],
            "response": result["response"],
            "screenshot_taken": "screenshot_path" in result.get("details", {}),
            "ocr_text": result.get("details", {}).get("ocr_text", ""),
            "analysis": result.get("details", {}).get("analysis", {}),
            "recommendations": result.get("recommendations", []),
            "user_id": request.user_id
        }
        
    except Exception as e:
        logger.error(f"Error in screen analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing screen: {str(e)}"
        )

@router.post("/voice/system-diagnostic", response_model=Dict[str, Any])
async def system_diagnostic_voice(request: VoiceQueryRequest):
    """
    Perform system diagnostics via voice command
    """
    try:
        enhanced_voice_assistant = get_enhanced_voice_assistant()
        
        # Force system diagnostic mode
        result = await enhanced_voice_assistant._handle_system_diagnostic(
            voice_input=request.voice_input,
            context=request.context
        )
        
        return {
            "success": result["success"],
            "response": result["response"],
            "diagnostic_type": "system",
            "details": result.get("details", {}),
            "recommendations": result.get("recommendations", []),
            "user_id": request.user_id
        }
        
    except Exception as e:
        logger.error(f"Error in system diagnostic: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error performing system diagnostic: {str(e)}"
        )

@router.post("/voice/network-diagnostic", response_model=Dict[str, Any])
async def network_diagnostic_voice(request: VoiceQueryRequest):
    """
    Perform network diagnostics via voice command
    """
    try:
        enhanced_voice_assistant = get_enhanced_voice_assistant()
        
        # Force network diagnostic mode
        result = await enhanced_voice_assistant._handle_network_diagnostic(
            voice_input=request.voice_input,
            context=request.context
        )
        
        return {
            "success": result["success"],
            "response": result["response"],
            "diagnostic_type": "network",
            "details": result.get("details", {}),
            "recommendations": result.get("recommendations", []),
            "user_id": request.user_id
        }
        
    except Exception as e:
        logger.error(f"Error in network diagnostic: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error performing network diagnostic: {str(e)}"
        )

@router.post("/voice/automation", response_model=Dict[str, Any])
async def automation_command_voice(request: VoiceCommandRequest):
    """
    Execute automation commands via voice
    """
    try:
        enhanced_voice_assistant = get_enhanced_voice_assistant()
        
        # Force automation mode
        result = await enhanced_voice_assistant._handle_automation_command(
            voice_input=request.command,
            context=request.parameters
        )
        
        return {
            "success": result["success"],
            "response": result["response"],
            "command_type": "automation",
            "details": result.get("details", {}),
            "user_id": request.user_id
        }
        
    except Exception as e:
        logger.error(f"Error executing automation command: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing command: {str(e)}"
        )

@router.get("/voice/status", response_model=Dict[str, Any])
async def get_voice_assistant_status():
    """
    Get the status of the enhanced voice assistant
    """
    try:
        enhanced_voice_assistant = get_enhanced_voice_assistant()
        
        return {
            "status": "active",
            "services": {
                "automation": True,
                "ocr": True,
                "validation": True,
                "network_diagnostics": True,
                "system_diagnostics": True,
                "brain_core": True
            },
            "capabilities": [
                "voice_processing",
                "screen_analysis",
                "system_diagnostics",
                "network_diagnostics",
                "automation_control",
                "multi_modal_analysis",
                "context_awareness",
                "response_validation"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting voice assistant status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting status: {str(e)}"
        )

@router.post("/voice/validate-intent", response_model=Dict[str, Any])
async def validate_voice_intent(request: VoiceQueryRequest):
    """
    Validate the intent of a voice command before processing
    """
    try:
        validation_service = get_validation_service()
        
        # Validate query intent
        intent_analysis = await validation_service.validate_query_intent(request.voice_input)
        
        return {
            "intent": intent_analysis["intent"],
            "confidence": intent_analysis["confidence"],
            "requires_technical_response": intent_analysis["requires_technical_response"],
            "suggested_response": intent_analysis.get("suggested_response", ""),
            "technical_keywords": intent_analysis.get("technical_keywords", []),
            "diagnostic_type": intent_analysis.get("diagnostic_type", ""),
            "user_id": request.user_id
        }
        
    except Exception as e:
        logger.error(f"Error validating voice intent: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error validating intent: {str(e)}"
        )
