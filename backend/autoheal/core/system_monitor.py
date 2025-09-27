"""
Real System Monitor for Galaxy Autopilot

Collects actual system data including CPU, memory, disk, network, processes,
and application information for real-time monitoring and healing decisions.
"""

import asyncio
import logging
import psutil
import subprocess
import platform
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import os
import sys

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """Real system metrics data"""
    timestamp: datetime
    cpu_percent: float
    cpu_freq: Dict[str, float]
    memory_total: int
    memory_available: int
    memory_percent: float
    memory_used: int
    disk_total: int
    disk_free: int
    disk_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    network_connections: int
    processes_count: int
    boot_time: datetime
    uptime_seconds: float
    temperature: Optional[float]
    battery_percent: Optional[float]
    battery_plugged: Optional[bool]

@dataclass
class ProcessInfo:
    """Real process information"""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_rss: int
    memory_vms: int
    status: str
    create_time: datetime
    cmdline: List[str]
    username: str
    nice: int
    num_threads: int

@dataclass
class ApplicationInfo:
    """Real application information"""
    name: str
    pid: Optional[int]
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str
    start_time: Optional[datetime]
    is_system_app: bool
    crash_count: int
    network_usage: int

class RealSystemMonitor:
    """
    Real system monitor that collects actual system data
    """
    
    def __init__(self, device_id: str = "galaxy_device"):
        self.device_id = device_id
        self.is_monitoring = False
        self.metrics_history = []
        self.process_history = []
        self.application_history = []
        self.network_stats = {}
        self.start_time = time.time()
        
        # Performance thresholds
        self.thresholds = {
            "cpu_high": 80.0,
            "memory_high": 85.0,
            "disk_high": 90.0,
            "temperature_high": 70.0,
            "battery_low": 20.0,
            "process_cpu_high": 50.0,
            "process_memory_high": 30.0
        }
        
        # Initialize network baseline
        self._initialize_network_baseline()
    
    def _initialize_network_baseline(self):
        """Initialize network statistics baseline"""
        try:
            net_io = psutil.net_io_counters()
            self.network_stats = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin,
                "errout": net_io.errout,
                "dropin": net_io.dropin,
                "dropout": net_io.dropout
            }
        except Exception as e:
            logger.error(f"Error initializing network baseline: {e}")
            self.network_stats = {}
    
    async def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
            
            # Memory information
            memory = psutil.virtual_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            # Network information
            net_io = psutil.net_io_counters()
            
            # Process count
            processes_count = len(psutil.pids())
            
            # Boot time and uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime_seconds = time.time() - psutil.boot_time()
            
            # Temperature (if available)
            temperature = None
            try:
                if hasattr(psutil, "sensors_temperatures"):
                    temps = psutil.sensors_temperatures()
                    if temps:
                        # Get the first available temperature sensor
                        for name, entries in temps.items():
                            if entries:
                                temperature = entries[0].current
                                break
            except Exception:
                pass
            
            # Battery information (if available)
            battery_percent = None
            battery_plugged = None
            try:
                battery = psutil.sensors_battery()
                if battery:
                    battery_percent = battery.percent
                    battery_plugged = battery.power_plugged
            except Exception:
                pass
            
            # Network connections
            network_connections = len(psutil.net_connections())
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                cpu_freq=cpu_freq,
                memory_total=memory.total,
                memory_available=memory.available,
                memory_percent=memory.percent,
                memory_used=memory.used,
                disk_total=disk.total,
                disk_free=disk.free,
                disk_percent=(disk.used / disk.total) * 100,
                network_bytes_sent=net_io.bytes_sent,
                network_bytes_recv=net_io.bytes_recv,
                network_connections=network_connections,
                processes_count=processes_count,
                boot_time=boot_time,
                uptime_seconds=uptime_seconds,
                temperature=temperature,
                battery_percent=battery_percent,
                battery_plugged=battery_plugged
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            # Return minimal metrics on error
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                cpu_freq={},
                memory_total=0,
                memory_available=0,
                memory_percent=0.0,
                memory_used=0,
                disk_total=0,
                disk_free=0,
                disk_percent=0.0,
                network_bytes_sent=0,
                network_bytes_recv=0,
                network_connections=0,
                processes_count=0,
                boot_time=datetime.now(),
                uptime_seconds=0.0,
                temperature=None,
                battery_percent=None,
                battery_plugged=None
            )
    
    async def get_processes(self) -> List[ProcessInfo]:
        """Get detailed information about running processes"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                           'memory_info', 'status', 'create_time', 'cmdline', 
                                           'username', 'nice', 'num_threads']):
                try:
                    proc_info = proc.info
                    processes.append(ProcessInfo(
                        pid=proc_info['pid'],
                        name=proc_info['name'],
                        cpu_percent=proc_info['cpu_percent'] or 0.0,
                        memory_percent=proc_info['memory_percent'] or 0.0,
                        memory_rss=proc_info['memory_info'].rss if proc_info['memory_info'] else 0,
                        memory_vms=proc_info['memory_info'].vms if proc_info['memory_info'] else 0,
                        status=proc_info['status'],
                        create_time=datetime.fromtimestamp(proc_info['create_time']),
                        cmdline=proc_info['cmdline'] or [],
                        username=proc_info['username'] or 'unknown',
                        nice=proc_info['nice'],
                        num_threads=proc_info['num_threads']
                    ))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            logger.error(f"Error getting processes: {e}")
        
        return processes
    
    async def get_applications(self) -> List[ApplicationInfo]:
        """Get information about applications (non-system processes)"""
        applications = []
        processes = await self.get_processes()
        
        # System process names to filter out
        system_processes = {
            'systemd', 'kernel', 'init', 'kthreadd', 'ksoftirqd', 'migration',
            'rcu_', 'watchdog', 'kworker', 'kswapd', 'kcompactd', 'khugepaged',
            'oom_reaper', 'writeback', 'crypto', 'kintegrityd', 'bioset',
            'kblockd', 'ata_sff', 'md', 'dm-', 'scsi_eh', 'scsi_tmf'
        }
        
        for proc in processes:
            # Skip system processes
            if any(sys_proc in proc.name.lower() for sys_proc in system_processes):
                continue
            
            # Skip processes with very low resource usage
            if proc.cpu_percent < 0.1 and proc.memory_percent < 0.1:
                continue
            
            # Calculate network usage for this process
            network_usage = await self._get_process_network_usage(proc.pid)
            
            # Count crashes (simplified - would need actual crash logs)
            crash_count = await self._get_process_crash_count(proc.pid)
            
            applications.append(ApplicationInfo(
                name=proc.name,
                pid=proc.pid,
                cpu_percent=proc.cpu_percent,
                memory_percent=proc.memory_percent,
                memory_mb=proc.memory_rss / (1024 * 1024),
                status=proc.status,
                start_time=proc.create_time,
                is_system_app=False,  # We filtered out system apps
                crash_count=crash_count,
                network_usage=network_usage
            ))
        
        return applications
    
    async def _get_process_network_usage(self, pid: int) -> int:
        """Get network usage for a specific process"""
        try:
            # This is a simplified implementation
            # In a real system, you'd need to parse /proc/net or use specialized tools
            return 0
        except Exception:
            return 0
    
    async def _get_process_crash_count(self, pid: int) -> int:
        """Get crash count for a process (simplified)"""
        try:
            # This would typically read from system logs
            # For now, return 0 as we don't have access to crash logs
            return 0
        except Exception:
            return 0
    
    async def get_system_health_score(self) -> float:
        """Calculate overall system health score (0-100)"""
        try:
            metrics = await self.get_current_metrics()
            processes = await self.get_processes()
            
            # Base score
            score = 100.0
            
            # CPU penalty
            if metrics.cpu_percent > self.thresholds["cpu_high"]:
                score -= (metrics.cpu_percent - self.thresholds["cpu_high"]) * 0.5
            
            # Memory penalty
            if metrics.memory_percent > self.thresholds["memory_high"]:
                score -= (metrics.memory_percent - self.thresholds["memory_high"]) * 0.5
            
            # Disk penalty
            if metrics.disk_percent > self.thresholds["disk_high"]:
                score -= (metrics.disk_percent - self.thresholds["disk_high"]) * 0.3
            
            # Temperature penalty
            if metrics.temperature and metrics.temperature > self.thresholds["temperature_high"]:
                score -= (metrics.temperature - self.thresholds["temperature_high"]) * 0.2
            
            # Battery penalty
            if metrics.battery_percent and metrics.battery_percent < self.thresholds["battery_low"]:
                score -= (self.thresholds["battery_low"] - metrics.battery_percent) * 0.1
            
            # Process penalty (high CPU/memory processes)
            high_cpu_processes = sum(1 for p in processes if p.cpu_percent > self.thresholds["process_cpu_high"])
            high_memory_processes = sum(1 for p in processes if p.memory_percent > self.thresholds["process_memory_high"])
            
            score -= high_cpu_processes * 2
            score -= high_memory_processes * 1
            
            # Ensure score is between 0 and 100
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating system health score: {e}")
            return 50.0  # Default moderate health score
    
    async def detect_issues(self) -> List[Dict[str, Any]]:
        """Detect system issues based on current metrics"""
        issues = []
        metrics = await self.get_current_metrics()
        processes = await self.get_processes()
        
        # High CPU usage
        if metrics.cpu_percent > self.thresholds["cpu_high"]:
            issues.append({
                "type": "high_cpu",
                "severity": "high" if metrics.cpu_percent > 90 else "medium",
                "description": f"CPU usage is {metrics.cpu_percent:.1f}%",
                "value": metrics.cpu_percent,
                "threshold": self.thresholds["cpu_high"]
            })
        
        # High memory usage
        if metrics.memory_percent > self.thresholds["memory_high"]:
            issues.append({
                "type": "high_memory",
                "severity": "high" if metrics.memory_percent > 95 else "medium",
                "description": f"Memory usage is {metrics.memory_percent:.1f}%",
                "value": metrics.memory_percent,
                "threshold": self.thresholds["memory_high"]
            })
        
        # High disk usage
        if metrics.disk_percent > self.thresholds["disk_high"]:
            issues.append({
                "type": "high_disk",
                "severity": "high" if metrics.disk_percent > 95 else "medium",
                "description": f"Disk usage is {metrics.disk_percent:.1f}%",
                "value": metrics.disk_percent,
                "threshold": self.thresholds["disk_high"]
            })
        
        # High temperature
        if metrics.temperature and metrics.temperature > self.thresholds["temperature_high"]:
            issues.append({
                "type": "high_temperature",
                "severity": "high" if metrics.temperature > 80 else "medium",
                "description": f"Temperature is {metrics.temperature:.1f}°C",
                "value": metrics.temperature,
                "threshold": self.thresholds["temperature_high"]
            })
        
        # Low battery
        if metrics.battery_percent and metrics.battery_percent < self.thresholds["battery_low"]:
            issues.append({
                "type": "low_battery",
                "severity": "high" if metrics.battery_percent < 10 else "medium",
                "description": f"Battery is {metrics.battery_percent:.1f}%",
                "value": metrics.battery_percent,
                "threshold": self.thresholds["battery_low"]
            })
        
        # High resource processes
        for proc in processes:
            if proc.cpu_percent > self.thresholds["process_cpu_high"]:
                issues.append({
                    "type": "high_cpu_process",
                    "severity": "medium",
                    "description": f"Process {proc.name} using {proc.cpu_percent:.1f}% CPU",
                    "process": proc.name,
                    "pid": proc.pid,
                    "value": proc.cpu_percent
                })
            
            if proc.memory_percent > self.thresholds["process_memory_high"]:
                issues.append({
                    "type": "high_memory_process",
                    "severity": "medium",
                    "description": f"Process {proc.name} using {proc.memory_percent:.1f}% memory",
                    "process": proc.name,
                    "pid": proc.pid,
                    "value": proc.memory_percent
                })
        
        return issues
    
    async def start_monitoring(self, interval: int = 30):
        """Start continuous system monitoring"""
        self.is_monitoring = True
        logger.info(f"Starting system monitoring with {interval}s interval")
        
        while self.is_monitoring:
            try:
                # Collect metrics
                metrics = await self.get_current_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only last 100 metrics
                if len(self.metrics_history) > 100:
                    self.metrics_history = self.metrics_history[-100:]
                
                # Detect issues
                issues = await self.detect_issues()
                if issues:
                    logger.info(f"Detected {len(issues)} system issues")
                    for issue in issues:
                        logger.warning(f"Issue: {issue['description']}")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    async def stop_monitoring(self):
        """Stop system monitoring"""
        self.is_monitoring = False
        logger.info("System monitoring stopped")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics"""
        if not self.metrics_history:
            return {"message": "No metrics collected yet"}
        
        latest = self.metrics_history[-1]
        oldest = self.metrics_history[0]
        
        return {
            "device_id": self.device_id,
            "monitoring_duration": (latest.timestamp - oldest.timestamp).total_seconds(),
            "metrics_collected": len(self.metrics_history),
            "current_health_score": asyncio.create_task(self.get_system_health_score()),
            "latest_metrics": asdict(latest),
            "thresholds": self.thresholds
        }

