"""
Enhanced Galaxy Autopilot Service

Integrates Galaxy Autopilot with SmartFix-AI to provide intelligent
system healing and optimization capabilities.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from ..core.ai_engine import GalaxyAutopilotAI
from ..core.system_monitor import RealSystemMonitor
from ..core.database import GalaxyAutopilotDatabase
from ..core.healing_executor import RealHealingExecutor

logger = logging.getLogger(__name__)

class EnhancedAutopilotService:
    """
    Enhanced Galaxy Autopilot service that integrates with SmartFix-AI
    """
    
    def __init__(self, device_id: str = "smartfix_device"):
        self.device_id = device_id
        self.ai_engine = None
        self.system_monitor = None
        self.database = None
        self.healing_executor = None
        self.is_initialized = False
        self.is_monitoring = False
        
        # Performance tracking
        self.healing_stats = {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "last_healing_time": None,
            "average_improvement": 0.0
        }
    
    async def initialize(self):
        """Initialize the enhanced autopilot service"""
        try:
            logger.info("Initializing Enhanced Galaxy Autopilot Service")
            
            # Initialize core components
            self.system_monitor = RealSystemMonitor(self.device_id)
            self.database = GalaxyAutopilotDatabase()
            self.healing_executor = RealHealingExecutor(self.device_id)
            
            # Initialize database
            await self.database.initialize()
            
            # Initialize AI engine
            self.ai_engine = GalaxyAutopilotAI(self.device_id)
            await self.ai_engine.initialize()
            
            # Set up AI engine with real components
            self.ai_engine.system_monitor = self.system_monitor
            self.ai_engine.database = self.database
            self.ai_engine.healing_executor = self.healing_executor
            
            self.is_initialized = True
            logger.info("Enhanced Galaxy Autopilot Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Galaxy Autopilot Service: {e}")
            raise
    
    async def start_intelligent_monitoring(self, interval: int = 30):
        """Start intelligent monitoring with automatic healing"""
        if not self.is_initialized:
            await self.initialize()
        
        self.is_monitoring = True
        logger.info(f"Starting intelligent monitoring with {interval}s interval")
        
        while self.is_monitoring:
            try:
                # Get current system state
                current_state = await self.system_monitor.get_current_metrics()
                
                # Save metrics to database
                health_score = await self.system_monitor.get_system_health_score()
                await self.database.save_system_metrics(
                    self.device_id, 
                    current_state.__dict__, 
                    health_score
                )
                
                # Detect issues
                issues = await self.system_monitor.detect_issues()
                
                # Process issues with AI
                if issues:
                    await self._process_issues_with_ai(issues)
                
                # Check for proactive healing opportunities
                if health_score < 70:
                    await self._perform_proactive_healing()
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in intelligent monitoring: {e}")
                await asyncio.sleep(interval)
    
    async def _process_issues_with_ai(self, issues: List[Dict[str, Any]]):
        """Process detected issues using AI engine"""
        try:
            for issue in issues:
                logger.info(f"Processing issue: {issue['description']}")
                
                # Determine issue type and severity
                issue_type = self._map_issue_type(issue['type'])
                severity = issue['severity']
                
                # Create context for AI
                context = {
                    "issue_details": issue,
                    "proactive": True,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Process with AI engine
                result = await self.ai_engine.process_healing_request(
                    issue_type=issue_type,
                    severity=severity,
                    context=context
                )
                
                # Log the result
                if result.get('success'):
                    logger.info(f"AI successfully processed issue: {issue['description']}")
                    self.healing_stats["successful_actions"] += 1
                else:
                    logger.warning(f"AI failed to process issue: {issue['description']}")
                    self.healing_stats["failed_actions"] += 1
                
                self.healing_stats["total_actions"] += 1
                self.healing_stats["last_healing_time"] = datetime.now()
                
        except Exception as e:
            logger.error(f"Error processing issues with AI: {e}")
    
    async def _perform_proactive_healing(self):
        """Perform proactive healing when system health is low"""
        try:
            logger.info("Performing proactive healing due to low system health")
            
            # Get current system state
            current_state = await self.system_monitor.get_current_metrics()
            
            # Determine proactive actions based on current state
            proactive_actions = []
            
            if current_state.memory_percent > 80:
                proactive_actions.append({
                    "action_type": "optimize_memory",
                    "target": "system_memory",
                    "reason": "High memory usage"
                })
            
            if current_state.cpu_percent > 80:
                # Find high CPU processes
                processes = await self.system_monitor.get_processes()
                high_cpu_processes = [p for p in processes if p.cpu_percent > 50]
                
                for proc in high_cpu_processes[:3]:  # Limit to 3 processes
                    proactive_actions.append({
                        "action_type": "kill_high_cpu_process",
                        "target": str(proc.pid),
                        "reason": f"High CPU usage: {proc.cpu_percent:.1f}%"
                    })
            
            if current_state.disk_percent > 85:
                proactive_actions.append({
                    "action_type": "clear_system_cache",
                    "target": "system_cache",
                    "reason": "High disk usage"
                })
            
            # Execute proactive actions
            for action in proactive_actions:
                try:
                    result = await self.healing_executor.execute_healing_action(
                        action["action_type"],
                        action["target"]
                    )
                    
                    # Save to database
                    from ..core.database import HealingAction
                    healing_action = HealingAction(
                        id=None,
                        action_type=action["action_type"],
                        layer="proactive",
                        target=action["target"],
                        parameters={"reason": action["reason"]},
                        success=result.success,
                        timestamp=datetime.now(),
                        duration_ms=result.duration_ms,
                        improvement_score=result.improvement_score,
                        user_feedback=None,
                        error_message=result.error_message
                    )
                    
                    await self.database.save_healing_action(healing_action)
                    
                    logger.info(f"Proactive action completed: {action['action_type']} - {result.success}")
                    
                except Exception as e:
                    logger.error(f"Error executing proactive action {action['action_type']}: {e}")
            
        except Exception as e:
            logger.error(f"Error in proactive healing: {e}")
    
    def _map_issue_type(self, issue_type: str) -> str:
        """Map system issue type to AI engine issue type"""
        mapping = {
            "high_cpu": "performance",
            "high_memory": "performance",
            "high_disk": "storage",
            "high_temperature": "performance",
            "low_battery": "battery",
            "high_cpu_process": "performance",
            "high_memory_process": "performance"
        }
        return mapping.get(issue_type, "performance")
    
    async def get_system_health_report(self) -> Dict[str, Any]:
        """Get comprehensive system health report"""
        try:
            if not self.is_initialized:
                return {"error": "Service not initialized"}
            
            # Get current metrics
            current_metrics = await self.system_monitor.get_current_metrics()
            health_score = await self.system_monitor.get_system_health_score()
            issues = await self.system_monitor.detect_issues()
            
            # Get healing statistics
            healing_success_rate = await self.database.get_healing_success_rate()
            
            # Get recent healing actions
            recent_actions = await self.database.get_healing_actions(limit=10)
            
            # Get database statistics
            db_stats = await self.database.get_database_stats()
            
            return {
                "device_id": self.device_id,
                "timestamp": datetime.now().isoformat(),
                "system_health": {
                    "overall_score": health_score,
                    "cpu_percent": current_metrics.cpu_percent,
                    "memory_percent": current_metrics.memory_percent,
                    "disk_percent": current_metrics.disk_percent,
                    "temperature": current_metrics.temperature,
                    "battery_percent": current_metrics.battery_percent,
                    "uptime_hours": current_metrics.uptime_seconds / 3600
                },
                "issues_detected": issues,
                "healing_statistics": {
                    "success_rate": healing_success_rate,
                    "total_actions": self.healing_stats["total_actions"],
                    "successful_actions": self.healing_stats["successful_actions"],
                    "failed_actions": self.healing_stats["failed_actions"],
                    "last_healing_time": self.healing_stats["last_healing_time"].isoformat() if self.healing_stats["last_healing_time"] else None
                },
                "recent_actions": recent_actions,
                "database_stats": db_stats,
                "monitoring_status": "active" if self.is_monitoring else "inactive"
            }
            
        except Exception as e:
            logger.error(f"Error getting system health report: {e}")
            return {"error": str(e)}
    
    async def perform_manual_healing(self, issue_type: str, severity: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform manual healing action"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            context = context or {}
            context["manual"] = True
            
            # Process with AI engine
            result = await self.ai_engine.process_healing_request(
                issue_type=issue_type,
                severity=severity,
                context=context
            )
            
            return {
                "success": result.get("success", False),
                "action_taken": result.get("action", "unknown"),
                "layer_used": result.get("layer", "unknown"),
                "details": result.get("details", {}),
                "timestamp": datetime.now().isoformat(),
                "estimated_improvement": result.get("estimated_improvement", 0)
            }
            
        except Exception as e:
            logger.error(f"Error performing manual healing: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_predictive_insights(self) -> Dict[str, Any]:
        """Get predictive insights about system health"""
        try:
            if not self.is_initialized:
                return {"error": "Service not initialized"}
            
            # Get historical metrics
            historical_metrics = await self.database.get_system_metrics_history(self.device_id, hours=24)
            
            # Simple trend analysis
            if len(historical_metrics) >= 2:
                recent_health = historical_metrics[0]['health_score']
                older_health = historical_metrics[-1]['health_score']
                trend = "improving" if recent_health > older_health else "degrading"
                trend_magnitude = abs(recent_health - older_health)
            else:
                trend = "stable"
                trend_magnitude = 0
            
            # Predict potential issues
            current_metrics = await self.system_monitor.get_current_metrics()
            predictions = []
            
            if current_metrics.memory_percent > 70:
                predictions.append({
                    "type": "memory_pressure",
                    "probability": min(1.0, (current_metrics.memory_percent - 70) / 30),
                    "time_horizon": "1-2 hours",
                    "recommendation": "Consider memory optimization"
                })
            
            if current_metrics.cpu_percent > 70:
                predictions.append({
                    "type": "cpu_overload",
                    "probability": min(1.0, (current_metrics.cpu_percent - 70) / 30),
                    "time_horizon": "30 minutes",
                    "recommendation": "Monitor high CPU processes"
                })
            
            if current_metrics.disk_percent > 80:
                predictions.append({
                    "type": "storage_full",
                    "probability": min(1.0, (current_metrics.disk_percent - 80) / 20),
                    "time_horizon": "2-4 hours",
                    "recommendation": "Clear cache and temporary files"
                })
            
            return {
                "timestamp": datetime.now().isoformat(),
                "health_trend": {
                    "direction": trend,
                    "magnitude": trend_magnitude,
                    "confidence": 0.8 if len(historical_metrics) >= 5 else 0.5
                },
                "predictions": predictions,
                "recommendations": [
                    "Continue monitoring system health",
                    "Consider proactive maintenance if trends continue",
                    "Review healing action effectiveness"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting predictive insights: {e}")
            return {"error": str(e)}
    
    async def stop_monitoring(self):
        """Stop intelligent monitoring"""
        self.is_monitoring = False
        logger.info("Intelligent monitoring stopped")
    
    async def shutdown(self):
        """Shutdown the enhanced autopilot service"""
        try:
            self.is_monitoring = False
            
            if self.database:
                await self.database.close()
            
            logger.info("Enhanced Galaxy Autopilot Service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Global service instance
_enhanced_autopilot_service = None

async def get_enhanced_autopilot_service() -> EnhancedAutopilotService:
    """Get or create the enhanced autopilot service instance"""
    global _enhanced_autopilot_service
    if _enhanced_autopilot_service is None:
        _enhanced_autopilot_service = EnhancedAutopilotService()
        await _enhanced_autopilot_service.initialize()
    return _enhanced_autopilot_service

