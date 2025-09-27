"""
Advanced System Diagnostics Service for SmartFix-AI
Provides comprehensive OS-level system monitoring and troubleshooting
"""

import asyncio
import platform
import psutil
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import os
import subprocess

from .automation_service import AutomationService

logger = logging.getLogger(__name__)

class SystemDiagnosticsService:
    """
    Comprehensive system diagnostics and performance monitoring service
    """
    
    def __init__(self):
        self.automation_service = AutomationService()
        self.system = platform.system()
        self.system_info = self._get_basic_system_info()
        
        # Performance thresholds
        self.thresholds = {
            "cpu_usage_critical": 90,
            "cpu_usage_warning": 70,
            "memory_usage_critical": 90,
            "memory_usage_warning": 80,
            "disk_usage_critical": 95,
            "disk_usage_warning": 85,
            "temperature_critical": 85,
            "temperature_warning": 75
        }
    
    def _get_basic_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
        try:
            return {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "architecture": platform.architecture(),
                "hostname": platform.node(),
                "python_version": platform.python_version()
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    async def comprehensive_system_diagnostic(self) -> Dict[str, Any]:
        """
        Run a comprehensive system diagnostic
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self.system_info,
            "diagnostics": {},
            "performance_summary": {},
            "health_score": 0,
            "recommendations": []
        }
        
        try:
            logger.info("Running comprehensive system diagnostic...")
            
            # CPU Diagnostics
            logger.info("Analyzing CPU performance...")
            results["diagnostics"]["cpu"] = await self._diagnose_cpu()
            
            # Memory Diagnostics
            logger.info("Analyzing memory usage...")
            results["diagnostics"]["memory"] = await self._diagnose_memory()
            
            # Disk Diagnostics
            logger.info("Analyzing disk usage...")
            results["diagnostics"]["disk"] = await self._diagnose_disk()
            
            # Process Diagnostics
            logger.info("Analyzing running processes...")
            results["diagnostics"]["processes"] = await self._diagnose_processes()
            
            # System Services
            logger.info("Checking system services...")
            results["diagnostics"]["services"] = await self._diagnose_services()
            
            # Hardware Information
            logger.info("Gathering hardware information...")
            results["diagnostics"]["hardware"] = await self._diagnose_hardware()
            
            # System Performance Metrics
            logger.info("Collecting performance metrics...")
            results["diagnostics"]["performance"] = await self._collect_performance_metrics()
            
            # Generate summary and health score
            results["performance_summary"] = self._generate_performance_summary(results["diagnostics"])
            results["health_score"] = self._calculate_health_score(results["diagnostics"])
            results["recommendations"] = self._generate_system_recommendations(results["diagnostics"])
            
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive system diagnostic: {e}")
            results["error"] = str(e)
            return results
    
    async def _diagnose_cpu(self) -> Dict[str, Any]:
        """Diagnose CPU performance and usage"""
        cpu_info = {
            "status": "analyzing",
            "usage": {},
            "details": {},
            "issues": []
        }
        
        try:
            # Current CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_info["usage"]["current"] = cpu_percent
            
            # Per-core CPU usage
            cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
            cpu_info["usage"]["per_core"] = cpu_per_core
            
            # CPU count and frequency
            cpu_info["details"]["logical_cores"] = psutil.cpu_count(logical=True)
            cpu_info["details"]["physical_cores"] = psutil.cpu_count(logical=False)
            
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    cpu_info["details"]["frequency"] = {
                        "current": cpu_freq.current,
                        "min": cpu_freq.min,
                        "max": cpu_freq.max
                    }
            except Exception:
                cpu_info["details"]["frequency"] = "unavailable"
            
            # CPU times
            cpu_times = psutil.cpu_times()
            cpu_info["details"]["times"] = {
                "user": cpu_times.user,
                "system": cpu_times.system,
                "idle": cpu_times.idle
            }
            
            # Load average (Unix systems)
            if hasattr(os, 'getloadavg'):
                load_avg = os.getloadavg()
                cpu_info["details"]["load_average"] = {
                    "1min": load_avg[0],
                    "5min": load_avg[1],
                    "15min": load_avg[2]
                }
            
            # Analyze CPU issues
            if cpu_percent > self.thresholds["cpu_usage_critical"]:
                cpu_info["issues"].append(f"Critical CPU usage: {cpu_percent:.1f}%")
            elif cpu_percent > self.thresholds["cpu_usage_warning"]:
                cpu_info["issues"].append(f"High CPU usage: {cpu_percent:.1f}%")
            
            # Check for unbalanced core usage
            if cpu_per_core:
                max_core = max(cpu_per_core)
                min_core = min(cpu_per_core)
                if max_core - min_core > 50:
                    cpu_info["issues"].append("Unbalanced CPU core usage detected")
            
            cpu_info["status"] = "completed"
            
        except Exception as e:
            cpu_info["error"] = str(e)
            cpu_info["status"] = "error"
        
        return cpu_info
    
    async def _diagnose_memory(self) -> Dict[str, Any]:
        """Diagnose memory usage and performance"""
        memory_info = {
            "status": "analyzing",
            "usage": {},
            "details": {},
            "issues": []
        }
        
        try:
            # Virtual memory
            virtual_mem = psutil.virtual_memory()
            memory_info["usage"]["virtual"] = {
                "total": virtual_mem.total,
                "available": virtual_mem.available,
                "used": virtual_mem.used,
                "percentage": virtual_mem.percent,
                "free": virtual_mem.free
            }
            
            # Swap memory
            swap_mem = psutil.swap_memory()
            memory_info["usage"]["swap"] = {
                "total": swap_mem.total,
                "used": swap_mem.used,
                "free": swap_mem.free,
                "percentage": swap_mem.percent
            }
            
            # Memory details
            memory_info["details"]["total_gb"] = virtual_mem.total / (1024**3)
            memory_info["details"]["available_gb"] = virtual_mem.available / (1024**3)
            memory_info["details"]["used_gb"] = virtual_mem.used / (1024**3)
            
            # Analyze memory issues
            if virtual_mem.percent > self.thresholds["memory_usage_critical"]:
                memory_info["issues"].append(f"Critical memory usage: {virtual_mem.percent:.1f}%")
            elif virtual_mem.percent > self.thresholds["memory_usage_warning"]:
                memory_info["issues"].append(f"High memory usage: {virtual_mem.percent:.1f}%")
            
            if swap_mem.percent > 50:
                memory_info["issues"].append(f"High swap usage: {swap_mem.percent:.1f}%")
            
            if virtual_mem.available < (1024**3):  # Less than 1GB available
                memory_info["issues"].append("Low available memory (< 1GB)")
            
            memory_info["status"] = "completed"
            
        except Exception as e:
            memory_info["error"] = str(e)
            memory_info["status"] = "error"
        
        return memory_info
    
    async def _diagnose_disk(self) -> Dict[str, Any]:
        """Diagnose disk usage and performance"""
        disk_info = {
            "status": "analyzing",
            "usage": {},
            "partitions": {},
            "io_stats": {},
            "issues": []
        }
        
        try:
            # Disk partitions
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    disk_info["partitions"][partition.device] = {
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype,
                        "total": partition_usage.total,
                        "used": partition_usage.used,
                        "free": partition_usage.free,
                        "percentage": (partition_usage.used / partition_usage.total) * 100
                    }
                    
                    # Check for disk space issues
                    usage_percent = (partition_usage.used / partition_usage.total) * 100
                    if usage_percent > self.thresholds["disk_usage_critical"]:
                        disk_info["issues"].append(f"Critical disk usage on {partition.device}: {usage_percent:.1f}%")
                    elif usage_percent > self.thresholds["disk_usage_warning"]:
                        disk_info["issues"].append(f"High disk usage on {partition.device}: {usage_percent:.1f}%")
                    
                except PermissionError:
                    disk_info["partitions"][partition.device] = {
                        "error": "Permission denied"
                    }
            
            # Disk I/O statistics
            try:
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    disk_info["io_stats"] = {
                        "read_count": disk_io.read_count,
                        "write_count": disk_io.write_count,
                        "read_bytes": disk_io.read_bytes,
                        "write_bytes": disk_io.write_bytes,
                        "read_time": disk_io.read_time,
                        "write_time": disk_io.write_time
                    }
            except Exception:
                disk_info["io_stats"] = {"error": "I/O stats unavailable"}
            
            disk_info["status"] = "completed"
            
        except Exception as e:
            disk_info["error"] = str(e)
            disk_info["status"] = "error"
        
        return disk_info
    
    async def _diagnose_processes(self) -> Dict[str, Any]:
        """Diagnose running processes and resource usage"""
        process_info = {
            "status": "analyzing",
            "summary": {},
            "top_cpu": [],
            "top_memory": [],
            "suspicious": [],
            "issues": []
        }
        
        try:
            processes = []
            
            # Collect process information
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Summary statistics
            process_info["summary"]["total_processes"] = len(processes)
            process_info["summary"]["running_processes"] = len([p for p in processes if p['cpu_percent'] > 0])
            
            # Top CPU consuming processes
            cpu_sorted = sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)
            process_info["top_cpu"] = cpu_sorted[:10]
            
            # Top memory consuming processes
            memory_sorted = sorted(processes, key=lambda x: x['memory_percent'] or 0, reverse=True)
            process_info["top_memory"] = memory_sorted[:10]
            
            # Look for suspicious processes
            for proc in processes:
                if proc['cpu_percent'] and proc['cpu_percent'] > 80:
                    process_info["suspicious"].append({
                        "pid": proc['pid'],
                        "name": proc['name'],
                        "reason": f"High CPU usage: {proc['cpu_percent']:.1f}%"
                    })
                
                if proc['memory_percent'] and proc['memory_percent'] > 20:
                    process_info["suspicious"].append({
                        "pid": proc['pid'],
                        "name": proc['name'],
                        "reason": f"High memory usage: {proc['memory_percent']:.1f}%"
                    })
            
            # Identify potential issues
            if len(process_info["suspicious"]) > 0:
                process_info["issues"].append(f"Found {len(process_info['suspicious'])} suspicious processes")
            
            if process_info["summary"]["total_processes"] > 300:
                process_info["issues"].append("High number of running processes")
            
            process_info["status"] = "completed"
            
        except Exception as e:
            process_info["error"] = str(e)
            process_info["status"] = "error"
        
        return process_info
    
    async def _diagnose_services(self) -> Dict[str, Any]:
        """Diagnose system services and startup programs"""
        service_info = {
            "status": "analyzing",
            "services": {},
            "startup_programs": [],
            "issues": []
        }
        
        try:
            # Get system services (Windows)
            if self.system == "Windows":
                result = await self.automation_service.execute_command("sc query state= all")
                if result["success"]:
                    service_info["services"] = self._parse_windows_services(result["stdout"])
            
            # Get system services (Linux/Mac)
            elif self.system in ["Linux", "Darwin"]:
                # Try systemctl for Linux
                result = await self.automation_service.execute_command("systemctl list-units --type=service --state=running")
                if result["success"]:
                    service_info["services"] = self._parse_linux_services(result["stdout"])
            
            # Get startup programs
            startup_programs = self._get_startup_programs()
            service_info["startup_programs"] = startup_programs
            
            # Analyze service issues
            if len(startup_programs) > 20:
                service_info["issues"].append("High number of startup programs may slow boot time")
            
            service_info["status"] = "completed"
            
        except Exception as e:
            service_info["error"] = str(e)
            service_info["status"] = "error"
        
        return service_info
    
    async def _diagnose_hardware(self) -> Dict[str, Any]:
        """Diagnose hardware information and health"""
        hardware_info = {
            "status": "analyzing",
            "cpu": {},
            "memory": {},
            "storage": {},
            "network": {},
            "sensors": {},
            "issues": []
        }
        
        try:
            # CPU hardware info
            hardware_info["cpu"] = {
                "brand": platform.processor(),
                "architecture": platform.machine(),
                "cores": {
                    "physical": psutil.cpu_count(logical=False),
                    "logical": psutil.cpu_count(logical=True)
                }
            }
            
            # Memory hardware info
            virtual_mem = psutil.virtual_memory()
            hardware_info["memory"] = {
                "total_gb": round(virtual_mem.total / (1024**3), 2),
                "type": "Unknown"  # Would need additional tools to detect DDR type
            }
            
            # Storage hardware info
            hardware_info["storage"] = {
                "devices": []
            }
            
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    hardware_info["storage"]["devices"].append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype,
                        "size_gb": round(usage.total / (1024**3), 2)
                    })
                except:
                    continue
            
            # Network hardware info
            network_interfaces = psutil.net_if_addrs()
            hardware_info["network"] = {
                "interfaces": list(network_interfaces.keys()),
                "active_interfaces": []
            }
            
            for interface, addresses in network_interfaces.items():
                for addr in addresses:
                    if addr.family == 2:  # IPv4
                        hardware_info["network"]["active_interfaces"].append({
                            "interface": interface,
                            "ip": addr.address
                        })
            
            # Sensor information (temperature, fans, etc.)
            try:
                sensors = psutil.sensors_temperatures()
                if sensors:
                    hardware_info["sensors"]["temperatures"] = {}
                    for sensor_name, sensor_list in sensors.items():
                        temps = []
                        for sensor in sensor_list:
                            temps.append({
                                "label": sensor.label or "Unknown",
                                "current": sensor.current,
                                "high": sensor.high,
                                "critical": sensor.critical
                            })
                            
                            # Check for temperature issues
                            if sensor.current and sensor.current > self.thresholds["temperature_critical"]:
                                hardware_info["issues"].append(f"Critical temperature: {sensor.label} at {sensor.current}°C")
                            elif sensor.current and sensor.current > self.thresholds["temperature_warning"]:
                                hardware_info["issues"].append(f"High temperature: {sensor.label} at {sensor.current}°C")
                        
                        hardware_info["sensors"]["temperatures"][sensor_name] = temps
            except:
                hardware_info["sensors"]["temperatures"] = "unavailable"
            
            # Fan information
            try:
                fans = psutil.sensors_fans()
                if fans:
                    hardware_info["sensors"]["fans"] = {}
                    for fan_name, fan_list in fans.items():
                        fan_info = []
                        for fan in fan_list:
                            fan_info.append({
                                "label": fan.label or "Unknown",
                                "current": fan.current
                            })
                        hardware_info["sensors"]["fans"][fan_name] = fan_info
            except:
                hardware_info["sensors"]["fans"] = "unavailable"
            
            hardware_info["status"] = "completed"
            
        except Exception as e:
            hardware_info["error"] = str(e)
            hardware_info["status"] = "error"
        
        return hardware_info
    
    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect real-time performance metrics"""
        metrics = {
            "status": "collecting",
            "timestamp": datetime.now().isoformat(),
            "cpu": {},
            "memory": {},
            "disk": {},
            "network": {}
        }
        
        try:
            # CPU metrics over time
            cpu_samples = []
            for _ in range(5):
                cpu_samples.append(psutil.cpu_percent(interval=0.2))
            
            metrics["cpu"] = {
                "average": sum(cpu_samples) / len(cpu_samples),
                "peak": max(cpu_samples),
                "samples": cpu_samples
            }
            
            # Memory metrics
            mem = psutil.virtual_memory()
            metrics["memory"] = {
                "usage_percent": mem.percent,
                "available_gb": round(mem.available / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2)
            }
            
            # Disk I/O metrics
            disk_io_start = psutil.disk_io_counters()
            await asyncio.sleep(1)
            disk_io_end = psutil.disk_io_counters()
            
            if disk_io_start and disk_io_end:
                metrics["disk"] = {
                    "read_bytes_per_sec": disk_io_end.read_bytes - disk_io_start.read_bytes,
                    "write_bytes_per_sec": disk_io_end.write_bytes - disk_io_start.write_bytes,
                    "read_ops_per_sec": disk_io_end.read_count - disk_io_start.read_count,
                    "write_ops_per_sec": disk_io_end.write_count - disk_io_start.write_count
                }
            
            # Network I/O metrics
            net_io_start = psutil.net_io_counters()
            await asyncio.sleep(1)
            net_io_end = psutil.net_io_counters()
            
            if net_io_start and net_io_end:
                metrics["network"] = {
                    "bytes_sent_per_sec": net_io_end.bytes_sent - net_io_start.bytes_sent,
                    "bytes_recv_per_sec": net_io_end.bytes_recv - net_io_start.bytes_recv,
                    "packets_sent_per_sec": net_io_end.packets_sent - net_io_start.packets_sent,
                    "packets_recv_per_sec": net_io_end.packets_recv - net_io_start.packets_recv
                }
            
            metrics["status"] = "completed"
            
        except Exception as e:
            metrics["error"] = str(e)
            metrics["status"] = "error"
        
        return metrics
    
    def _parse_windows_services(self, output: str) -> Dict[str, Any]:
        """Parse Windows services output"""
        services = {"running": [], "stopped": []}
        
        try:
            lines = output.split('\n')
            current_service = {}
            
            for line in lines:
                line = line.strip()
                
                if "SERVICE_NAME:" in line:
                    if current_service:
                        # Add previous service
                        status = current_service.get("state", "").lower()
                        if "running" in status:
                            services["running"].append(current_service["name"])
                        else:
                            services["stopped"].append(current_service["name"])
                    
                    current_service = {"name": line.split(":", 1)[1].strip()}
                
                elif "STATE" in line and current_service:
                    current_service["state"] = line.split(":", 1)[1].strip()
                    
        except Exception as e:
            logger.error(f"Error parsing Windows services: {e}")
        
        return services
    
    def _parse_linux_services(self, output: str) -> Dict[str, Any]:
        """Parse Linux systemctl services output"""
        services = {"running": [], "stopped": []}
        
        try:
            lines = output.split('\n')
            
            for line in lines:
                if ".service" in line and "running" in line:
                    parts = line.split()
                    if parts:
                        service_name = parts[0].replace(".service", "")
                        services["running"].append(service_name)
                        
        except Exception as e:
            logger.error(f"Error parsing Linux services: {e}")
        
        return services
    
    def _get_startup_programs(self) -> List[Dict[str, Any]]:
        """Get list of startup programs"""
        startup_programs = []
        
        try:
            if self.system == "Windows":
                # Windows startup programs (simplified)
                startup_programs.append({
                    "name": "Windows Startup Check",
                    "status": "Use 'msconfig' or Task Manager to view startup programs"
                })
            
            elif self.system == "Linux":
                # Linux autostart programs
                autostart_dirs = [
                    "/etc/xdg/autostart/",
                    os.path.expanduser("~/.config/autostart/")
                ]
                
                for directory in autostart_dirs:
                    if os.path.exists(directory):
                        for filename in os.listdir(directory):
                            if filename.endswith(".desktop"):
                                startup_programs.append({
                                    "name": filename.replace(".desktop", ""),
                                    "location": directory
                                })
                                
        except Exception as e:
            logger.error(f"Error getting startup programs: {e}")
        
        return startup_programs
    
    def _generate_performance_summary(self, diagnostics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance summary from diagnostics"""
        summary = {
            "overall_status": "unknown",
            "critical_issues": 0,
            "warnings": 0,
            "key_metrics": {},
            "bottlenecks": []
        }
        
        try:
            # Count issues
            for category, data in diagnostics.items():
                if isinstance(data, dict) and "issues" in data:
                    for issue in data["issues"]:
                        if "critical" in issue.lower():
                            summary["critical_issues"] += 1
                        else:
                            summary["warnings"] += 1
            
            # Key metrics
            if "cpu" in diagnostics and "usage" in diagnostics["cpu"]:
                summary["key_metrics"]["cpu_usage"] = diagnostics["cpu"]["usage"].get("current", 0)
            
            if "memory" in diagnostics and "usage" in diagnostics["memory"]:
                summary["key_metrics"]["memory_usage"] = diagnostics["memory"]["usage"]["virtual"].get("percentage", 0)
            
            # Identify bottlenecks
            if summary["key_metrics"].get("cpu_usage", 0) > 80:
                summary["bottlenecks"].append("CPU")
            
            if summary["key_metrics"].get("memory_usage", 0) > 80:
                summary["bottlenecks"].append("Memory")
            
            # Determine overall status
            if summary["critical_issues"] > 0:
                summary["overall_status"] = "critical"
            elif summary["warnings"] > 3:
                summary["overall_status"] = "warning"
            elif summary["warnings"] > 0:
                summary["overall_status"] = "good"
            else:
                summary["overall_status"] = "excellent"
                
        except Exception as e:
            logger.error(f"Error generating performance summary: {e}")
        
        return summary
    
    def _calculate_health_score(self, diagnostics: Dict[str, Any]) -> int:
        """Calculate overall system health score (0-100)"""
        score = 100
        
        try:
            # CPU score
            if "cpu" in diagnostics and "usage" in diagnostics["cpu"]:
                cpu_usage = diagnostics["cpu"]["usage"].get("current", 0)
                if cpu_usage > 90:
                    score -= 30
                elif cpu_usage > 70:
                    score -= 15
                elif cpu_usage > 50:
                    score -= 5
            
            # Memory score
            if "memory" in diagnostics and "usage" in diagnostics["memory"]:
                mem_usage = diagnostics["memory"]["usage"]["virtual"].get("percentage", 0)
                if mem_usage > 90:
                    score -= 25
                elif mem_usage > 80:
                    score -= 15
                elif mem_usage > 70:
                    score -= 10
            
            # Disk score
            if "disk" in diagnostics and "partitions" in diagnostics["disk"]:
                for partition_info in diagnostics["disk"]["partitions"].values():
                    if isinstance(partition_info, dict) and "percentage" in partition_info:
                        disk_usage = partition_info["percentage"]
                        if disk_usage > 95:
                            score -= 20
                        elif disk_usage > 85:
                            score -= 10
            
            # Process score
            if "processes" in diagnostics and "suspicious" in diagnostics["processes"]:
                suspicious_count = len(diagnostics["processes"]["suspicious"])
                score -= min(suspicious_count * 5, 20)
            
            # Hardware issues
            if "hardware" in diagnostics and "issues" in diagnostics["hardware"]:
                issue_count = len(diagnostics["hardware"]["issues"])
                score -= min(issue_count * 10, 30)
                
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            score = 50  # Default to medium score on error
        
        return max(0, min(100, score))
    
    def _generate_system_recommendations(self, diagnostics: Dict[str, Any]) -> List[str]:
        """Generate system optimization recommendations"""
        recommendations = []
        
        try:
            # CPU recommendations
            if "cpu" in diagnostics and "issues" in diagnostics["cpu"]:
                for issue in diagnostics["cpu"]["issues"]:
                    if "high cpu" in issue.lower():
                        recommendations.append("Close unnecessary programs to reduce CPU usage")
                        recommendations.append("Check Task Manager for high CPU processes")
            
            # Memory recommendations
            if "memory" in diagnostics and "issues" in diagnostics["memory"]:
                for issue in diagnostics["memory"]["issues"]:
                    if "memory usage" in issue.lower():
                        recommendations.append("Close memory-heavy applications")
                        recommendations.append("Consider adding more RAM if usage is consistently high")
                    if "swap usage" in issue.lower():
                        recommendations.append("Reduce memory usage to avoid slow swap file access")
            
            # Disk recommendations
            if "disk" in diagnostics and "issues" in diagnostics["disk"]:
                for issue in diagnostics["disk"]["issues"]:
                    if "disk usage" in issue.lower():
                        recommendations.append("Free up disk space by deleting unnecessary files")
                        recommendations.append("Use disk cleanup tools to remove temporary files")
            
            # Process recommendations
            if "processes" in diagnostics and "suspicious" in diagnostics["processes"]:
                if diagnostics["processes"]["suspicious"]:
                    recommendations.append("Review high resource usage processes")
                    recommendations.append("Consider ending unnecessary background processes")
            
            # Hardware recommendations
            if "hardware" in diagnostics and "issues" in diagnostics["hardware"]:
                for issue in diagnostics["hardware"]["issues"]:
                    if "temperature" in issue.lower():
                        recommendations.append("Check system cooling - clean fans and vents")
                        recommendations.append("Monitor system temperature to prevent overheating")
            
            # Default recommendations
            if not recommendations:
                recommendations.extend([
                    "System appears healthy - continue regular maintenance",
                    "Keep software updated for optimal performance",
                    "Run regular disk cleanup and defragmentation"
                ])
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("Unable to generate specific recommendations")
        
        return recommendations[:8]  # Limit to 8 recommendations

# Create singleton instance
system_diagnostics = SystemDiagnosticsService()

def get_system_diagnostics() -> SystemDiagnosticsService:
    """Get the system diagnostics service instance"""
    return system_diagnostics
