"""
Enhanced Voice Assistant Service for SmartFix-AI
Integrates voice commands with system diagnostics, screenshot analysis, and OCR
"""

import asyncio
import logging
import json
import base64
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import io
from PIL import Image

from .automation_service import AutomationService
from .ocr_service import OCRService
from .validation_service import ValidationService
from .network_diagnostics import NetworkDiagnosticsService
from .system_diagnostics import SystemDiagnosticsService
from .brain_core import BrainCore

logger = logging.getLogger(__name__)

class EnhancedVoiceAssistant:
    """
    Enhanced voice assistant that combines voice input with multi-modal analysis
    """
    
    def __init__(self):
        self.automation_service = AutomationService()
        self.ocr_service = OCRService()
        self.validation_service = ValidationService()
        self.network_diagnostics = NetworkDiagnosticsService()
        self.system_diagnostics = SystemDiagnosticsService()
        self.brain_core = BrainCore()
        
        # Voice command patterns for different actions
        self.command_patterns = {
            "screenshot_analysis": [
                "analyze screen", "check display", "screen issue", "display problem",
                "what's on screen", "screen not working", "display error", "monitor issue"
            ],
            "system_diagnostic": [
                "check system", "system health", "performance check", "cpu usage",
                "memory usage", "disk space", "system slow", "computer slow"
            ],
            "network_diagnostic": [
                "check internet", "network issue", "wifi problem", "connection problem",
                "internet slow", "can't connect", "network test", "ping test"
            ],
            "automation": [
                "take screenshot", "adjust brightness", "change volume", "open app",
                "close app", "volume up", "volume down", "brightness up", "brightness down"
            ]
        }
    
    async def process_voice_command(self, voice_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process voice command with intelligent analysis and multi-modal integration
        """
        try:
            logger.info(f"Processing voice command: {voice_input}")
            
            # Step 1: Validate intent and context
            intent_analysis = await self.validation_service.validate_query_intent(voice_input)
            
            # Handle greetings and non-technical queries
            if intent_analysis["intent"] == "greeting":
                return {
                    "success": True,
                    "response": intent_analysis["suggested_response"],
                    "type": "greeting",
                    "requires_action": False
                }
            
            # Step 2: Determine the type of analysis needed
            command_type = self._classify_voice_command(voice_input)
            
            # Step 3: Execute appropriate analysis based on command type
            if command_type == "screenshot_analysis":
                return await self._handle_screen_analysis(voice_input, context)
            
            elif command_type == "system_diagnostic":
                return await self._handle_system_diagnostic(voice_input, context)
            
            elif command_type == "network_diagnostic":
                return await self._handle_network_diagnostic(voice_input, context)
            
            elif command_type == "automation":
                return await self._handle_automation_command(voice_input, context)
            
            else:
                # Default to general query processing
                return await self._handle_general_query(voice_input, context)
        
        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "Sorry, I encountered an error processing your voice command."
            }
    
    def _classify_voice_command(self, voice_input: str) -> str:
        """
        Classify voice command to determine the appropriate handler
        """
        voice_lower = voice_input.lower()
        
        # Check each command pattern
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                if pattern in voice_lower:
                    return command_type
        
        return "general"
    
    async def _handle_screen_analysis(self, voice_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle screen analysis requests with screenshot + OCR + AI analysis
        """
        try:
            logger.info("Handling screen analysis request")
            
            # Step 1: Take screenshot
            screenshot_result = await self.automation_service.take_screenshot()
            
            if not screenshot_result["success"]:
                return {
                    "success": False,
                    "response": "Unable to take screenshot. Please check permissions.",
                    "error": screenshot_result.get("error", "Screenshot failed")
                }
            
            # Step 2: Extract text from screenshot using OCR
            image_data = screenshot_result.get("image_data", "")
            if image_data.startswith("data:image"):
                # Remove data URL prefix
                image_data = image_data.split(",", 1)[1]
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            
            # Perform OCR
            ocr_result = await self.ocr_service.extract_text_from_image(image_bytes)
            
            # Step 3: Combine voice query with OCR text for comprehensive analysis
            combined_analysis_input = {
                "input_type": "multimodal",
                "voice_query": voice_input,
                "ocr_text": ocr_result.get("text", ""),
                "image_data": image_bytes,
                "analysis_type": "screen_diagnostic"
            }
            
            # Step 4: Use brain core for intelligent analysis
            brain_result = await self.brain_core.process_input(combined_analysis_input)
            
            # Step 5: Generate concise response
            response = self._generate_screen_analysis_response(
                voice_input, 
                ocr_result, 
                brain_result, 
                screenshot_result["filepath"]
            )
            
            return {
                "success": True,
                "response": response["summary"],
                "type": "screen_analysis",
                "details": {
                    "screenshot_path": screenshot_result["filepath"],
                    "ocr_text": ocr_result.get("text", ""),
                    "analysis": brain_result,
                    "recommendations": response["recommendations"]
                }
            }
        
        except Exception as e:
            logger.error(f"Error in screen analysis: {e}")
            return {
                "success": False,
                "response": "I couldn't analyze your screen. Please try again.",
                "error": str(e)
            }
    
    async def _handle_system_diagnostic(self, voice_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle system diagnostic requests
        """
        try:
            logger.info("Handling system diagnostic request")
            
            # Determine specific system check needed
            if any(keyword in voice_input.lower() for keyword in ["cpu", "processor", "performance"]):
                # CPU-focused diagnostic
                diagnostic_result = await self.system_diagnostics._diagnose_cpu()
                summary = self._generate_cpu_summary(diagnostic_result)
            
            elif any(keyword in voice_input.lower() for keyword in ["memory", "ram"]):
                # Memory-focused diagnostic
                diagnostic_result = await self.system_diagnostics._diagnose_memory()
                summary = self._generate_memory_summary(diagnostic_result)
            
            elif any(keyword in voice_input.lower() for keyword in ["disk", "storage", "space"]):
                # Disk-focused diagnostic
                diagnostic_result = await self.system_diagnostics._diagnose_disk()
                summary = self._generate_disk_summary(diagnostic_result)
            
            else:
                # Comprehensive system check
                diagnostic_result = await self.system_diagnostics.comprehensive_system_diagnostic()
                summary = self._generate_comprehensive_system_summary(diagnostic_result)
            
            return {
                "success": True,
                "response": summary["response"],
                "type": "system_diagnostic",
                "details": diagnostic_result,
                "recommendations": summary.get("recommendations", [])
            }
        
        except Exception as e:
            logger.error(f"Error in system diagnostic: {e}")
            return {
                "success": False,
                "response": "I couldn't check your system health. Please try again.",
                "error": str(e)
            }
    
    async def _handle_network_diagnostic(self, voice_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle network diagnostic requests
        """
        try:
            logger.info("Handling network diagnostic request")
            
            # Run comprehensive network test
            network_result = await self.network_diagnostics.comprehensive_network_test()
            
            # Generate concise summary
            summary = self._generate_network_summary(network_result, voice_input)
            
            return {
                "success": True,
                "response": summary["response"],
                "type": "network_diagnostic",
                "details": network_result,
                "recommendations": summary.get("recommendations", [])
            }
        
        except Exception as e:
            logger.error(f"Error in network diagnostic: {e}")
            return {
                "success": False,
                "response": "I couldn't test your network connection. Please try again.",
                "error": str(e)
            }
    
    async def _handle_automation_command(self, voice_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle automation commands (brightness, volume, screenshot, etc.)
        """
        try:
            logger.info("Handling automation command")
            
            voice_lower = voice_input.lower()
            
            # Screenshot commands
            if "screenshot" in voice_lower or "capture screen" in voice_lower:
                result = await self.automation_service.take_screenshot()
                response = "Screenshot taken successfully!" if result["success"] else "Failed to take screenshot."
            
            # Brightness commands
            elif "brightness up" in voice_lower or "brighter" in voice_lower:
                result = await self.automation_service.control_brightness("up")
                response = "Brightness increased!" if result["success"] else "Couldn't adjust brightness."
            
            elif "brightness down" in voice_lower or "dimmer" in voice_lower:
                result = await self.automation_service.control_brightness("down")
                response = "Brightness decreased!" if result["success"] else "Couldn't adjust brightness."
            
            # Volume commands
            elif "volume up" in voice_lower or "louder" in voice_lower:
                result = await self.automation_service.control_volume("up")
                response = "Volume increased!" if result["success"] else "Couldn't adjust volume."
            
            elif "volume down" in voice_lower or "quieter" in voice_lower:
                result = await self.automation_service.control_volume("down")
                response = "Volume decreased!" if result["success"] else "Couldn't adjust volume."
            
            elif "mute" in voice_lower:
                result = await self.automation_service.control_volume("mute")
                response = "Audio muted!" if result["success"] else "Couldn't mute audio."
            
            # App commands
            elif "open" in voice_lower:
                app_name = self._extract_app_name(voice_input)
                if app_name:
                    result = await self.automation_service.open_application(app_name)
                    response = f"Opening {app_name}!" if result["success"] else f"Couldn't open {app_name}."
                else:
                    result = {"success": False}
                    response = "Please specify which application to open."
            
            elif "close" in voice_lower:
                app_name = self._extract_app_name(voice_input)
                if app_name:
                    result = await self.automation_service.close_application(app_name)
                    response = f"Closing {app_name}!" if result["success"] else f"Couldn't close {app_name}."
                else:
                    result = {"success": False}
                    response = "Please specify which application to close."
            
            else:
                result = {"success": False}
                response = "I didn't understand that automation command."
            
            return {
                "success": result["success"],
                "response": response,
                "type": "automation",
                "details": result
            }
        
        except Exception as e:
            logger.error(f"Error in automation command: {e}")
            return {
                "success": False,
                "response": "I couldn't execute that command. Please try again.",
                "error": str(e)
            }
    
    async def _handle_general_query(self, voice_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle general troubleshooting queries
        """
        try:
            logger.info("Handling general query")
            
            # Use brain core for general analysis
            input_data = {
                "input_type": "voice",
                "text_query": voice_input,
                "context": context or {}
            }
            
            brain_result = await self.brain_core.process_input(input_data)
            
            # Generate concise response
            response = self._optimize_general_response(brain_result)
            
            return {
                "success": True,
                "response": response,
                "type": "general_query",
                "details": brain_result
            }
        
        except Exception as e:
            logger.error(f"Error in general query: {e}")
            return {
                "success": False,
                "response": "I couldn't process your query. Please try rephrasing it.",
                "error": str(e)
            }
    
    def _generate_screen_analysis_response(self, voice_query: str, ocr_result: Dict, brain_result: Dict, screenshot_path: str) -> Dict[str, Any]:
        """
        Generate concise response for screen analysis
        """
        ocr_text = ocr_result.get("text", "").strip()
        
        if not ocr_text:
            summary = "I took a screenshot but couldn't detect any text on your screen."
            recommendations = ["Try taking another screenshot with better visibility"]
        else:
            # Analyze the OCR text for potential issues
            issues_found = []
            
            if "error" in ocr_text.lower():
                issues_found.append("Error messages detected on screen")
            
            if "not responding" in ocr_text.lower():
                issues_found.append("Application not responding")
            
            if len(ocr_text) < 10:
                issues_found.append("Limited text detected - screen may be mostly visual")
            
            if issues_found:
                summary = f"Screen analysis complete. Found: {', '.join(issues_found)}"
            else:
                summary = f"Screen appears normal. Detected text includes: {ocr_text[:100]}..."
            
            # Generate recommendations based on brain result
            brain_solution = brain_result.get("solution", {})
            recommendations = [
                step.get("description", "")
                for step in brain_solution.get("recommended_steps", [])[:3]
            ]
        
        return {
            "summary": summary,
            "recommendations": recommendations,
            "confidence": brain_result.get("solution", {}).get("confidence_score", 0.5)
        }
    
    def _generate_cpu_summary(self, cpu_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate concise CPU diagnostic summary"""
        usage = cpu_result.get("usage", {})
        current_usage = usage.get("current", 0)
        issues = cpu_result.get("issues", [])
        
        if current_usage > 80:
            response = f"CPU usage is high at {current_usage:.1f}%. This may slow down your system."
        elif current_usage > 50:
            response = f"CPU usage is moderate at {current_usage:.1f}%. System performance is okay."
        else:
            response = f"CPU usage is low at {current_usage:.1f}%. System performance looks good."
        
        recommendations = []
        if issues:
            recommendations.extend([
                "Close unnecessary programs",
                "Check Task Manager for high CPU processes",
                "Restart your computer if issues persist"
            ])
        
        return {
            "response": response,
            "recommendations": recommendations
        }
    
    def _generate_memory_summary(self, memory_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate concise memory diagnostic summary"""
        usage = memory_result.get("usage", {})
        virtual_mem = usage.get("virtual", {})
        memory_percent = virtual_mem.get("percentage", 0)
        available_gb = virtual_mem.get("available", 0) / (1024**3)
        
        if memory_percent > 85:
            response = f"Memory usage is critical at {memory_percent:.1f}%. Only {available_gb:.1f}GB available."
        elif memory_percent > 70:
            response = f"Memory usage is high at {memory_percent:.1f}%. {available_gb:.1f}GB available."
        else:
            response = f"Memory usage is normal at {memory_percent:.1f}%. {available_gb:.1f}GB available."
        
        recommendations = []
        if memory_percent > 80:
            recommendations.extend([
                "Close unused applications",
                "Restart your computer to free memory",
                "Consider upgrading RAM if this happens frequently"
            ])
        
        return {
            "response": response,
            "recommendations": recommendations
        }
    
    def _generate_disk_summary(self, disk_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate concise disk diagnostic summary"""
        partitions = disk_result.get("partitions", {})
        issues = disk_result.get("issues", [])
        
        if issues:
            response = f"Disk space issues detected: {issues[0]}"
            recommendations = [
                "Delete unnecessary files",
                "Empty recycle bin",
                "Use disk cleanup tools"
            ]
        else:
            response = "Disk space looks healthy on all drives."
            recommendations = ["Continue regular maintenance"]
        
        return {
            "response": response,
            "recommendations": recommendations
        }
    
    def _generate_comprehensive_system_summary(self, system_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate concise comprehensive system summary"""
        health_score = system_result.get("health_score", 50)
        summary = system_result.get("performance_summary", {})
        
        if health_score >= 80:
            response = f"System health is excellent (Score: {health_score}/100). Everything looks good!"
        elif health_score >= 60:
            response = f"System health is good (Score: {health_score}/100). Minor optimizations recommended."
        elif health_score >= 40:
            response = f"System health needs attention (Score: {health_score}/100). Several issues found."
        else:
            response = f"System health is poor (Score: {health_score}/100). Immediate action recommended."
        
        recommendations = system_result.get("recommendations", [])[:3]  # Top 3 recommendations
        
        return {
            "response": response,
            "recommendations": recommendations
        }
    
    def _generate_network_summary(self, network_result: Dict[str, Any], voice_input: str) -> Dict[str, Any]:
        """Generate concise network diagnostic summary"""
        summary = network_result.get("summary", {})
        overall_status = summary.get("overall_status", "unknown")
        
        if overall_status == "excellent":
            response = "Network connection is excellent. All tests passed!"
        elif overall_status == "good":
            response = "Network connection is working well with minor issues."
        elif overall_status == "needs_attention":
            response = "Network connection has several issues that need attention."
        else:
            response = "Network connection problems detected. Troubleshooting needed."
        
        recommendations = network_result.get("recommendations", [])[:3]
        
        return {
            "response": response,
            "recommendations": recommendations
        }
    
    def _optimize_general_response(self, brain_result: Dict[str, Any]) -> str:
        """
        Optimize general response to be concise like ChatGPT
        """
        solution = brain_result.get("solution", {})
        issue = solution.get("issue", "")
        steps = solution.get("recommended_steps", [])
        
        # Create concise response
        if issue:
            response = f"Issue identified: {issue}."
        else:
            response = "I've analyzed your query."
        
        if steps:
            # Add first 2 steps only for conciseness
            response += f" Try: 1) {steps[0].get('description', '')}."
            if len(steps) > 1:
                response += f" 2) {steps[1].get('description', '')}."
        
        return response
    
    def _extract_app_name(self, voice_input: str) -> Optional[str]:
        """
        Extract application name from voice input
        """
        voice_lower = voice_input.lower()
        
        # Common application names
        app_names = [
            "notepad", "calculator", "chrome", "firefox", "edge", "word", "excel",
            "powerpoint", "outlook", "teams", "zoom", "skype", "discord", "spotify",
            "vlc", "photoshop", "illustrator", "steam", "task manager"
        ]
        
        for app in app_names:
            if app in voice_lower:
                return app
        
        # Try to extract app name after "open" or "close"
        words = voice_input.split()
        for i, word in enumerate(words):
            if word.lower() in ["open", "close"] and i + 1 < len(words):
                return words[i + 1]
        
        return None

# Create singleton instance
enhanced_voice_assistant = EnhancedVoiceAssistant()

def get_enhanced_voice_assistant() -> EnhancedVoiceAssistant:
    """Get the enhanced voice assistant instance"""
    return enhanced_voice_assistant
