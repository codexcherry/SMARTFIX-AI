"""
Galaxy Autopilot Service Integration

Integrates Galaxy Autopilot with SmartFix-AI services to provide
real system monitoring and healing capabilities.
"""

import asyncio
import logging
import psutil
import subprocess
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os
import platform

logger = logging.getLogger(__name__)

class GalaxyAutopilotService:
    """
    Galaxy Autopilot service integrated with SmartFix-AI
    """
    
    def __init__(self):
        self.device_id = "smartfix_device"
        self.is_monitoring = False
        self.healing_stats = {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "last_healing_time": None
        }
        
        # System thresholds
        self.thresholds = {
            "cpu_high": 80.0,
            "memory_high": 85.0,
            "disk_high": 90.0,
            "temperature_high": 70.0,
            "battery_low": 20.0
        }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get real system metrics"""
        try:
            # Get CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            
            # Get memory information
            memory = psutil.virtual_memory()
            
            # Get disk information
            disk = psutil.disk_usage('/')
            
            # Get network information
            net_io = psutil.net_io_counters()
            
            # Get boot time and uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime_seconds = time.time() - psutil.boot_time()
            
            # Get temperature (if available)
            temperature = None
            try:
                if hasattr(psutil, "sensors_temperatures"):
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            if entries:
                                temperature = entries[0].current
                                break
            except Exception:
                pass
            
            # Get battery information (if available)
            battery_percent = None
            battery_plugged = None
            try:
                battery = psutil.sensors_battery()
                if battery:
                    battery_percent = battery.percent
                    battery_plugged = battery.power_plugged
            except Exception:
                pass
            
            # Calculate health score
            health_score = await self._calculate_health_score(
                cpu_percent, memory.percent, (disk.used / disk.total) * 100,
                temperature, battery_percent
            )
            
            return {
                "timestamp": datetime.now().isoformat(),
                "device_id": self.device_id,
                "cpu_percent": cpu_percent,
                "cpu_freq": cpu_freq.current if cpu_freq else None,
                "memory_total": memory.total,
                "memory_available": memory.available,
                "memory_percent": memory.percent,
                "memory_used": memory.used,
                "disk_total": disk.total,
                "disk_free": disk.free,
                "disk_percent": (disk.used / disk.total) * 100,
                "network_bytes_sent": net_io.bytes_sent,
                "network_bytes_recv": net_io.bytes_recv,
                "network_connections": len(psutil.net_connections()),
                "processes_count": len(psutil.pids()),
                "boot_time": boot_time.isoformat(),
                "uptime_seconds": uptime_seconds,
                "temperature": temperature,
                "battery_percent": battery_percent,
                "battery_plugged": battery_plugged,
                "health_score": health_score,
                "platform": platform.system(),
                "platform_version": platform.version()
            }
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "device_id": self.device_id,
                "error": str(e),
                "health_score": 50.0
            }
    
    async def _calculate_health_score(self, cpu_percent: float, memory_percent: float, 
                                    disk_percent: float, temperature: Optional[float], 
                                    battery_percent: Optional[float]) -> float:
        """Calculate overall system health score (0-100)"""
        try:
            score = 100.0
            
            # CPU penalty
            if cpu_percent > self.thresholds["cpu_high"]:
                score -= (cpu_percent - self.thresholds["cpu_high"]) * 0.5
            
            # Memory penalty
            if memory_percent > self.thresholds["memory_high"]:
                score -= (memory_percent - self.thresholds["memory_high"]) * 0.5
            
            # Disk penalty
            if disk_percent > self.thresholds["disk_high"]:
                score -= (disk_percent - self.thresholds["disk_high"]) * 0.3
            
            # Temperature penalty
            if temperature and temperature > self.thresholds["temperature_high"]:
                score -= (temperature - self.thresholds["temperature_high"]) * 0.2
            
            # Battery penalty
            if battery_percent and battery_percent < self.thresholds["battery_low"]:
                score -= (self.thresholds["battery_low"] - battery_percent) * 0.1
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return 50.0
    
    async def get_processes(self) -> List[Dict[str, Any]]:
        """Get information about running processes"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                           'memory_info', 'status', 'create_time', 'cmdline', 
                                           'username', 'nice', 'num_threads']):
                try:
                    proc_info = proc.info
                    processes.append({
                        "pid": proc_info['pid'],
                        "name": proc_info['name'],
                        "cpu_percent": proc_info['cpu_percent'] or 0.0,
                        "memory_percent": proc_info['memory_percent'] or 0.0,
                        "memory_rss": proc_info['memory_info'].rss if proc_info['memory_info'] else 0,
                        "memory_vms": proc_info['memory_info'].vms if proc_info['memory_info'] else 0,
                        "status": proc_info['status'],
                        "create_time": datetime.fromtimestamp(proc_info['create_time']).isoformat(),
                        "cmdline": proc_info['cmdline'] or [],
                        "username": proc_info['username'] or 'unknown',
                        "nice": proc_info['nice'],
                        "num_threads": proc_info['num_threads']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            logger.error(f"Error getting processes: {e}")
        
        return processes
    
    async def detect_issues(self) -> List[Dict[str, Any]]:
        """Detect system issues based on current metrics"""
        issues = []
        
        try:
            metrics = await self.get_system_metrics()
            
            # High CPU usage
            if metrics.get('cpu_percent', 0) > self.thresholds["cpu_high"]:
                issues.append({
                    "type": "high_cpu",
                    "severity": "high" if metrics['cpu_percent'] > 90 else "medium",
                    "description": f"CPU usage is {metrics['cpu_percent']:.1f}%",
                    "value": metrics['cpu_percent'],
                    "threshold": self.thresholds["cpu_high"]
                })
            
            # High memory usage
            if metrics.get('memory_percent', 0) > self.thresholds["memory_high"]:
                issues.append({
                    "type": "high_memory",
                    "severity": "high" if metrics['memory_percent'] > 95 else "medium",
                    "description": f"Memory usage is {metrics['memory_percent']:.1f}%",
                    "value": metrics['memory_percent'],
                    "threshold": self.thresholds["memory_high"]
                })
            
            # High disk usage
            if metrics.get('disk_percent', 0) > self.thresholds["disk_high"]:
                issues.append({
                    "type": "high_disk",
                    "severity": "high" if metrics['disk_percent'] > 95 else "medium",
                    "description": f"Disk usage is {metrics['disk_percent']:.1f}%",
                    "value": metrics['disk_percent'],
                    "threshold": self.thresholds["disk_high"]
                })
            
            # High temperature
            if metrics.get('temperature') and metrics['temperature'] > self.thresholds["temperature_high"]:
                issues.append({
                    "type": "high_temperature",
                    "severity": "high" if metrics['temperature'] > 80 else "medium",
                    "description": f"Temperature is {metrics['temperature']:.1f}°C",
                    "value": metrics['temperature'],
                    "threshold": self.thresholds["temperature_high"]
                })
            
            # Low battery
            if metrics.get('battery_percent') and metrics['battery_percent'] < self.thresholds["battery_low"]:
                issues.append({
                    "type": "low_battery",
                    "severity": "high" if metrics['battery_percent'] < 10 else "medium",
                    "description": f"Battery is {metrics['battery_percent']:.1f}%",
                    "value": metrics['battery_percent'],
                    "threshold": self.thresholds["battery_low"]
                })
            
        except Exception as e:
            logger.error(f"Error detecting issues: {e}")
        
        return issues
    
    async def perform_healing_action(self, action_type: str, target: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform a healing action"""
        parameters = parameters or {}
        start_time = time.time()
        
        try:
            if action_type == "optimize_memory":
                result = await self._optimize_memory()
            elif action_type == "clear_cache":
                result = await self._clear_cache()
            elif action_type == "kill_process":
                result = await self._kill_process(int(target))
            elif action_type == "restart_service":
                result = await self._restart_service(target)
            elif action_type == "defragment_disk":
                result = await self._defragment_disk(parameters.get('drive', 'C:'))
            else:
                result = {
                    "success": False,
                    "error": f"Unknown action type: {action_type}"
                }
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Update statistics
            self.healing_stats["total_actions"] += 1
            if result.get("success", False):
                self.healing_stats["successful_actions"] += 1
            else:
                self.healing_stats["failed_actions"] += 1
            self.healing_stats["last_healing_time"] = datetime.now()
            
            return {
                "success": result.get("success", False),
                "action_type": action_type,
                "target": target,
                "duration_ms": duration_ms,
                "improvement_score": result.get("improvement_score", 0.0),
                "details": result.get("details", {}),
                "error_message": result.get("error"),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error performing healing action: {e}")
            return {
                "success": False,
                "action_type": action_type,
                "target": target,
                "duration_ms": int((time.time() - start_time) * 1000),
                "improvement_score": 0.0,
                "details": {"error": str(e)},
                "error_message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _optimize_memory(self) -> Dict[str, Any]:
        """Optimize memory usage"""
        try:
            # Get memory info before optimization
            memory_before = psutil.virtual_memory()
            
            # Clear Python garbage collection
            import gc
            gc.collect()
            
            # Clear system caches (platform specific)
            if platform.system() == "Linux":
                try:
                    subprocess.run(['sync'], check=True)
                    with open('/proc/sys/vm/drop_caches', 'w') as f:
                        f.write('3')
                except (subprocess.CalledProcessError, PermissionError):
                    pass
            
            # Wait for memory to be freed
            await asyncio.sleep(2)
            
            # Get memory info after optimization
            memory_after = psutil.virtual_memory()
            
            memory_freed = memory_before.used - memory_after.used
            improvement_percent = (memory_freed / memory_before.total) * 100
            
            return {
                "success": True,
                "improvement_score": min(1.0, improvement_percent / 10),
                "details": {
                    "memory_before_mb": memory_before.used / (1024 * 1024),
                    "memory_after_mb": memory_after.used / (1024 * 1024),
                    "memory_freed_mb": memory_freed / (1024 * 1024),
                    "improvement_percent": improvement_percent
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _clear_cache(self) -> Dict[str, Any]:
        """Clear system cache and temporary files"""
        try:
            cleared_size = 0
            cleared_files = 0
            
            # Get temp directories
            temp_dirs = []
            if platform.system() == "Windows":
                temp_dirs.extend([
                    os.environ.get('TEMP', ''),
                    os.environ.get('TMP', ''),
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp')
                ])
            else:
                temp_dirs.extend(['/tmp', '/var/tmp'])
            
            # Clear temp directories
            for temp_dir in temp_dirs:
                if temp_dir and os.path.exists(temp_dir):
                    try:
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                try:
                                    file_path = os.path.join(root, file)
                                    file_size = os.path.getsize(file_path)
                                    os.remove(file_path)
                                    cleared_size += file_size
                                    cleared_files += 1
                                except (OSError, PermissionError):
                                    continue
                    except (OSError, PermissionError):
                        continue
            
            return {
                "success": True,
                "improvement_score": 0.6,
                "details": {
                    "cleared_files": cleared_files,
                    "cleared_size_mb": cleared_size / (1024 * 1024),
                    "temp_dirs_cleared": len(temp_dirs)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _kill_process(self, pid: int) -> Dict[str, Any]:
        """Kill a process by PID"""
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            # Check if it's a critical system process
            critical_processes = {
                'system', 'kernel', 'init', 'systemd', 'winlogon', 'csrss',
                'wininit', 'services', 'lsass', 'svchost', 'explorer'
            }
            
            if process_name.lower() in critical_processes:
                return {
                    "success": False,
                    "error": "Critical system process, cannot kill"
                }
            
            # Kill the process
            process.kill()
            process.wait(timeout=5)
            
            return {
                "success": True,
                "improvement_score": 0.8,
                "details": {
                    "process_name": process_name,
                    "pid": pid,
                    "cpu_usage_before": process.cpu_percent()
                }
            }
            
        except psutil.NoSuchProcess:
            return {
                "success": False,
                "error": "Process not found"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _restart_service(self, service_name: str) -> Dict[str, Any]:
        """Restart a system service"""
        try:
            # Get the appropriate command for the platform
            if platform.system() == "Windows":
                cmd = f"net stop {service_name} && net start {service_name}"
            elif platform.system() == "Linux":
                cmd = f"systemctl restart {service_name}"
            else:  # macOS
                cmd = f"sudo launchctl unload {service_name} && sudo launchctl load {service_name}"
            
            # Execute the command
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "improvement_score": 0.7,
                    "details": {
                        "service_name": service_name,
                        "command": cmd,
                        "output": result.stdout
                    }
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _defragment_disk(self, drive: str) -> Dict[str, Any]:
        """Defragment a disk drive"""
        try:
            # Get the appropriate command for the platform
            if platform.system() == "Windows":
                cmd = f"defrag {drive} /O"
            elif platform.system() == "Linux":
                cmd = "sudo e4defrag /"
            else:  # macOS
                cmd = "sudo diskutil defragmentVolume /"
            
            # Execute the command
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "improvement_score": 0.5,
                    "details": {
                        "drive": drive,
                        "command": cmd,
                        "output": result.stdout
                    }
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Defragmentation timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_healing_statistics(self) -> Dict[str, Any]:
        """Get healing statistics"""
        total_actions = self.healing_stats["total_actions"]
        success_rate = (self.healing_stats["successful_actions"] / total_actions * 100) if total_actions > 0 else 0
        
        return {
            "total_actions": total_actions,
            "successful_actions": self.healing_stats["successful_actions"],
            "failed_actions": self.healing_stats["failed_actions"],
            "success_rate": success_rate,
            "last_healing_time": self.healing_stats["last_healing_time"].isoformat() if self.healing_stats["last_healing_time"] else None
        }
    
    async def start_monitoring(self, interval: int = 30):
        """Start continuous monitoring"""
        self.is_monitoring = True
        logger.info(f"Starting Galaxy Autopilot monitoring with {interval}s interval")
        
        while self.is_monitoring:
            try:
                # Get current metrics
                metrics = await self.get_system_metrics()
                
                # Detect issues
                issues = await self.detect_issues()
                
                # Log issues if any
                if issues:
                    logger.warning(f"Detected {len(issues)} system issues")
                    for issue in issues:
                        logger.warning(f"Issue: {issue['description']}")
                
                # Check for proactive healing
                if metrics.get('health_score', 100) < 70:
                    logger.info("System health is low, considering proactive healing")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.is_monitoring = False
        logger.info("Galaxy Autopilot monitoring stopped")

# Global service instance
_galaxy_autopilot_service = None

def get_galaxy_autopilot_service() -> GalaxyAutopilotService:
    """Get or create the Galaxy Autopilot service instance"""
    global _galaxy_autopilot_service
    if _galaxy_autopilot_service is None:
        _galaxy_autopilot_service = GalaxyAutopilotService()
    return _galaxy_autopilot_service

