"""
Device Logs Collector Service for SmartFix-AI
Collects system logs and performance data to provide context for AI analysis
"""

import os
import sys
import platform
import psutil
import logging
import json
import time
import asyncio
import re
import socket
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class DeviceLogsCollector:
    """
    Service for collecting system logs and performance data
    to enhance AI troubleshooting capabilities
    """
    
    def __init__(self):
        """Initialize the device logs collector"""
        self.system = platform.system()  # 'Windows', 'Linux', 'Darwin' (macOS)
        self.collection_start_time = None
        self.collection_end_time = None
    
    async def collect_system_data(self, duration_seconds: int = 5) -> Dict[str, Any]:
        """
        Collect comprehensive system data including performance metrics over time
        
        Args:
            duration_seconds: How long to collect performance data (in seconds)
            
        Returns:
            Dict with collected system data
        """
        self.collection_start_time = datetime.now()
        
        # Collect basic system info immediately
        system_info = self._collect_system_info()
        
        # Collect initial performance metrics
        initial_metrics = self._collect_performance_metrics()
        
        # Collect performance samples over time
        performance_samples = []
        for _ in range(max(1, duration_seconds)):
            performance_samples.append(self._collect_performance_metrics())
            await asyncio.sleep(1)
        
        # Collect final performance metrics
        final_metrics = self._collect_performance_metrics()
        
        # Collect logs appropriate for the platform
        logs = await self._collect_system_logs()
        
        self.collection_end_time = datetime.now()
        
        # Compile all data
        return {
            "collection_start": self.collection_start_time.isoformat(),
            "collection_end": self.collection_end_time.isoformat(),
            "system_info": system_info,
            "initial_metrics": initial_metrics,
            "performance_samples": performance_samples,
            "final_metrics": final_metrics,
            "logs": logs
        }
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect basic system information"""
        info = {
            "platform": self.system,
            "platform_version": platform.version(),
            "platform_release": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python_version": platform.python_version(),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
        }
        
        # Memory information
        mem = psutil.virtual_memory()
        info["memory"] = {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "percent_used": mem.percent
        }
        
        # Disk information
        disk_info = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "filesystem": partition.fstype,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent_used": usage.percent
                })
            except (PermissionError, FileNotFoundError):
                # Skip partitions that can't be accessed
                continue
        
        info["disk"] = disk_info
        
        # Network information
        net_io = psutil.net_io_counters()
        info["network"] = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "error_in": net_io.errin,
            "error_out": net_io.errout,
            "drop_in": net_io.dropin,
            "drop_out": net_io.dropout
        }
        
        # Network interfaces
        interfaces = []
        for iface_name, iface_addresses in psutil.net_if_addrs().items():
            for addr in iface_addresses:
                if addr.family == socket.AF_INET:  # IPv4
                    interfaces.append({
                        "interface": iface_name,
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    })
        
        info["network_interfaces"] = interfaces
        
        return info
    
    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect current performance metrics"""
        timestamp = datetime.now().isoformat()
        
        metrics = {
            "timestamp": timestamp,
            "cpu": {
                "percent": psutil.cpu_percent(interval=0.5),
                "per_cpu_percent": psutil.cpu_percent(interval=0.5, percpu=True),
                "count": psutil.cpu_count(),
                "physical_count": psutil.cpu_count(logical=False)
            },
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "available_gb": round(psutil.virtual_memory().available / (1024**3), 2)
            },
            "disk": {
                "read_bytes": psutil.disk_io_counters().read_bytes,
                "write_bytes": psutil.disk_io_counters().write_bytes,
                "read_count": psutil.disk_io_counters().read_count,
                "write_count": psutil.disk_io_counters().write_count
            },
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv,
                "packets_sent": psutil.net_io_counters().packets_sent,
                "packets_recv": psutil.net_io_counters().packets_recv
            }
        }
        
        # Get top processes by CPU and memory
        processes = []
        for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']), 
                          key=lambda x: x.info['cpu_percent'], 
                          reverse=True)[:10]:  # Top 10 processes
            try:
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "cpu_percent": proc.info['cpu_percent'],
                    "memory_percent": proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process may have terminated
                continue
        
        metrics["top_processes"] = processes
        
        return metrics
    
    async def _collect_system_logs(self) -> Dict[str, Any]:
        """Collect recent system logs based on platform"""
        logs = {}
        
        try:
            if self.system == "Windows":
                # Windows Event Logs (simplified)
                logs["system"] = await self._get_windows_system_logs()
                logs["application"] = await self._get_windows_application_logs()
            
            elif self.system == "Linux":
                # Linux system logs
                logs["syslog"] = await self._get_linux_syslog()
                logs["dmesg"] = await self._get_linux_dmesg()
            
            elif self.system == "Darwin":  # macOS
                # macOS system logs
                logs["system"] = await self._get_macos_system_logs()
            
        except Exception as e:
            logger.error(f"Error collecting system logs: {e}")
            logs["error"] = str(e)
        
        return logs
    
    async def _get_windows_system_logs(self) -> List[Dict[str, Any]]:
        """Get recent Windows system logs"""
        try:
            # Use PowerShell to get recent system logs
            cmd = "powershell -Command \"Get-EventLog -LogName System -Newest 20 | Select-Object TimeGenerated, EntryType, Source, Message | ConvertTo-Json\""
            
            # Execute command
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                try:
                    logs = json.loads(stdout.decode())
                    # Ensure it's a list
                    if not isinstance(logs, list):
                        logs = [logs]
                    return logs
                except json.JSONDecodeError:
                    return [{"error": "Failed to parse Windows system logs"}]
            else:
                return [{"error": stderr.decode()}]
                
        except Exception as e:
            logger.error(f"Error getting Windows system logs: {e}")
            return [{"error": str(e)}]
    
    async def _get_windows_application_logs(self) -> List[Dict[str, Any]]:
        """Get recent Windows application logs"""
        try:
            # Use PowerShell to get recent application logs
            cmd = "powershell -Command \"Get-EventLog -LogName Application -Newest 20 | Select-Object TimeGenerated, EntryType, Source, Message | ConvertTo-Json\""
            
            # Execute command
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                try:
                    logs = json.loads(stdout.decode())
                    # Ensure it's a list
                    if not isinstance(logs, list):
                        logs = [logs]
                    return logs
                except json.JSONDecodeError:
                    return [{"error": "Failed to parse Windows application logs"}]
            else:
                return [{"error": stderr.decode()}]
                
        except Exception as e:
            logger.error(f"Error getting Windows application logs: {e}")
            return [{"error": str(e)}]
    
    async def _get_linux_syslog(self) -> List[str]:
        """Get recent Linux syslog entries"""
        try:
            # Use tail to get recent syslog entries
            cmd = "tail -n 50 /var/log/syslog 2>/dev/null || tail -n 50 /var/log/messages 2>/dev/null"
            
            # Execute command
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                return stdout.decode().splitlines()
            else:
                return [f"Error: {stderr.decode()}"]
                
        except Exception as e:
            logger.error(f"Error getting Linux syslog: {e}")
            return [f"Error: {str(e)}"]
    
    async def _get_linux_dmesg(self) -> List[str]:
        """Get recent Linux kernel messages"""
        try:
            # Use dmesg to get kernel messages
            cmd = "dmesg | tail -n 50"
            
            # Execute command
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                return stdout.decode().splitlines()
            else:
                return [f"Error: {stderr.decode()}"]
                
        except Exception as e:
            logger.error(f"Error getting Linux dmesg: {e}")
            return [f"Error: {str(e)}"]
    
    async def _get_macos_system_logs(self) -> List[str]:
        """Get recent macOS system logs"""
        try:
            # Use log command to get recent system logs
            cmd = "log show --last 1h --predicate 'eventMessage contains \"error\" or eventMessage contains \"warning\"' --style compact --no-debug"
            
            # Execute command
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                # Limit to last 50 lines to avoid excessive data
                return stdout.decode().splitlines()[-50:]
            else:
                return [f"Error: {stderr.decode()}"]
                
        except Exception as e:
            logger.error(f"Error getting macOS system logs: {e}")
            return [f"Error: {str(e)}"]
    
    def analyze_performance_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze collected performance data to identify potential issues
        """
        analysis = {
            "issues_detected": [],
            "performance_summary": {},
            "recommendations": []
        }
        
        try:
            # Check CPU usage
            final_metrics = data.get("final_metrics", {})
            cpu_percent = final_metrics.get("cpu", {}).get("percent", 0)
            
            if cpu_percent > 90:
                analysis["issues_detected"].append("Critical CPU usage detected")
                analysis["recommendations"].append("Check for CPU-intensive processes and consider closing unnecessary applications")
            elif cpu_percent > 70:
                analysis["issues_detected"].append("High CPU usage detected")
                analysis["recommendations"].append("Monitor CPU usage and close unused applications")
            
            # Check memory usage
            memory_percent = final_metrics.get("memory", {}).get("percent", 0)
            
            if memory_percent > 90:
                analysis["issues_detected"].append("Critical memory usage detected")
                analysis["recommendations"].append("Close memory-intensive applications and consider increasing RAM")
            elif memory_percent > 80:
                analysis["issues_detected"].append("High memory usage detected")
                analysis["recommendations"].append("Consider closing unused applications to free up memory")
            
            # Check disk space
            system_info = data.get("system_info", {})
            disk_info = system_info.get("disk", [])
            
            for disk in disk_info:
                if disk.get("percent_used", 0) > 90:
                    analysis["issues_detected"].append(f"Critical disk space usage on {disk.get('mountpoint', 'unknown drive')}")
                    analysis["recommendations"].append("Free up disk space by removing unnecessary files")
            
            # Check for high CPU processes
            top_processes = final_metrics.get("top_processes", [])
            high_cpu_processes = [p for p in top_processes if p.get("cpu_percent", 0) > 50]
            
            if high_cpu_processes:
                process_names = [p.get("name", "unknown") for p in high_cpu_processes[:3]]
                analysis["issues_detected"].append(f"High CPU usage by processes: {', '.join(process_names)}")
            
            # Performance summary
            analysis["performance_summary"] = {
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory_percent}%",
                "top_process": top_processes[0].get("name", "unknown") if top_processes else "None"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance data: {e}")
            analysis["error"] = str(e)
        
        return analysis

# Create singleton instance
device_logs_collector = DeviceLogsCollector()

def get_device_logs_collector() -> DeviceLogsCollector:
    """Get the device logs collector instance"""
    return device_logs_collector
