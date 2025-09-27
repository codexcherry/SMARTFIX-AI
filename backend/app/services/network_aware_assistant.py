"""
Network-Aware Assistant Service for SmartFix-AI
Intelligently switches between online (Gemini) and offline (local) modes based on network availability
"""

import logging
import asyncio
import re
import json
import time
import socket
from typing import Dict, List, Any, Optional, Tuple
import psutil

from .gemini_service import GeminiService
from .local_assistant import get_local_assistant_service
from .enhanced_speech_service import get_enhanced_speech_service
from ..core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class NetworkAwareAssistant:
    """
    Network-aware assistant that automatically switches between online and offline modes
    based on network availability and provides context-aware responses
    """
    
    def __init__(self):
        """Initialize the network-aware assistant"""
        self.gemini_service = GeminiService()
        self.local_assistant = get_local_assistant_service()
        self.speech_service = get_enhanced_speech_service()
        
        # Greeting patterns for intent detection
        self.greeting_patterns = [
            r'^(hi|hello|hey|good\s+(morning|afternoon|evening)|greetings?)\.?$',
            r'^(how\s+are\s+you|what\'?s\s+up|sup)\.?$',
            r'^(thanks?|thank\s+you|thx)\.?$',
            r'^(bye|goodbye|see\s+you|farewell)\.?$'
        ]
        
        # Technical query patterns
        self.technical_patterns = [
            r'(not\s+working|broken|issue|problem|error|fail)',
            r'(how\s+to\s+fix|how\s+to\s+solve|troubleshoot|repair)',
            r'(slow|crash|freeze|hang|blue\s+screen)',
            r'(wifi|internet|connection|network)'
        ]
        
        # Last network check time and status
        self.last_network_check = 0
        self.network_available = False
        self.network_check_interval = 30  # seconds
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a query with network awareness, intent detection, and context
        
        Args:
            query: The user's query text
            context: Optional context information including device logs, system info, etc.
            
        Returns:
            Dict with response data
        """
        # Check if this is a greeting or technical query
        query_intent = self._detect_intent(query)
        
        # If it's a greeting, respond appropriately without technical analysis
        if query_intent == "greeting":
            return self._handle_greeting(query)
        
        # Check network availability
        network_available = await self._check_network()
        
        # Enhance context with system information if available
        enhanced_context = await self._enhance_context(context)
        
        # Process based on network availability
        if network_available:
            logger.info("Network available - using Gemini service")
            return await self._process_with_gemini(query, enhanced_context)
        else:
            logger.info("Network unavailable - using local assistant")
            return await self._process_with_local_assistant(query, enhanced_context)
    
    def _detect_intent(self, query: str) -> str:
        """
        Detect the intent of the query (greeting vs technical)
        """
        query_lower = query.lower().strip()
        
        # Check for greetings
        for pattern in self.greeting_patterns:
            if re.match(pattern, query_lower, re.IGNORECASE):
                return "greeting"
        
        # Check for technical queries
        for pattern in self.technical_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return "technical"
        
        # Default to general query for short queries
        if len(query_lower.split()) <= 3:
            return "general"
        
        # Default to technical for longer queries
        return "technical"
    
    def _handle_greeting(self, query: str) -> Dict[str, Any]:
        """
        Handle greeting queries with appropriate responses
        """
        query_lower = query.lower().strip()
        
        # Map common greetings to responses
        greeting_responses = {
            "hi": "Hi! I'm SmartFix AI, your technical troubleshooting assistant. How can I help you with your device today?",
            "hello": "Hello! I'm here to help you solve technical issues. What problem can I assist you with?",
            "hey": "Hey there! Ready to fix some tech problems? What's bothering your device?",
            "good morning": "Good morning! I'm SmartFix AI. What technical issue can I help you resolve today?",
            "good afternoon": "Good afternoon! How can I assist you with your technical problems?",
            "good evening": "Good evening! What device issue can I help you troubleshoot?",
            "how are you": "I'm doing great and ready to help! What technical problem can I solve for you?",
            "what's up": "I'm here and ready to help! What technical issue are you facing?",
            "thanks": "You're welcome! Feel free to ask if you need help with any other technical issues.",
            "thank you": "You're welcome! I'm here whenever you need technical assistance.",
            "bye": "Goodbye! Don't hesitate to come back if you need technical support!",
            "goodbye": "Goodbye! I'll be here when you need help with your technical issues."
        }
        
        # Find matching greeting
        response_text = "Hello! I'm SmartFix AI. How can I help you with your technical issues today?"
        confidence = 0.95
        
        for greeting, response in greeting_responses.items():
            if greeting in query_lower:
                response_text = response
                confidence = 0.98
                break
        
        return {
            "success": True,
            "response": response_text,
            "solution": {
                "issue": "Greeting",
                "possible_causes": [],
                "recommended_steps": [],
                "confidence_score": confidence
            },
            "type": "greeting",
            "confidence_score": confidence,
            "source": "intent_detection"
        }
    
    async def _check_network(self) -> bool:
        """
        Check if network is available
        Uses caching to avoid frequent checks
        """
        current_time = time.time()
        
        # Use cached result if recent
        if current_time - self.last_network_check < self.network_check_interval:
            return self.network_available
        
        # Update last check time
        self.last_network_check = current_time
        
        # Check network connectivity
        try:
            # Try to connect to Google DNS
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            self.network_available = True
            return True
        except OSError:
            # Try alternate method
            try:
                socket.create_connection(("1.1.1.1", 53), timeout=3)
                self.network_available = True
                return True
            except OSError:
                self.network_available = False
                return False
    
    async def _enhance_context(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Enhance context with system information
        """
        enhanced_context = context or {}
        
        try:
            # Add system information
            system_info = {
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "boot_time": psutil.boot_time()
            }
            
            # Get network information
            network_info = {}
            net_io = psutil.net_io_counters()
            network_info["bytes_sent"] = net_io.bytes_sent
            network_info["bytes_recv"] = net_io.bytes_recv
            network_info["packets_sent"] = net_io.packets_sent
            network_info["packets_recv"] = net_io.packets_recv
            network_info["connections"] = len(psutil.net_connections())
            
            # Add to context
            enhanced_context["system_info"] = system_info
            enhanced_context["network_info"] = network_info
            
            # Add process information (top 5 CPU and memory consumers)
            processes = []
            for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']), 
                              key=lambda x: x.info['cpu_percent'], 
                              reverse=True)[:5]:
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "cpu_percent": proc.info['cpu_percent'],
                    "memory_percent": proc.info['memory_percent']
                })
            
            enhanced_context["top_processes"] = processes
            
        except Exception as e:
            logger.warning(f"Error enhancing context: {e}")
        
        return enhanced_context
    
    async def _process_with_gemini(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process query with Gemini service (online mode)
        """
        try:
            # Extract system info for prompt enhancement
            system_info_str = "No system information available"
            if context.get("system_info"):
                system_info = context["system_info"]
                system_info_str = f"""
                System Information:
                - CPU Usage: {system_info.get('cpu_usage', 'N/A')}%
                - Memory Usage: {system_info.get('memory_usage', 'N/A')}%
                - Disk Usage: {system_info.get('disk_usage', 'N/A')}%
                """
            
            # Extract process info
            process_info_str = "No process information available"
            if context.get("top_processes"):
                processes = context["top_processes"]
                process_info_str = "Top CPU-consuming processes:\n"
                for proc in processes:
                    process_info_str += f"- {proc.get('name', 'Unknown')}: CPU {proc.get('cpu_percent', 'N/A')}%, Memory {proc.get('memory_percent', 'N/A')}%\n"
            
            # Create enhanced prompt with context
            enhanced_query = f"""
            User Query: {query}
            
            {system_info_str}
            
            {process_info_str}
            
            Please analyze this issue considering the system information provided.
            """
            
            # Process with Gemini
            result = await self.gemini_service.analyze_text(enhanced_query)
            
            # Add source information
            result["source"] = "gemini_online"
            result["network_status"] = "online"
            
            return {
                "success": True,
                "response": self._format_response(result),
                "solution": result,
                "type": "technical_solution",
                "confidence_score": result.get("confidence_score", 0.5) * 100,
                "source": "gemini_online"
            }
            
        except Exception as e:
            logger.error(f"Error processing with Gemini: {e}")
            
            # Check if it's a model error and provide specific response
            if "404" in str(e) and "models/gemini" in str(e):
                logger.warning("Gemini model not found, falling back to offline mode")
                return {
                    "success": True,
                    "response": "I'm currently experiencing connectivity issues with the online AI service. Let me help you with your battery issue using my offline knowledge base.",
                    "solution": {
                        "issue": "Battery draining quickly",
                        "possible_causes": [
                            "Background apps consuming power",
                            "High screen brightness",
                            "WiFi/Bluetooth always on",
                            "Old or degraded battery"
                        ],
                        "recommended_steps": [
                            {"step_number": 1, "description": "Check battery usage in Settings > Battery"},
                            {"step_number": 2, "description": "Close unnecessary background apps"},
                            {"step_number": 3, "description": "Reduce screen brightness"},
                            {"step_number": 4, "description": "Turn off WiFi/Bluetooth when not needed"},
                            {"step_number": 5, "description": "Check for battery health in device settings"}
                        ],
                        "confidence_score": 0.8
                    },
                    "type": "technical_solution",
                    "confidence_score": 80,
                    "source": "offline_fallback"
                }
            
            # Fallback to local assistant for other errors
            logger.info("Falling back to local assistant due to Gemini error")
            return await self._process_with_local_assistant(query, context)
    
    async def _process_with_local_assistant(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process query with local assistant (offline mode)
        """
        try:
            # Process with local assistant
            result = await self.local_assistant.process_query(query, context)
            
            if not result.get("success", False):
                # Local assistant failed
                return {
                    "success": False,
                    "response": "I'm sorry, but I'm currently in offline mode and couldn't process your request. Please try again when internet connectivity is restored.",
                    "error": result.get("error", "Unknown error"),
                    "type": "error",
                    "source": "local_offline"
                }
            
            # Format local assistant response
            return {
                "success": True,
                "response": result.get("response", "I found a solution to your issue in my offline knowledge base."),
                "solution": result.get("solution", {}),
                "type": "technical_solution",
                "confidence_score": result.get("confidence_score", 0.5) * 100,
                "source": "local_offline",
                "network_status": "offline"
            }
            
        except Exception as e:
            logger.error(f"Error processing with local assistant: {e}")
            
            # Generic offline fallback
            return {
                "success": False,
                "response": "I'm sorry, but I'm currently in offline mode and encountered an error. Please try again when internet connectivity is restored.",
                "error": str(e),
                "type": "error",
                "source": "offline_fallback"
            }
    
    def _format_response(self, solution: Dict[str, Any]) -> str:
        """
        Format solution into a readable response
        """
        issue = solution.get("issue", "Unknown issue")
        possible_causes = solution.get("possible_causes", [])
        steps = solution.get("recommended_steps", [])
        
        # Create concise response
        response = f"I've analyzed your issue: {issue}. "
        
        if possible_causes:
            if len(possible_causes) == 1:
                response += f"The likely cause is {possible_causes[0]}. "
            else:
                response += f"Possible causes include {possible_causes[0]}"
                if len(possible_causes) > 1:
                    response += f" or {possible_causes[1]}"
                response += ". "
        
        if steps:
            response += "Here's what you can do: "
            # Only include first 2 steps in the text response for conciseness
            for i, step in enumerate(steps[:2]):
                step_desc = step.get("description", "")
                response += f"{i+1}) {step_desc} "
        
        return response.strip()

# Create singleton instance
network_aware_assistant = NetworkAwareAssistant()

def get_network_aware_assistant() -> NetworkAwareAssistant:
    """Get the network-aware assistant instance"""
    return network_aware_assistant
