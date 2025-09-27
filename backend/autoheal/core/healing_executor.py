"""
Real Healing Executor for Galaxy Autopilot

Implements actual system healing actions using subprocess, system commands,
and real system operations instead of mock responses.
"""

import asyncio
import logging
import subprocess
import psutil
import os
import signal
import time
import shutil
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import json
import tempfile
import platform

logger = logging.getLogger(__name__)

@dataclass
class HealingResult:
    """Result of a healing action"""
    success: bool
    action_type: str
    target: str
    duration_ms: int
    improvement_score: float
    details: Dict[str, Any]
    error_message: Optional[str] = None

class RealHealingExecutor:
    """
    Real healing executor that performs actual system operations
    """
    
    def __init__(self, device_id: str = "galaxy_device"):
        self.device_id = device_id
        self.is_windows = platform.system() == "Windows"
        self.is_linux = platform.system() == "Linux"
        self.is_macos = platform.system() == "Darwin"
        
        # Track healing actions for learning
        self.healing_history = []
        
        # System-specific commands
        self.system_commands = self._get_system_commands()
    
    def _get_system_commands(self) -> Dict[str, Dict[str, str]]:
        """Get system-specific commands for different operations"""
        commands = {
            "kill_process": {
                "windows": "taskkill /PID {pid} /F",
                "linux": "kill -9 {pid}",
                "macos": "kill -9 {pid}"
            },
            "restart_service": {
                "windows": "net stop {service} && net start {service}",
                "linux": "systemctl restart {service}",
                "macos": "sudo launchctl unload {service} && sudo launchctl load {service}"
            },
            "clear_cache": {
                "windows": "del /q /s %TEMP%\\*",
                "linux": "rm -rf /tmp/* /var/tmp/*",
                "macos": "rm -rf /tmp/* /var/tmp/*"
            },
            "defragment_disk": {
                "windows": "defrag C: /O",
                "linux": "sudo e4defrag /",
                "macos": "sudo diskutil defragmentVolume /"
            },
            "check_disk": {
                "windows": "chkdsk C: /f",
                "linux": "fsck -f /",
                "macos": "sudo diskutil verifyDisk /"
            }
        }
        return commands
    
    async def restart_app(self, package_name: str) -> HealingResult:
        """Restart an application by killing and restarting it"""
        start_time = time.time()
        
        try:
            # Find the process by name
            target_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if package_name.lower() in proc.info['name'].lower():
                        target_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not target_processes:
                return HealingResult(
                    success=False,
                    action_type="restart_app",
                    target=package_name,
                    duration_ms=int((time.time() - start_time) * 1000),
                    improvement_score=0.0,
                    details={"message": "Process not found"},
                    error_message="Process not found"
                )
            
            # Kill the processes
            killed_count = 0
            for proc in target_processes:
                try:
                    proc.kill()
                    proc.wait(timeout=5)
                    killed_count += 1
                except (psutil.NoSuchProcess, psutil.TimeoutExpired, psutil.AccessDenied):
                    continue
            
            # Wait a moment for cleanup
            await asyncio.sleep(1)
            
            # Try to restart the application
            restart_success = False
            try:
                # This is a simplified restart - in a real system, you'd need
                # to know the actual executable path and command line arguments
                if self.is_windows:
                    subprocess.Popen([package_name], shell=True)
                else:
                    subprocess.Popen([package_name])
                restart_success = True
            except Exception as e:
                logger.warning(f"Could not restart {package_name}: {e}")
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            return HealingResult(
                success=killed_count > 0,
                action_type="restart_app",
                target=package_name,
                duration_ms=duration_ms,
                improvement_score=0.7 if killed_count > 0 else 0.0,
                details={
                    "killed_processes": killed_count,
                    "restart_attempted": restart_success,
                    "total_processes": len(target_processes)
                }
            )
            
        except Exception as e:
            logger.error(f"Error restarting app {package_name}: {e}")
            return HealingResult(
                success=False,
                action_type="restart_app",
                target=package_name,
                duration_ms=int((time.time() - start_time) * 1000),
                improvement_score=0.0,
                details={"error": str(e)},
                error_message=str(e)
            )
    
    async def kill_high_cpu_process(self, pid: int) -> HealingResult:
        """Kill a high CPU usage process"""
        start_time = time.time()
        
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            # Check if it's a critical system process
            critical_processes = {
                'system', 'kernel', 'init', 'systemd', 'winlogon', 'csrss',
                'wininit', 'services', 'lsass', 'svchost', 'explorer'
            }
            
            if process_name.lower() in critical_processes:
                return HealingResult(
                    success=False,
                    action_type="kill_high_cpu_process",
                    target=f"{process_name} (PID: {pid})",
                    duration_ms=int((time.time() - start_time) * 1000),
                    improvement_score=0.0,
                    details={"message": "Critical system process, cannot kill"},
                    error_message="Critical system process"
                )
            
            # Kill the process
            process.kill()
            process.wait(timeout=5)
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            return HealingResult(
                success=True,
                action_type="kill_high_cpu_process",
                target=f"{process_name} (PID: {pid})",
                duration_ms=duration_ms,
                improvement_score=0.8,
                details={
                    "process_name": process_name,
                    "pid": pid,
                    "cpu_usage_before": process.cpu_percent()
                }
            )
            
        except psutil.NoSuchProcess:
            return HealingResult(
                success=False,
                action_type="kill_high_cpu_process",
                target=f"PID: {pid}",
                duration_ms=int((time.time() - start_time) * 1000),
                improvement_score=0.0,
                details={"message": "Process not found"},
                error_message="Process not found"
            )
        except Exception as e:
            logger.error(f"Error killing process {pid}: {e}")
            return HealingResult(
                success=False,
                action_type="kill_high_cpu_process",
                target=f"PID: {pid}",
                duration_ms=int((time.time() - start_time) * 1000),
                improvement_score=0.0,
                details={"error": str(e)},
                error_message=str(e)
            )
    
    async def clear_system_cache(self) -> HealingResult:
        """Clear system cache and temporary files"""
        start_time = time.time()
        
        try:
            cleared_size = 0
            cleared_files = 0
            
            # Get temp directories
            temp_dirs = []
            if self.is_windows:
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
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            return HealingResult(
                success=True,
                action_type="clear_system_cache",
                target="system_cache",
                duration_ms=duration_ms,
                improvement_score=0.6,
                details={
                    "cleared_files": cleared_files,
                    "cleared_size_mb": cleared_size / (1024 * 1024),
                    "temp_dirs_cleared": len(temp_dirs)
                }
            )
            
        except Exception as e:
            logger.error(f"Error clearing system cache: {e}")
            return HealingResult(
                success=False,
                action_type="clear_system_cache",
                target="system_cache",
                duration_ms=int((time.time() - start_time) * 1000),
                improvement_score=0.0,
                details={"error": str(e)},
                error_message=str(e)
            )
    
    async def optimize_memory(self) -> HealingResult:
        """Optimize memory usage by clearing caches and freeing memory"""
        start_time = time.time()
        
        try:
            # Get memory info before optimization
            memory_before = psutil.virtual_memory()
            
            # Clear Python garbage collection
            import gc
            gc.collect()
            
            # Clear system caches (platform specific)
            if self.is_linux:
                # Clear page cache, dentries and inodes
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
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            return HealingResult(
                success=True,
                action_type="optimize_memory",
                target="system_memory",
                duration_ms=duration_ms,
                improvement_score=min(1.0, improvement_percent / 10),  # Scale to 0-1
                details={
                    "memory_before_mb": memory_before.used / (1024 * 1024),
                    "memory_after_mb": memory_after.used / (1024 * 1024),
                    "memory_freed_mb": memory_freed / (1024 * 1024),
                    "improvement_percent": improvement_percent
                }
            )
            
        except Exception as e:
            logger.error(f"Error optimizing memory: {e}")
            return HealingResult(
                success=False,
                action_type="optimize_memory",
                target="system_memory",
                duration_ms=int((time.time() - start_time) * 1000),
                improvement_score=0.0,
                details={"error": str(e)},
                error_message=str(e)
            )
    
    async def restart_service(self, service_name: str) -> HealingResult:
        """Restart a system service"""
        start_time = time.time()
        
        try:
            # Get the appropriate command for the platform
            if self.is_windows:
                cmd = f"net stop {service_name} && net start {service_name}"
            elif self.is_linux:
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
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            if result.returncode == 0:
                return HealingResult(
                    success=True,
                    action_type="restart_service",
                    target=service_name,
                    duration_ms=duration_ms,
                    improvement_score=0.7,
                    details={
                        "service_name": service_name,
                        "command": cmd,
                        "output": result.stdout
                    }
                )
            else:
                return HealingResult(
                    success=False,
                    action_type="restart_service",
                    target=service_name,
                    duration_ms=duration_ms,
                    improvement_score=0.0,
                    details={
                        "service_name": service_name,
                        "command": cmd,
                        "error": result.stderr,
                        "return_code": result.returncode
                    },
                    error_message=result.stderr
                )
                
        except subprocess.TimeoutExpired:
            return HealingResult(
                success=False,
                action_type="restart_service",
                target=service_name,
                duration_ms=int((time.time() - start_time) * 1000),
                improvement_score=0.0,
                details={"error": "Command timeout"},
                error_message="Command timeout"
            )
        except Exception as e:
            logger.error(f"Error restarting service {service_name}: {e}")
            return HealingResult(
                success=False,
                action_type="restart_service",
                target=service_name,
                duration_ms=int((time.time() - start_time) * 1000),
                improvement_score=0.0,
                details={"error": str(e)},
                error_message=str(e)
            )
    
    async def defragment_disk(self, drive: str = "C:") -> HealingResult:
        """Defragment a disk drive"""
        start_time = time.time()
        
        try:
            # Get disk usage before defragmentation
            disk_before = psutil.disk_usage(drive if self.is_windows else '/')
            
            # Get the appropriate command for the platform
            if self.is_windows:
                cmd = f"defrag {drive} /O"
            elif self.is_linux:
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
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            if result.returncode == 0:
                return HealingResult(
                    success=True,
                    action_type="defragment_disk",
                    target=drive,
                    duration_ms=duration_ms,
                    improvement_score=0.5,
                    details={
                        "drive": drive,
                        "command": cmd,
                        "output": result.stdout,
                        "duration_minutes": duration_ms / 60000
                    }
                )
            else:
                return HealingResult(
                    success=False,
                    action_type="defragment_disk",
                    target=drive,
                    duration_ms=duration_ms,
                    improvement_score=0.0,
                    details={
                        "drive": drive,
                        "command": cmd,
                        "error": result.stderr,
                        "return_code": result.returncode
                    },
                    error_message=result.stderr
                )
                
        except subprocess.TimeoutExpired:
            return HealingResult(
                success=False,
                action_type="defragment_disk",
                target=drive,
                duration_ms=int((time.time() - start_time) * 1000),
                improvement_score=0.0,
                details={"error": "Defragmentation timeout"},
                error_message="Defragmentation timeout"
            )
        except Exception as e:
            logger.error(f"Error defragmenting disk {drive}: {e}")
            return HealingResult(
                success=False,
                action_type="defragment_disk",
                target=drive,
                duration_ms=int((time.time() - start_time) * 1000),
                improvement_score=0.0,
                details={"error": str(e)},
                error_message=str(e)
            )
    
    async def check_disk_health(self, drive: str = "C:") -> HealingResult:
        """Check disk health and fix errors"""
        start_time = time.time()
        
        try:
            # Get the appropriate command for the platform
            if self.is_windows:
                cmd = f"chkdsk {drive} /f"
            elif self.is_linux:
                cmd = "fsck -f /"
            else:  # macOS
                cmd = "sudo diskutil verifyDisk /"
            
            # Execute the command
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes timeout
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Check if errors were found and fixed
            errors_found = "errors" in result.stdout.lower() or "bad" in result.stdout.lower()
            errors_fixed = "fixed" in result.stdout.lower() or "corrected" in result.stdout.lower()
            
            improvement_score = 0.3 if errors_found else 0.1
            if errors_fixed:
                improvement_score = 0.8
            
            return HealingResult(
                success=True,
                action_type="check_disk_health",
                target=drive,
                duration_ms=duration_ms,
                improvement_score=improvement_score,
                details={
                    "drive": drive,
                    "command": cmd,
                    "output": result.stdout,
                    "errors_found": errors_found,
                    "errors_fixed": errors_fixed,
                    "return_code": result.returncode
                }
            )
            
        except subprocess.TimeoutExpired:
            return HealingResult(
                success=False,
                action_type="check_disk_health",
                target=drive,
                duration_ms=int((time.time() - start_time) * 1000),
                improvement_score=0.0,
                details={"error": "Disk check timeout"},
                error_message="Disk check timeout"
            )
        except Exception as e:
            logger.error(f"Error checking disk health {drive}: {e}")
            return HealingResult(
                success=False,
                action_type="check_disk_health",
                target=drive,
                duration_ms=int((time.time() - start_time) * 1000),
                improvement_score=0.0,
                details={"error": str(e)},
                error_message=str(e)
            )
    
    async def execute_healing_action(self, action_type: str, target: str, parameters: Dict[str, Any] = None) -> HealingResult:
        """Execute a healing action based on type"""
        parameters = parameters or {}
        
        # Route to appropriate healing method
        if action_type == "restart_app":
            return await self.restart_app(target)
        elif action_type == "kill_high_cpu_process":
            return await self.kill_high_cpu_process(int(target))
        elif action_type == "clear_system_cache":
            return await self.clear_system_cache()
        elif action_type == "optimize_memory":
            return await self.optimize_memory()
        elif action_type == "restart_service":
            return await self.restart_service(target)
        elif action_type == "defragment_disk":
            drive = parameters.get('drive', 'C:')
            return await self.defragment_disk(drive)
        elif action_type == "check_disk_health":
            drive = parameters.get('drive', 'C:')
            return await self.check_disk_health(drive)
        else:
            return HealingResult(
                success=False,
                action_type=action_type,
                target=target,
                duration_ms=0,
                improvement_score=0.0,
                details={"error": "Unknown action type"},
                error_message=f"Unknown action type: {action_type}"
            )
    
    def get_healing_history(self) -> List[Dict[str, Any]]:
        """Get history of healing actions"""
        return self.healing_history
    
    def get_success_rate(self) -> float:
        """Get success rate of healing actions"""
        if not self.healing_history:
            return 0.0
        
        successful = sum(1 for action in self.healing_history if action.get('success', False))
        return (successful / len(self.healing_history)) * 100

