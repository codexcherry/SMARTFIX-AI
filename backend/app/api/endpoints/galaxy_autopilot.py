"""
Galaxy Autopilot API Endpoints

Real system monitoring and healing endpoints integrated with SmartFix-AI
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from ...services.galaxy_autopilot_service import get_galaxy_autopilot_service, GalaxyAutopilotService
from ...core.config import settings

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/galaxy-autopilot", tags=["Galaxy Autopilot"])

@router.get("/status")
async def get_system_status():
    """Get Galaxy Autopilot system status"""
    try:
        service = get_galaxy_autopilot_service()
        
        # Get current metrics
        metrics = await service.get_system_metrics()
        
        # Get issues
        issues = await service.detect_issues()
        
        # Get healing statistics
        healing_stats = await service.get_healing_statistics()
        
        return {
            "success": True,
            "system_status": "active",
            "monitoring_status": "active" if service.is_monitoring else "inactive",
            "overall_health": metrics.get("health_score", 0),
            "current_metrics": metrics,
            "issues_detected": issues,
            "healing_statistics": healing_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_real_time_metrics():
    """Get real-time system metrics"""
    try:
        service = get_galaxy_autopilot_service()
        metrics = await service.get_system_metrics()
        
        return {
            "success": True,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting real-time metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/processes")
async def get_system_processes():
    """Get information about running processes"""
    try:
        service = get_galaxy_autopilot_service()
        processes = await service.get_processes()
        
        # Sort by CPU usage
        processes.sort(key=lambda p: p.get('cpu_percent', 0), reverse=True)
        
        return {
            "success": True,
            "processes": processes[:50],  # Return top 50 processes
            "total_processes": len(processes),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting processes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/issues")
async def get_system_issues():
    """Get detected system issues"""
    try:
        service = get_galaxy_autopilot_service()
        issues = await service.detect_issues()
        
        return {
            "success": True,
            "issues": issues,
            "total_issues": len(issues),
            "critical_issues": len([i for i in issues if i.get('severity') == 'high']),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting system issues: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/heal")
async def perform_healing_action(
    action_type: str,
    target: str,
    parameters: Optional[Dict[str, Any]] = None
):
    """Perform a healing action"""
    try:
        service = get_galaxy_autopilot_service()
        
        # Validate action type
        valid_actions = ["optimize_memory", "clear_cache", "kill_process", "restart_service", "defragment_disk"]
        if action_type not in valid_actions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid action type. Valid actions: {valid_actions}"
            )
        
        # Perform the healing action
        result = await service.perform_healing_action(action_type, target, parameters or {})
        
        return {
            "success": result.get("success", False),
            "action_type": action_type,
            "target": target,
            "duration_ms": result.get("duration_ms", 0),
            "improvement_score": result.get("improvement_score", 0),
            "details": result.get("details", {}),
            "error_message": result.get("error_message"),
            "timestamp": result.get("timestamp")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing healing action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emergency-heal")
async def perform_emergency_healing():
    """Perform emergency healing for critical issues"""
    try:
        service = get_galaxy_autopilot_service()
        
        # Get current metrics and issues
        metrics = await service.get_system_metrics()
        issues = await service.detect_issues()
        
        # Determine emergency actions
        emergency_actions = []
        
        if metrics.get('health_score', 100) < 30:
            emergency_actions.append({
                "action_type": "optimize_memory",
                "target": "system_memory",
                "reason": "Critical memory pressure"
            })
            
            emergency_actions.append({
                "action_type": "clear_cache",
                "target": "system_cache",
                "reason": "Critical disk space"
            })
        
        # Execute emergency actions
        results = []
        for action in emergency_actions:
            try:
                result = await service.perform_healing_action(
                    action["action_type"],
                    action["target"]
                )
                results.append({
                    "action": action,
                    "result": result,
                    "success": result.get("success", False)
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

@router.get("/health-report")
async def get_comprehensive_health_report():
    """Get comprehensive system health report"""
    try:
        service = get_galaxy_autopilot_service()
        
        # Get all system information
        metrics = await service.get_system_metrics()
        issues = await service.detect_issues()
        processes = await service.get_processes()
        healing_stats = await service.get_healing_statistics()
        
        # Calculate recommendations
        recommendations = []
        
        if metrics.get('cpu_percent', 0) > 70:
            recommendations.append({
                "type": "cpu_optimization",
                "priority": "high" if metrics['cpu_percent'] > 85 else "medium",
                "description": f"CPU usage is {metrics['cpu_percent']:.1f}%. Consider optimizing CPU usage.",
                "action": "monitor_high_cpu_processes"
            })
        
        if metrics.get('memory_percent', 0) > 70:
            recommendations.append({
                "type": "memory_optimization",
                "priority": "high" if metrics['memory_percent'] > 85 else "medium",
                "description": f"Memory usage is {metrics['memory_percent']:.1f}%. Consider memory optimization.",
                "action": "optimize_memory"
            })
        
        if metrics.get('disk_percent', 0) > 80:
            recommendations.append({
                "type": "storage_cleanup",
                "priority": "high" if metrics['disk_percent'] > 90 else "medium",
                "description": f"Disk usage is {metrics['disk_percent']:.1f}%. Clear cache and temporary files.",
                "action": "clear_cache"
            })
        
        # Get top resource-consuming processes
        top_cpu_processes = sorted(processes, key=lambda p: p.get('cpu_percent', 0), reverse=True)[:5]
        top_memory_processes = sorted(processes, key=lambda p: p.get('memory_percent', 0), reverse=True)[:5]
        
        return {
            "success": True,
            "report": {
                "timestamp": datetime.now().isoformat(),
                "device_id": service.device_id,
                "system_health": {
                    "overall_score": metrics.get("health_score", 0),
                    "cpu_percent": metrics.get("cpu_percent", 0),
                    "memory_percent": metrics.get("memory_percent", 0),
                    "disk_percent": metrics.get("disk_percent", 0),
                    "temperature": metrics.get("temperature"),
                    "battery_percent": metrics.get("battery_percent"),
                    "uptime_hours": metrics.get("uptime_seconds", 0) / 3600,
                    "processes_count": metrics.get("processes_count", 0),
                    "network_connections": metrics.get("network_connections", 0)
                },
                "issues_detected": issues,
                "recommendations": recommendations,
                "top_cpu_processes": top_cpu_processes,
                "top_memory_processes": top_memory_processes,
                "healing_statistics": healing_stats,
                "monitoring_status": "active" if service.is_monitoring else "inactive"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting health report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-monitoring")
async def start_monitoring(interval: int = 30):
    """Start continuous system monitoring"""
    try:
        service = get_galaxy_autopilot_service()
        
        if service.is_monitoring:
            return {
                "success": True,
                "message": "Monitoring is already active",
                "interval": interval,
                "timestamp": datetime.now().isoformat()
            }
        
        # Start monitoring in background
        import asyncio
        asyncio.create_task(service.start_monitoring(interval))
        
        return {
            "success": True,
            "message": f"Continuous monitoring started with {interval}s interval",
            "interval": interval,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-monitoring")
async def stop_monitoring():
    """Stop continuous system monitoring"""
    try:
        service = get_galaxy_autopilot_service()
        await service.stop_monitoring()
        
        return {
            "success": True,
            "message": "Continuous monitoring stopped",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_healing_statistics():
    """Get healing statistics"""
    try:
        service = get_galaxy_autopilot_service()
        stats = await service.get_healing_statistics()
        
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting healing statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/optimization-suggestions")
async def get_optimization_suggestions():
    """Get system optimization suggestions"""
    try:
        service = get_galaxy_autopilot_service()
        
        # Get current metrics
        metrics = await service.get_system_metrics()
        issues = await service.detect_issues()
        
        suggestions = []
        
        # CPU optimization suggestions
        if metrics.get('cpu_percent', 0) > 70:
            suggestions.append({
                "category": "cpu",
                "priority": "high" if metrics['cpu_percent'] > 85 else "medium",
                "title": "CPU Optimization",
                "description": f"CPU usage is {metrics['cpu_percent']:.1f}%. Monitor high CPU processes.",
                "action": "monitor_cpu_processes",
                "estimated_improvement": 10
            })
        
        # Memory optimization suggestions
        if metrics.get('memory_percent', 0) > 70:
            suggestions.append({
                "category": "memory",
                "priority": "high" if metrics['memory_percent'] > 85 else "medium",
                "title": "Memory Optimization",
                "description": f"Memory usage is {metrics['memory_percent']:.1f}%. Consider optimizing memory usage.",
                "action": "optimize_memory",
                "estimated_improvement": 15
            })
        
        # Storage optimization suggestions
        if metrics.get('disk_percent', 0) > 80:
            suggestions.append({
                "category": "storage",
                "priority": "high" if metrics['disk_percent'] > 90 else "medium",
                "title": "Storage Cleanup",
                "description": f"Disk usage is {metrics['disk_percent']:.1f}%. Clear cache and temporary files.",
                "action": "clear_cache",
                "estimated_improvement": 20
            })
        
        # Temperature optimization suggestions
        if metrics.get('temperature') and metrics['temperature'] > 60:
            suggestions.append({
                "category": "thermal",
                "priority": "high" if metrics['temperature'] > 70 else "medium",
                "title": "Thermal Management",
                "description": f"Temperature is {metrics['temperature']:.1f}°C. Reduce CPU load.",
                "action": "reduce_cpu_load",
                "estimated_improvement": 5
            })
        
        # Battery optimization suggestions
        if metrics.get('battery_percent') and metrics['battery_percent'] < 30:
            suggestions.append({
                "category": "battery",
                "priority": "high" if metrics['battery_percent'] < 15 else "medium",
                "title": "Battery Optimization",
                "description": f"Battery is {metrics['battery_percent']:.1f}%. Optimize power usage.",
                "action": "optimize_power",
                "estimated_improvement": 8
            })
        
        # General suggestions based on health score
        health_score = metrics.get('health_score', 100)
        if health_score < 60:
            suggestions.append({
                "category": "general",
                "priority": "high",
                "title": "System Health Improvement",
                "description": f"Overall system health is {health_score:.1f}. Consider comprehensive optimization.",
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
