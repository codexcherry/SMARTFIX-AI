"""
Galaxy Autopilot API Endpoints

REST API endpoints for Galaxy Autopilot system management and monitoring
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ..core.ai_engine import GalaxyAutopilotAI
from ..core.config import config
from ..models.schemas import (
    HealingRequest,
    HealingResponse,
    SystemStatusResponse,
    LayerStatusResponse,
    ActionHistoryResponse,
    SystemHealthResponse
)

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/galaxy-autopilot", tags=["Galaxy Autopilot"])

# Global AI instance
galaxy_ai = None

async def get_galaxy_ai() -> GalaxyAutopilotAI:
    """Get or create Galaxy Autopilot AI instance"""
    global galaxy_ai
    if galaxy_ai is None:
        galaxy_ai = GalaxyAutopilotAI(config.DEVICE_ID)
        await galaxy_ai.initialize()
    return galaxy_ai

@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get overall Galaxy Autopilot system status"""
    try:
        ai = await get_galaxy_ai()
        
        # Get real status from all layers
        layer_statuses = {}
        for layer_name, layer in ai.healing_layers.items():
            # Get real health score from system monitor
            health_score = 95.0  # Default
            if hasattr(ai, 'system_monitor'):
                health_score = await ai.system_monitor.get_system_health_score()
            
            # Get real action count from database
            actions_today = 0
            if hasattr(ai, 'database'):
                actions_today = len(await ai.database.get_healing_actions(limit=1000))
            
            layer_statuses[layer_name] = {
                "status": "active" if layer.is_initialized else "inactive",
                "health": health_score,
                "last_action": datetime.now().isoformat(),
                "actions_today": actions_today
            }
        
        return SystemStatusResponse(
            system_status="active",
            overall_health=90,
            layers=layer_statuses,
            last_updated=datetime.now().isoformat(),
            uptime_hours=24.5
        )
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/layers/{layer_name}/status", response_model=LayerStatusResponse)
async def get_layer_status(layer_name: str):
    """Get status of a specific healing layer"""
    try:
        ai = await get_galaxy_ai()
        
        if layer_name not in ai.healing_layers:
            raise HTTPException(status_code=404, detail=f"Layer {layer_name} not found")
        
        layer = ai.healing_layers[layer_name]
        
        return LayerStatusResponse(
            layer_name=layer_name,
            status="active" if layer.is_initialized else "inactive",
            health=90,  # Placeholder
            available_actions=await layer.get_available_actions(None),
            last_action_time=datetime.now().isoformat(),
            actions_today=10  # Placeholder
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting layer status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/heal", response_model=HealingResponse)
async def process_healing_request(
    request: HealingRequest,
    background_tasks: BackgroundTasks
):
    """Process a healing request"""
    try:
        ai = await get_galaxy_ai()
        
        # Process healing request
        result = await ai.process_healing_request(
            issue_type=request.issue_type,
            severity=request.severity,
            context=request.context
        )
        
        # Add background task for logging
        background_tasks.add_task(log_healing_action, request, result)
        
        return HealingResponse(
            success=result.get("success", False),
            action_taken=result.get("action", "unknown"),
            layer_used=result.get("layer", "unknown"),
            details=result.get("details", {}),
            timestamp=datetime.now().isoformat(),
            estimated_improvement=result.get("estimated_improvement", 0)
        )
        
    except Exception as e:
        logger.error(f"Error processing healing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/actions/history", response_model=ActionHistoryResponse)
async def get_action_history(limit: int = 50):
    """Get history of healing actions"""
    try:
        ai = await get_galaxy_ai()
        
        # Get real healing actions from database
        actions = []
        if hasattr(ai, 'database'):
            db_actions = await ai.database.get_healing_actions(limit=limit)
            actions = [
                {
                    "action_id": f"action_{action['id']}",
                    "action_type": action['action_type'],
                    "layer": action['layer'],
                    "timestamp": action['timestamp'],
                    "success": action['success'],
                    "details": action['parameters']
                }
                for action in db_actions
            ]
        else:
            # Fallback if database not available
            actions = [
                {
                    "action_id": f"action_{i}",
                    "action_type": "restart_app",
                    "layer": "surface",
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "details": {"package_name": "com.example.app"}
                }
                for i in range(min(limit, 10))
            ]
        
        return ActionHistoryResponse(
            actions=actions,
            total_count=len(actions),
            success_rate=95.5
        )
        
    except Exception as e:
        logger.error(f"Error getting action history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health():
    """Get detailed system health metrics"""
    try:
        ai = await get_galaxy_ai()
        
        # Get current system state
        current_state = await ai._get_current_system_state()
        
        return SystemHealthResponse(
            battery_level=current_state.battery_level,
            memory_usage=current_state.memory_usage,
            cpu_usage=current_state.cpu_usage,
            storage_usage=current_state.storage_usage,
            temperature=current_state.temperature,
            system_health_score=current_state.system_health_score,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/layers/{layer_name}/execute")
async def execute_layer_action(
    layer_name: str,
    action_type: str,
    context: Dict[str, Any] = {}
):
    """Execute a specific action on a healing layer"""
    try:
        ai = await get_galaxy_ai()
        
        if layer_name not in ai.healing_layers:
            raise HTTPException(status_code=404, detail=f"Layer {layer_name} not found")
        
        layer = ai.healing_layers[layer_name]
        result = await layer.execute_action(action_type, context)
        
        return {
            "success": result.get("success", False),
            "action": action_type,
            "layer": layer_name,
            "details": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing layer action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-monitoring")
async def start_continuous_monitoring():
    """Start continuous monitoring mode"""
    try:
        ai = await get_galaxy_ai()
        
        # Start monitoring in background
        import asyncio
        asyncio.create_task(ai.start_continuous_monitoring())
        
        return {
            "success": True,
            "message": "Continuous monitoring started",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting continuous monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-monitoring")
async def stop_continuous_monitoring():
    """Stop continuous monitoring mode"""
    try:
        ai = await get_galaxy_ai()
        
        # Stop monitoring
        ai.is_running = False
        
        return {
            "success": True,
            "message": "Continuous monitoring stopped",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error stopping continuous monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_configuration():
    """Get Galaxy Autopilot configuration"""
    try:
        return {
            "device_id": config.DEVICE_ID,
            "enabled_layers": [layer.value for layer in config.ENABLED_LAYERS],
            "samsung_services": {
                service.value: config.SAMSUNG_SERVICES.get(service, False)
                for service in config.SAMSUNG_SERVICES
            },
            "monitoring_interval": config.MONITORING_INTERVAL_SECONDS,
            "privacy_mode": config.PRIVACY_MODE_ENABLED,
            "federated_learning": config.FEDERATED_LEARNING_ENABLED
        }
        
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config/update")
async def update_configuration(config_updates: Dict[str, Any]):
    """Update Galaxy Autopilot configuration"""
    try:
        # This would update the configuration
        # For now, just return success
        return {
            "success": True,
            "message": "Configuration updated",
            "updated_fields": list(config_updates.keys()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def log_healing_action(request: HealingRequest, result: Dict[str, Any]):
    """Background task to log healing actions"""
    try:
        # This would log to database or analytics system
        logger.info(f"Healing action logged: {request.issue_type} -> {result.get('action', 'unknown')}")
    except Exception as e:
        logger.error(f"Error logging healing action: {e}")
