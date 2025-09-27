import os
import sys
import logging
import subprocess
import platform
import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomationService:
    """Service for automating system operations and device controls"""
    
    def __init__(self):
        """Initialize the automation service"""
        self.system = platform.system()  # 'Windows', 'Linux', 'Darwin' (macOS)
        logger.info(f"Initializing automation service for {self.system}")
        
        # Track automation status
        self.last_action = None
        self.status = "ready"
    
    async def execute_command(self, command: str, shell: bool = True) -> Dict[str, Any]:
        """Execute a system command and return the result"""
        try:
            logger.info(f"Executing command: {command}")
            
            # Create a subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=shell
            )
            
            # Wait for the process to complete and get output
            stdout, stderr = await process.communicate()
            
            # Process the results
            if process.returncode == 0:
                logger.info(f"Command executed successfully")
                return {
                    "success": True,
                    "stdout": stdout.decode('utf-8', errors='replace'),
                    "stderr": stderr.decode('utf-8', errors='replace'),
                    "return_code": process.returncode
                }
            else:
                logger.error(f"Command failed with return code {process.returncode}")
                return {
                    "success": False,
                    "stdout": stdout.decode('utf-8', errors='replace'),
                    "stderr": stderr.decode('utf-8', errors='replace'),
                    "return_code": process.returncode,
                    "error": f"Command failed with return code {process.returncode}"
                }
                
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def control_brightness(self, direction: str) -> Dict[str, Any]:
        """Control screen brightness"""
        try:
            self.last_action = f"brightness_{direction}"
            self.status = f"Adjusting brightness {direction}"
            
            if self.system == "Windows":
                # On Windows, we can use PowerShell to adjust brightness
                if direction == "up":
                    # This is a placeholder - actual implementation would use Windows API
                    # or a third-party tool to control brightness
                    command = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 100)"
                    result = await self.execute_command(f"powershell -Command \"{command}\"")
                else:
                    command = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 30)"
                    result = await self.execute_command(f"powershell -Command \"{command}\"")
                
                return {
                    "success": result["success"],
                    "action": f"brightness_{direction}",
                    "message": f"Brightness adjusted {direction}",
                    "details": result
                }
                
            elif self.system == "Linux":
                # On Linux, we can use xrandr or similar tools
                if direction == "up":
                    command = "xrandr --output $(xrandr | grep ' connected' | head -n 1 | cut -d ' ' -f1) --brightness 1.0"
                else:
                    command = "xrandr --output $(xrandr | grep ' connected' | head -n 1 | cut -d ' ' -f1) --brightness 0.5"
                
                result = await self.execute_command(command)
                return {
                    "success": result["success"],
                    "action": f"brightness_{direction}",
                    "message": f"Brightness adjusted {direction}",
                    "details": result
                }
                
            elif self.system == "Darwin":  # macOS
                # On macOS, we can use brightness command line tools
                if direction == "up":
                    command = "brightness 1.0"
                else:
                    command = "brightness 0.5"
                
                result = await self.execute_command(command)
                return {
                    "success": result["success"],
                    "action": f"brightness_{direction}",
                    "message": f"Brightness adjusted {direction}",
                    "details": result
                }
                
            else:
                return {
                    "success": False,
                    "action": f"brightness_{direction}",
                    "message": f"Brightness control not supported on {self.system}",
                    "error": "Unsupported platform"
                }
                
        except Exception as e:
            logger.error(f"Error controlling brightness: {str(e)}")
            return {
                "success": False,
                "action": f"brightness_{direction}",
                "message": f"Failed to adjust brightness {direction}",
                "error": str(e)
            }
    
    async def control_volume(self, action: str) -> Dict[str, Any]:
        """Control system volume (up, down, mute)"""
        try:
            self.last_action = f"volume_{action}"
            self.status = f"Adjusting volume {action}"
            
            if self.system == "Windows":
                # On Windows, we can use PowerShell to control volume
                if action == "up":
                    command = "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"  # Volume up key
                elif action == "down":
                    command = "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"  # Volume down key
                else:  # mute
                    command = "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"  # Mute key
                
                result = await self.execute_command(f"powershell -Command \"{command}\"")
                
            elif self.system == "Linux":
                # On Linux, we can use amixer or pactl
                if action == "up":
                    command = "amixer -D pulse sset Master 10%+"
                elif action == "down":
                    command = "amixer -D pulse sset Master 10%-"
                else:  # mute
                    command = "amixer -D pulse sset Master toggle"
                
                result = await self.execute_command(command)
                
            elif self.system == "Darwin":  # macOS
                # On macOS, we can use osascript
                if action == "up":
                    command = "osascript -e 'set volume output volume (output volume of (get volume settings) + 10)'"
                elif action == "down":
                    command = "osascript -e 'set volume output volume (output volume of (get volume settings) - 10)'"
                else:  # mute
                    command = "osascript -e 'set volume with output muted'"
                
                result = await self.execute_command(command)
                
            else:
                return {
                    "success": False,
                    "action": f"volume_{action}",
                    "message": f"Volume control not supported on {self.system}",
                    "error": "Unsupported platform"
                }
            
            return {
                "success": result["success"],
                "action": f"volume_{action}",
                "message": f"Volume {action} completed",
                "details": result
            }
                
        except Exception as e:
            logger.error(f"Error controlling volume: {str(e)}")
            return {
                "success": False,
                "action": f"volume_{action}",
                "message": f"Failed to adjust volume {action}",
                "error": str(e)
            }
    
    async def take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot of the current screen"""
        try:
            self.last_action = "screenshot"
            self.status = "Taking screenshot"
            
            # Create screenshots directory if it doesn't exist
            screenshots_dir = Path("./screenshots")
            screenshots_dir.mkdir(exist_ok=True)
            
            # Generate a filename based on timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = screenshots_dir / filename
            
            if self.system == "Windows":
                # On Windows, we can use PowerShell to take a screenshot
                command = f"""
                Add-Type -AssemblyName System.Windows.Forms
                Add-Type -AssemblyName System.Drawing
                $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
                $bitmap = New-Object System.Drawing.Bitmap $screen.Width, $screen.Height
                $graphic = [System.Drawing.Graphics]::FromImage($bitmap)
                $graphic.CopyFromScreen($screen.X, $screen.Y, 0, 0, $bitmap.Size)
                $bitmap.Save('{filepath}')
                """
                result = await self.execute_command(f"powershell -Command \"{command}\"")
                
            elif self.system == "Linux":
                # On Linux, we can use scrot or import
                command = f"import -window root {filepath}"
                result = await self.execute_command(command)
                
            elif self.system == "Darwin":  # macOS
                # On macOS, we can use screencapture
                command = f"screencapture -x {filepath}"
                result = await self.execute_command(command)
                
            else:
                return {
                    "success": False,
                    "action": "screenshot",
                    "message": f"Screenshot not supported on {self.system}",
                    "error": "Unsupported platform"
                }
            
            if result["success"] and os.path.exists(filepath):
                # Read the screenshot file as base64 for returning to frontend
                import base64
                with open(filepath, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")
                
                return {
                    "success": True,
                    "action": "screenshot",
                    "message": "Screenshot taken successfully",
                    "filepath": str(filepath),
                    "image_data": f"data:image/png;base64,{image_data}"
                }
            else:
                return {
                    "success": False,
                    "action": "screenshot",
                    "message": "Failed to take screenshot",
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return {
                "success": False,
                "action": "screenshot",
                "message": "Failed to take screenshot",
                "error": str(e)
            }
    
    async def open_application(self, app_name: str) -> Dict[str, Any]:
        """Open an application by name"""
        try:
            self.last_action = f"open_{app_name}"
            self.status = f"Opening {app_name}"
            
            if self.system == "Windows":
                # On Windows, we can use start command
                command = f"start {app_name}"
                result = await self.execute_command(command)
                
            elif self.system == "Linux":
                # On Linux, we can use xdg-open or specific app names
                command = f"{app_name} &"
                result = await self.execute_command(command)
                
            elif self.system == "Darwin":  # macOS
                # On macOS, we can use open
                command = f"open -a '{app_name}'"
                result = await self.execute_command(command)
                
            else:
                return {
                    "success": False,
                    "action": f"open_{app_name}",
                    "message": f"Opening applications not supported on {self.system}",
                    "error": "Unsupported platform"
                }
            
            return {
                "success": result["success"],
                "action": f"open_{app_name}",
                "message": f"Application {app_name} opened",
                "details": result
            }
                
        except Exception as e:
            logger.error(f"Error opening application: {str(e)}")
            return {
                "success": False,
                "action": f"open_{app_name}",
                "message": f"Failed to open {app_name}",
                "error": str(e)
            }
    
    async def close_application(self, app_name: str) -> Dict[str, Any]:
        """Close an application by name"""
        try:
            self.last_action = f"close_{app_name}"
            self.status = f"Closing {app_name}"
            
            if self.system == "Windows":
                # On Windows, we can use taskkill
                command = f"taskkill /F /IM {app_name}.exe"
                result = await self.execute_command(command)
                
            elif self.system == "Linux":
                # On Linux, we can use pkill
                command = f"pkill {app_name}"
                result = await self.execute_command(command)
                
            elif self.system == "Darwin":  # macOS
                # On macOS, we can use osascript to quit an application
                command = f"osascript -e 'quit app \"{app_name}\"'"
                result = await self.execute_command(command)
                
            else:
                return {
                    "success": False,
                    "action": f"close_{app_name}",
                    "message": f"Closing applications not supported on {self.system}",
                    "error": "Unsupported platform"
                }
            
            return {
                "success": result["success"],
                "action": f"close_{app_name}",
                "message": f"Application {app_name} closed",
                "details": result
            }
                
        except Exception as e:
            logger.error(f"Error closing application: {str(e)}")
            return {
                "success": False,
                "action": f"close_{app_name}",
                "message": f"Failed to close {app_name}",
                "error": str(e)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the automation service"""
        return {
            "status": self.status,
            "last_action": self.last_action,
            "system": self.system,
            "available_actions": [
                "brightness_up",
                "brightness_down",
                "volume_up",
                "volume_down",
                "volume_mute",
                "screenshot",
                "open_application",
                "close_application"
            ]
        }

# Create a singleton instance
automation_service = AutomationService()

def get_automation_service() -> AutomationService:
    """Get the automation service instance"""
    return automation_service
