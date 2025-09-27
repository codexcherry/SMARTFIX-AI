import platform
import psutil
import os
import subprocess
import json
import logging
import socket
import uuid
import re
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import threading
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeviceDetectorService:
    """
    Automated Device Detection and Analysis Service
    Performs comprehensive system health checks and generates detailed reports
    """
    
    def __init__(self):
        self.system_info = {}
        self.health_metrics = {}
        self.detected_issues = []
        self.recommendations = []
        self.hardware_info = {}
        self.network_info = {}
        self.security_info = {}
        self.benchmark_results = {}
        
    async def perform_full_system_analysis(self) -> Dict[str, Any]:
        """
        Perform comprehensive system analysis and generate health report
        """
        try:
            logger.info("Starting comprehensive system analysis...")
            
            # Collect system information
            self._collect_system_info()
            
            # Collect hardware information
            self._collect_hardware_info()
            
            # Collect network information
            self._collect_network_info()
            
            # Collect security information
            self._collect_security_info()
            
            # Perform health checks
            await self._perform_health_checks()
            
            # Run benchmarks
            await self._run_benchmarks()
            
            # Detect issues
            self._detect_system_issues()
            
            # Generate recommendations
            self._generate_recommendations()
            
            # Create comprehensive report
            report = self._generate_analysis_report()
            
            logger.info("System analysis completed successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error during system analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _collect_system_info(self):
        """Collect basic system information"""
        try:
            self.system_info = {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "hostname": platform.node(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "memory_total": psutil.virtual_memory().total,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "analysis_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error collecting system info: {e}")
    
    def _collect_hardware_info(self):
        """Collect detailed hardware information"""
        try:
            # GPU Information (if available)
            gpu_info = []
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    gpu_info.append({
                        "id": gpu.id,
                        "name": gpu.name,
                        "driver": gpu.driver,
                        "memory_total": gpu.memoryTotal,
                        "memory_free": gpu.memoryFree,
                        "memory_used": gpu.memoryUsed,
                        "temperature": gpu.temperature,
                        "uuid": gpu.uuid
                    })
            except Exception as e:
                logger.debug(f"Could not get GPU info: {e}")
            
            # Disk Information
            disk_info = []
            try:
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disk_info.append({
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total_size": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent_used": usage.percent
                        })
                    except:
                        continue
            except Exception as e:
                logger.debug(f"Could not get disk info: {e}")
            
            # Battery Information
            battery_info = {}
            try:
                battery = psutil.sensors_battery()
                if battery:
                    battery_info = {
                        "percent": battery.percent,
                        "power_plugged": battery.power_plugged,
                        "secsleft": battery.secsleft
                    }
            except Exception as e:
                logger.debug(f"Could not get battery info: {e}")
            
            self.hardware_info = {
                "gpus": gpu_info,
                "disks": disk_info,
                "battery": battery_info
            }
        except Exception as e:
            logger.error(f"Error collecting hardware info: {e}")
    
    def _collect_network_info(self):
        """Collect network information"""
        try:
            # Network interfaces
            interfaces = []
            for interface_name, interface_addresses in psutil.net_if_addrs().items():
                interface_info = {"name": interface_name, "addresses": []}
                for address in interface_addresses:
                    interface_info["addresses"].append({
                        "family": address.family.name,
                        "address": address.address,
                        "netmask": address.netmask,
                        "broadcast": address.broadcast
                    })
                interfaces.append(interface_info)
            
            # Network stats
            net_io = psutil.net_io_counters()
            network_stats = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin,
                "errout": net_io.errout,
                "dropin": net_io.dropin,
                "dropout": net_io.dropout
            }
            
            self.network_info = {
                "interfaces": interfaces,
                "stats": network_stats,
                "hostname": socket.gethostname(),
                "fqdn": socket.getfqdn(),
                "ip_address": socket.gethostbyname(socket.gethostname())
            }
        except Exception as e:
            logger.error(f"Error collecting network info: {e}")
    
    def _collect_security_info(self):
        """Collect security-related information"""
        try:
            # Firewall status (platform-specific)
            firewall_status = "unknown"
            if platform.system() == "Windows":
                try:
                    result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles', 'state'], 
                                          capture_output=True, text=True)
                    if "ON" in result.stdout:
                        firewall_status = "enabled"
                    elif "OFF" in result.stdout:
                        firewall_status = "disabled"
                except:
                    pass
            
            # Check for open ports
            open_ports = []
            try:
                # Check common ports
                common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080]
                for port in common_ports:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.1)
                    result = sock.connect_ex(('127.0.0.1', port))
                    if result == 0:
                        open_ports.append(port)
                    sock.close()
            except:
                pass
            
            self.security_info = {
                "firewall_status": firewall_status,
                "open_ports": open_ports
            }
        except Exception as e:
            logger.error(f"Error collecting security info: {e}")
    
    async def _run_benchmarks(self):
        """Run system benchmarks"""
        try:
            # CPU Benchmark
            cpu_score = await self._run_cpu_benchmark()
            
            # Disk Benchmark
            disk_score = await self._run_disk_benchmark()
            
            # Memory Benchmark
            memory_score = await self._run_memory_benchmark()
            
            self.benchmark_results = {
                "cpu_score": cpu_score,
                "disk_score": disk_score,
                "memory_score": memory_score,
                "overall_score": round((cpu_score + disk_score + memory_score) / 3, 2)
            }
        except Exception as e:
            logger.error(f"Error running benchmarks: {e}")
    
    async def _run_cpu_benchmark(self) -> float:
        """Run a simple CPU benchmark"""
        try:
            start_time = time.time()
            
            # Perform some CPU-intensive calculations
            def calculate_primes(n):
                primes = []
                for num in range(2, n):
                    is_prime = True
                    for i in range(2, int(num**0.5) + 1):
                        if num % i == 0:
                            is_prime = False
                            break
                    if is_prime:
                        primes.append(num)
                return primes
            
            # Run the calculation
            await asyncio.get_event_loop().run_in_executor(None, calculate_primes, 5000)
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            # Score based on time (lower is better)
            score = max(0, min(100, 100 - (elapsed * 10)))
            return round(score, 2)
        except:
            return 0
    
    async def _run_disk_benchmark(self) -> float:
        """Run a simple disk benchmark"""
        try:
            test_file = "disk_benchmark_test.tmp"
            test_data = os.urandom(1024 * 1024)  # 1MB of random data
            
            # Write test
            start_time = time.time()
            with open(test_file, 'wb') as f:
                for _ in range(5):  # Write 5MB total
                    f.write(test_data)
            write_time = time.time() - start_time
            
            # Read test
            start_time = time.time()
            with open(test_file, 'rb') as f:
                while f.read(1024 * 1024):  # Read in 1MB chunks
                    pass
            read_time = time.time() - start_time
            
            # Clean up
            try:
                os.remove(test_file)
            except:
                pass
            
            # Calculate scores (higher write/read speed is better)
            write_speed = 5 / write_time  # MB/s
            read_speed = 5 / read_time    # MB/s
            
            # Normalize to 0-100 scale
            score = min(100, (write_speed + read_speed) / 2)
            return round(score, 2)
        except:
            return 0
    
    async def _run_memory_benchmark(self) -> float:
        """Run a simple memory benchmark"""
        try:
            start_time = time.time()
            
            # Perform memory-intensive operations
            def memory_operations():
                # Create a large list and perform operations
                large_list = list(range(500000))
                # Various operations
                _ = [x * 2 for x in large_list]
                _ = sorted(large_list)
                _ = sum(large_list)
            
            # Run the operations
            await asyncio.get_event_loop().run_in_executor(None, memory_operations)
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            # Score based on time (lower is better)
            score = max(0, min(100, 100 - (elapsed * 100)))
            return round(score, 2)
        except:
            return 0
    
    async def _perform_health_checks(self):
        """Perform comprehensive health checks"""
        try:
            # CPU Health Check
            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            
            self.health_metrics["cpu"] = {
                "usage_percent": cpu_usage,
                "frequency_current": cpu_freq.current if cpu_freq else None,
                "frequency_min": cpu_freq.min if cpu_freq else None,
                "frequency_max": cpu_freq.max if cpu_freq else None,
                "temperature": self._get_cpu_temperature(),
                "status": "healthy" if cpu_usage < 80 else "warning" if cpu_usage < 95 else "critical"
            }
            
            # Memory Health Check
            memory = psutil.virtual_memory()
            self.health_metrics["memory"] = {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": memory.percent,
                "status": "healthy" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
            }
            
            # Disk Health Check
            disk_usage = psutil.disk_usage('/')
            self.health_metrics["disk"] = {
                "total_gb": round(disk_usage.total / (1024**3), 2),
                "used_gb": round(disk_usage.used / (1024**3), 2),
                "free_gb": round(disk_usage.free / (1024**3), 2),
                "usage_percent": round((disk_usage.used / disk_usage.total) * 100, 2),
                "status": "healthy" if (disk_usage.used / disk_usage.total) < 0.8 else "warning" if (disk_usage.used / disk_usage.total) < 0.95 else "critical"
            }
            
            # Network Health Check
            network = psutil.net_io_counters()
            self.health_metrics["network"] = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
                "status": "healthy"
            }
            
            # Process Health Check
            processes = self._analyze_processes()
            self.health_metrics["processes"] = processes
            
            # System Load Check
            if hasattr(psutil, 'getloadavg'):
                try:
                    load_avg = psutil.getloadavg()
                    self.health_metrics["system_load"] = {
                        "load_1min": load_avg[0],
                        "load_5min": load_avg[1],
                        "load_15min": load_avg[2],
                        "status": "healthy" if load_avg[0] < psutil.cpu_count() else "warning"
                    }
                except:
                    self.health_metrics["system_load"] = {"status": "unknown"}
            
        except Exception as e:
            logger.error(f"Error performing health checks: {e}")
    
    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature if available"""
        try:
            if platform.system() == "Windows":
                # Windows temperature reading
                try:
                    import wmi
                    w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                    temperature_infos = w.Sensor()
                    for sensor in temperature_infos:
                        if sensor.SensorType == 'Temperature':
                            return float(sensor.Value)
                except:
                    pass
            elif platform.system() == "Linux":
                # Linux temperature reading
                try:
                    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                        temp = float(f.read()) / 1000.0
                        return temp
                except:
                    pass
            elif platform.system() == "Darwin":
                # macOS temperature reading
                try:
                    result = subprocess.run(['sudo', 'powermetrics', '-n', '1', '-i', '1000'], 
                                          capture_output=True, text=True, timeout=5)
                    for line in result.stdout.split('\n'):
                        if 'CPU die temperature' in line:
                            temp = float(line.split()[-1])
                            return temp
                except:
                    pass
        except Exception as e:
            logger.debug(f"Could not read CPU temperature: {e}")
        return None
    
    def _analyze_processes(self) -> Dict[str, Any]:
        """Analyze running processes for potential issues"""
        try:
            processes = []
            high_cpu_processes = []
            high_memory_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 10:  # High CPU usage
                        high_cpu_processes.append({
                            "pid": proc_info['pid'],
                            "name": proc_info['name'],
                            "cpu_percent": proc_info['cpu_percent'],
                            "memory_percent": proc_info['memory_percent']
                        })
                    
                    if proc_info['memory_percent'] > 5:  # High memory usage
                        high_memory_processes.append({
                            "pid": proc_info['pid'],
                            "name": proc_info['name'],
                            "cpu_percent": proc_info['cpu_percent'],
                            "memory_percent": proc_info['memory_percent']
                        })
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                "total_processes": len(list(psutil.process_iter())),
                "high_cpu_processes": sorted(high_cpu_processes, key=lambda x: x['cpu_percent'], reverse=True)[:10],
                "high_memory_processes": sorted(high_memory_processes, key=lambda x: x['memory_percent'], reverse=True)[:10]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing processes: {e}")
            return {"error": str(e)}
    
    def _detect_system_issues(self):
        """Detect system issues based on health metrics"""
        self.detected_issues = []
        
        # CPU Issues
        if self.health_metrics.get("cpu", {}).get("usage_percent", 0) > 90:
            self.detected_issues.append({
                "type": "cpu",
                "severity": "high",
                "description": "High CPU usage detected",
                "details": f"CPU usage is {self.health_metrics['cpu']['usage_percent']}%",
                "impact": "System performance may be degraded"
            })
        
        # Memory Issues
        if self.health_metrics.get("memory", {}).get("usage_percent", 0) > 90:
            self.detected_issues.append({
                "type": "memory",
                "severity": "high",
                "description": "High memory usage detected",
                "details": f"Memory usage is {self.health_metrics['memory']['usage_percent']}%",
                "impact": "System may become unresponsive"
            })
        
        # Disk Issues
        if self.health_metrics.get("disk", {}).get("usage_percent", 0) > 90:
            self.detected_issues.append({
                "type": "disk",
                "severity": "high",
                "description": "Low disk space detected",
                "details": f"Disk usage is {self.health_metrics['disk']['usage_percent']}%",
                "impact": "System may not be able to save files or install updates"
            })
        
        # Process Issues
        high_cpu_procs = self.health_metrics.get("processes", {}).get("high_cpu_processes", [])
        if len(high_cpu_procs) > 0:
            self.detected_issues.append({
                "type": "process",
                "severity": "medium",
                "description": "High CPU consuming processes detected",
                "details": f"{len(high_cpu_procs)} processes using >10% CPU",
                "impact": "System performance may be affected"
            })
    
    def _generate_recommendations(self):
        """Generate recommendations based on detected issues"""
        self.recommendations = []
        
        for issue in self.detected_issues:
            if issue["type"] == "cpu":
                self.recommendations.extend([
                    "Close unnecessary applications to reduce CPU load",
                    "Check for background processes that may be consuming CPU",
                    "Consider upgrading CPU if high usage is persistent",
                    "Monitor CPU temperature to prevent thermal throttling"
                ])
            
            elif issue["type"] == "memory":
                self.recommendations.extend([
                    "Close applications that are not in use",
                    "Check for memory leaks in running applications",
                    "Consider adding more RAM if high usage is persistent",
                    "Restart the system to clear memory cache"
                ])
            
            elif issue["type"] == "disk":
                self.recommendations.extend([
                    "Delete unnecessary files and applications",
                    "Empty the recycle bin/trash",
                    "Clear temporary files and cache",
                    "Consider upgrading to a larger storage drive",
                    "Run disk cleanup utility"
                ])
            
            elif issue["type"] == "process":
                self.recommendations.extend([
                    "Identify and close unnecessary background processes",
                    "Check for malware or unwanted software",
                    "Update applications to latest versions",
                    "Consider using task manager to end problematic processes"
                ])
        
        # General recommendations
        if not self.detected_issues:
            self.recommendations.append("System is running optimally. Continue regular maintenance.")
        
        self.recommendations.append("Run regular system updates to maintain security and performance")
        self.recommendations.append("Consider running a full system scan for malware")
    
    def _generate_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        overall_status = "healthy"
        if any(issue["severity"] == "high" for issue in self.detected_issues):
            overall_status = "critical"
        elif any(issue["severity"] == "medium" for issue in self.detected_issues):
            overall_status = "warning"
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "system_info": self.system_info,
            "hardware_info": self.hardware_info,
            "network_info": self.network_info,
            "security_info": self.security_info,
            "health_metrics": self.health_metrics,
            "benchmark_results": self.benchmark_results,
            "detected_issues": self.detected_issues,
            "recommendations": list(set(self.recommendations)),  # Remove duplicates
            "summary": {
                "total_issues": len(self.detected_issues),
                "critical_issues": len([i for i in self.detected_issues if i["severity"] == "high"]),
                "warning_issues": len([i for i in self.detected_issues if i["severity"] == "medium"]),
                "system_health_score": self._calculate_health_score(),
                "performance_score": self.benchmark_results.get("overall_score", 0)
            }
        }
    
    def _calculate_health_score(self) -> int:
        """Calculate overall system health score (0-100)"""
        score = 100
        
        # Deduct points for issues
        for issue in self.detected_issues:
            if issue["severity"] == "high":
                score -= 20
            elif issue["severity"] == "medium":
                score -= 10
        
        # Ensure score doesn't go below 0
        return max(0, score)
    
    async def get_quick_health_check(self) -> Dict[str, Any]:
        """Perform a quick health check for real-time monitoring"""
        try:
            cpu_usage = psutil.cpu_percent(interval=0.5)
            memory_usage = psutil.virtual_memory().percent
            disk_usage = (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
            
            status = "healthy"
            if cpu_usage > 90 or memory_usage > 90 or disk_usage > 90:
                status = "warning"
            if cpu_usage > 95 or memory_usage > 95 or disk_usage > 95:
                status = "critical"
            
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "metrics": {
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage,
                    "disk_usage": round(disk_usage, 2)
                }
            }
        except Exception as e:
            logger.error(f"Error in quick health check: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Create singleton instance
device_detector = DeviceDetectorService()

def get_device_detector() -> DeviceDetectorService:
    """Get the device detector service instance"""
    return device_detector
