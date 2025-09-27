"""
Enhanced Galaxy Autopilot API Endpoints

Advanced endpoints that integrate Galaxy Autopilot with SmartFix-AI
for intelligent system healing and optimization.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ..services.enhanced_autopilot_service import get_enhanced_autopilot_service, EnhancedAutopilotService
from ..models.schemas import (
    HealingRequest,
    HealingResponse,
    SystemStatusResponse,
    SystemHealthResponse
)

logger = logging.getLogger(__name__)

# Create enhanced API router
router = APIRouter(prefix="/enhanced-galaxy-autopilot", tags=["Enhanced Galaxy Autopilot"])

@router.get("/health-report", response_model=Dict[str, Any])
async def get_comprehensive_health_report():
    """Get comprehensive system health report with AI insights"""
    try:
        service = await get_enhanced_autopilot_service()
        report = await service.get_system_health_report()
        
        return {
            "success": True,
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting health report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/intelligent-healing", response_model=HealingResponse)
async def perform_intelligent_healing(
    request: HealingRequest,
    background_tasks: BackgroundTasks
):
    """Perform intelligent healing using AI-powered decision making"""
    try:
        service = await get_enhanced_autopilot_service()
        
        # Perform manual healing with AI
        result = await service.perform_manual_healing(
            issue_type=request.issue_type,
            severity=request.severity,
            context=request.context
        )
        
        # Add background task for analytics
        background_tasks.add_task(log_intelligent_healing, request, result)
        
        return HealingResponse(
            success=result.get("success", False),
            action_taken=result.get("action_taken", "unknown"),
            layer_used=result.get("layer_used", "unknown"),
            details=result.get("details", {}),
            timestamp=result.get("timestamp", datetime.now().isoformat()),
            estimated_improvement=result.get("estimated_improvement", 0)
        )
        
    except Exception as e:
        logger.error(f"Error performing intelligent healing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-intelligent-monitoring")
async def start_intelligent_monitoring(interval: int = 30):
    """Start intelligent monitoring with automatic healing"""
    try:
        service = await get_enhanced_autopilot_service()
        
        # Start monitoring in background
        import asyncio
        asyncio.create_task(service.start_intelligent_monitoring(interval))
        
        return {
            "success": True,
            "message": f"Intelligent monitoring started with {interval}s interval",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting intelligent monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-intelligent-monitoring")
async def stop_intelligent_monitoring():
    """Stop intelligent monitoring"""
    try:
        service = await get_enhanced_autopilot_service()
        await service.stop_monitoring()
        
        return {
            "success": True,
            "message": "Intelligent monitoring stopped",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error stopping intelligent monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictive-insights", response_model=Dict[str, Any])
async def get_predictive_insights():
    """Get predictive insights about system health and potential issues"""
    try:
        service = await get_enhanced_autopilot_service()
        insights = await service.get_predictive_insights()
        
        return {
            "success": True,
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting predictive insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/real-time-metrics", response_model=Dict[str, Any])
async def get_real_time_metrics():
    """Get real-time system metrics"""
    try:
        service = await get_enhanced_autopilot_service()
        
        if not service.is_initialized:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Get current metrics
        current_metrics = await service.system_monitor.get_current_metrics()
        health_score = await service.system_monitor.get_system_health_score()
        issues = await service.system_monitor.detect_issues()
        
        return {
            "success": True,
            "metrics": {
                "timestamp": datetime.now().isoformat(),
                "health_score": health_score,
                "cpu_percent": current_metrics.cpu_percent,
                "memory_percent": current_metrics.memory_percent,
                "disk_percent": current_metrics.disk_percent,
                "temperature": current_metrics.temperature,
                "battery_percent": current_metrics.battery_percent,
                "uptime_hours": current_metrics.uptime_seconds / 3600,
                "processes_count": current_metrics.processes_count,
                "network_connections": current_metrics.network_connections
            },
            "issues_detected": issues,
            "monitoring_status": "active" if service.is_monitoring else "inactive"
        }
        
    except Exception as e:
        logger.error(f"Error getting real-time metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/healing-statistics", response_model=Dict[str, Any])
async def get_healing_statistics():
    """Get comprehensive healing statistics"""
    try:
        service = await get_enhanced_autopilot_service()
        
        if not service.is_initialized:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Get healing success rate
        success_rate = await service.database.get_healing_success_rate()
        
        # Get recent actions
        recent_actions = await service.database.get_healing_actions(limit=50)
        
        # Get database statistics
        db_stats = await service.database.get_database_stats()
        
        return {
            "success": True,
            "statistics": {
                "success_rate": success_rate,
                "total_actions": service.healing_stats["total_actions"],
                "successful_actions": service.healing_stats["successful_actions"],
                "failed_actions": service.healing_stats["failed_actions"],
                "last_healing_time": service.healing_stats["last_healing_time"].isoformat() if service.healing_stats["last_healing_time"] else None,
                "average_improvement": service.healing_stats["average_improvement"]
            },
            "recent_actions": recent_actions,
            "database_stats": db_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting healing statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emergency-healing")
async def perform_emergency_healing(context: Dict[str, Any] = {}):
    """Perform emergency healing for critical system issues"""
    try:
        service = await get_enhanced_autopilot_service()
        
        if not service.is_initialized:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Get current system state
        current_metrics = await service.system_monitor.get_current_metrics()
        health_score = await service.system_monitor.get_system_health_score()
        
        # Determine emergency actions
        emergency_actions = []
        
        if health_score < 30:
            emergency_actions.append({
                "action_type": "optimize_memory",
                "target": "system_memory",
                "priority": "critical"
            })
            
            emergency_actions.append({
                "action_type": "clear_system_cache",
                "target": "system_cache",
                "priority": "critical"
            })
        
        if current_metrics.cpu_percent > 95:
            # Kill top CPU processes
            processes = await service.system_monitor.get_processes()
            high_cpu_processes = sorted(processes, key=lambda p: p.cpu_percent, reverse=True)[:3]
            
            for proc in high_cpu_processes:
                emergency_actions.append({
                    "action_type": "kill_high_cpu_process",
                    "target": str(proc.pid),
                    "priority": "critical"
                })
        
        # Execute emergency actions
        results = []
        for action in emergency_actions:
            try:
                result = await service.healing_executor.execute_healing_action(
                    action["action_type"],
                    action["target"]
                )
                results.append({
                    "action": action,
                    "result": result,
                    "success": result.success
                })
            except Exception as e:
                results.append({
                    "action": action,
                    "error": str(e),
                    "success": False
                })
        
        successful_actions = sum(1 for r in results if r["success"])
        
        return {
            "success": successful_actions > 0,
            "message": f"Emergency healing completed: {successful_actions}/{len(emergency_actions)} actions successful",
            "actions_taken": len(emergency_actions),
            "successful_actions": successful_actions,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error performing emergency healing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-optimization-suggestions", response_model=Dict[str, Any])
async def get_system_optimization_suggestions():
    """Get AI-powered system optimization suggestions"""
    try:
        service = await get_enhanced_autopilot_service()
        
        if not service.is_initialized:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Get current system state
        current_metrics = await service.system_monitor.get_current_metrics()
        health_score = await service.system_monitor.get_system_health_score()
        issues = await service.system_monitor.detect_issues()
        
        suggestions = []
        
        # Memory optimization suggestions
        if current_metrics.memory_percent > 70:
            suggestions.append({
                "category": "memory",
                "priority": "high" if current_metrics.memory_percent > 85 else "medium",
                "title": "Memory Optimization",
                "description": f"Memory usage is {current_metrics.memory_percent:.1f}%. Consider optimizing memory usage.",
                "action": "optimize_memory",
                "estimated_improvement": 15
            })
        
        # CPU optimization suggestions
        if current_metrics.cpu_percent > 70:
            suggestions.append({
                "category": "cpu",
                "priority": "high" if current_metrics.cpu_percent > 85 else "medium",
                "title": "CPU Optimization",
                "description": f"CPU usage is {current_metrics.cpu_percent:.1f}%. Monitor high CPU processes.",
                "action": "monitor_cpu_processes",
                "estimated_improvement": 10
            })
        
        # Storage optimization suggestions
        if current_metrics.disk_percent > 80:
            suggestions.append({
                "category": "storage",
                "priority": "high" if current_metrics.disk_percent > 90 else "medium",
                "title": "Storage Cleanup",
                "description": f"Disk usage is {current_metrics.disk_percent:.1f}%. Clear cache and temporary files.",
                "action": "clear_system_cache",
                "estimated_improvement": 20
            })
        
        # Temperature optimization suggestions
        if current_metrics.temperature and current_metrics.temperature > 60:
            suggestions.append({
                "category": "thermal",
                "priority": "high" if current_metrics.temperature > 70 else "medium",
                "title": "Thermal Management",
                "description": f"Temperature is {current_metrics.temperature:.1f}°C. Reduce CPU load.",
                "action": "reduce_cpu_load",
                "estimated_improvement": 5
            })
        
        # Battery optimization suggestions
        if current_metrics.battery_percent and current_metrics.battery_percent < 30:
            suggestions.append({
                "category": "battery",
                "priority": "high" if current_metrics.battery_percent < 15 else "medium",
                "title": "Battery Optimization",
                "description": f"Battery is {current_metrics.battery_percent:.1f}%. Optimize power usage.",
                "action": "optimize_power",
                "estimated_improvement": 8
            })
        
        # General suggestions based on health score
        if health_score < 60:
            suggestions.append({
                "category": "general",
                "priority": "high",
                "title": "System Health Improvement",
                "description": f"Overall system health is {health_score:.1f}%. Consider comprehensive optimization.",
                "action": "comprehensive_optimization",
                "estimated_improvement": 25
            })
        
        return {
            "success": True,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions),
            "high_priority_count": sum(1 for s in suggestions if s["priority"] == "high"),
            "current_health_score": health_score,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting optimization suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def log_intelligent_healing(request: HealingRequest, result: Dict[str, Any]):
    """Background task to log intelligent healing actions"""
    try:
        logger.info(f"Intelligent healing logged: {request.issue_type} -> {result.get('action_taken', 'unknown')}")
    except Exception as e:
        logger.error(f"Error logging intelligent healing: {e}")

