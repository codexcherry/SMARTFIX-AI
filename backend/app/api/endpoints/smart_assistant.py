"""
Smart Assistant API Endpoints
Provides network-aware assistant capabilities with context awareness
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, Optional
import logging
from pydantic import BaseModel

from ...services.network_aware_assistant import get_network_aware_assistant
from ...services.device_logs_collector import get_device_logs_collector
from ...services.enhanced_offline_assistant import get_enhanced_offline_assistant
from ...core.security import rate_limit_dependency

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

class AssistantQuery(BaseModel):
    query: str
    user_id: str = "anonymous"
    collect_system_data: bool = True
    context: Optional[Dict[str, Any]] = None

@router.post("/query", response_model=Dict[str, Any])
async def process_smart_query(
    request: AssistantQuery,
    _: Any = Depends(rate_limit_dependency)
):
    """
    Process a query using the network-aware smart assistant
    
    - Automatically switches between online (Gemini) and offline modes
    - Provides context-aware responses
    - Collects system data for better diagnostics
    - Handles greetings appropriately
    """
    try:
        # Get service instances
        network_assistant = get_network_aware_assistant()
        device_logs_collector = get_device_logs_collector()
        
        # Collect system data if requested
        context = request.context or {}
        if request.collect_system_data:
            system_data = await device_logs_collector.collect_system_data(duration_seconds=2)
            context["system_data"] = system_data
            
            # Add performance analysis
            performance_analysis = device_logs_collector.analyze_performance_data(system_data)
            context["performance_analysis"] = performance_analysis
        
        # Process the query with the network-aware assistant
        result = await network_assistant.process_query(request.query, context)
        
        return {
            "success": True,
            "response": result.get("response", ""),
            "solution": result.get("solution", {}),
            "type": result.get("type", "unknown"),
            "confidence_score": result.get("confidence_score", 0),
            "source": result.get("source", "unknown"),
            "network_status": result.get("network_status", "unknown"),
            "user_id": request.user_id
        }
        
    except Exception as e:
        logger.error(f"Error processing smart query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@router.post("/offline", response_model=Dict[str, Any])
async def process_offline_query(
    request: AssistantQuery,
    _: Any = Depends(rate_limit_dependency)
):
    """
    Process a query using the enhanced offline assistant
    
    - Works without internet connection
    - Uses local LLM and templates
    - Handles greetings appropriately
    """
    try:
        # Get offline assistant
        offline_assistant = get_enhanced_offline_assistant()
        
        # Process the query with enhanced offline capabilities
        result = await offline_assistant.process_query(request.query, request.context)
        
        if not result.get("success", False) and result.get("fallback_to_online", False):
            # If offline assistant fails and suggests online fallback,
            # return appropriate error
            return {
                "success": False,
                "response": "Offline assistant is not available. Please check your installation or try online mode.",
                "error": result.get("error", "Unknown error"),
                "fallback_to_online": True,
                "user_id": request.user_id
            }
        
        return {
            "success": True,
            "response": result.get("response", ""),
            "solution": result.get("solution", {}),
            "type": result.get("type", "unknown"),
            "confidence_score": result.get("confidence_score", 0),
            "source": result.get("source", "offline"),
            "user_id": request.user_id
        }
        
    except Exception as e:
        logger.error(f"Error processing offline query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing offline query: {str(e)}"
        )

@router.get("/status", response_model=Dict[str, Any])
async def get_assistant_status():
    """
    Get the status of the smart assistant services
    """
    try:
        network_assistant = get_network_aware_assistant()
        offline_assistant = get_enhanced_offline_assistant()
        
        # Check network availability
        network_available = await network_assistant._check_network()
        
        # Get offline assistant status
        offline_status = await offline_assistant.get_status()
        
        return {
            "network_status": "online" if network_available else "offline",
            "preferred_mode": "online" if network_available else "offline",
            "offline_assistant": offline_status,
            "services_available": {
                "network_aware_assistant": True,
                "device_logs_collector": True,
                "enhanced_offline_assistant": offline_status.get("available", False)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting assistant status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting assistant status: {str(e)}"
        )
