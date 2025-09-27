"""
Enhanced Offline Assistant Service for SmartFix-AI
Provides robust offline capabilities with intent detection and context awareness
"""

import os
import sys
import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple
import re

# Add the assistant directory to the path
assistant_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assistant")
if assistant_path not in sys.path:
    sys.path.append(assistant_path)

# Import the assistant API if available
try:
    from assistant.api_integration import get_assistant_api
    from assistant.llm_assistant import LLMAssistant
    ASSISTANT_AVAILABLE = True
except ImportError:
    ASSISTANT_AVAILABLE = False
    get_assistant_api = None
    LLMAssistant = None

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedOfflineAssistant:
    """
    Enhanced offline assistant with intent detection and context awareness
    """
    
    def __init__(self):
        """Initialize the enhanced offline assistant"""
        self.llm_assistant = self._initialize_llm_assistant()
        self.available = self.llm_assistant is not None
        self.conversation_history = []
        
        # Define greeting patterns
        self.greeting_patterns = [
            r'^(hi|hello|hey|good\s+(morning|afternoon|evening)|greetings?)\.?$',
            r'^(how\s+are\s+you|what\'?s\s+up|sup)\.?$',
            r'^(thanks?|thank\s+you|thx)\.?$',
            r'^(bye|goodbye|see\s+you|farewell)\.?$'
        ]
        
        # Define common troubleshooting templates
        self.troubleshooting_templates = self._load_troubleshooting_templates()
    
    def _initialize_llm_assistant(self) -> Optional[Any]:
        """Initialize the LLM assistant"""
        if not ASSISTANT_AVAILABLE:
            logger.warning("LLM Assistant not available - missing dependencies")
            return None
        
        try:
            llm_assistant = LLMAssistant()
            if not llm_assistant.index_available:
                logger.warning("LLM Assistant index not available")
                return None
                
            return llm_assistant
        except Exception as e:
            logger.error(f"Error initializing LLM Assistant: {e}")
            return None
    
    def _load_troubleshooting_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load common troubleshooting templates for offline use"""
        templates = {
            "network": {
                "issue": "Network Connectivity Problem",
                "possible_causes": [
                    "Router/modem issues",
                    "ISP service disruption",
                    "Network adapter problems",
                    "Incorrect network configuration"
                ],
                "recommended_steps": [
                    {"step_number": 1, "description": "Restart your router and modem"},
                    {"step_number": 2, "description": "Check network cables are properly connected"},
                    {"step_number": 3, "description": "Reset network adapter on your device"},
                    {"step_number": 4, "description": "Verify IP address settings"},
                    {"step_number": 5, "description": "Contact your ISP if problems persist"}
                ],
                "confidence_score": 0.85,
                "keywords": ["wifi", "internet", "network", "connection", "router", "modem", "ethernet", "offline"]
            },
            "display": {
                "issue": "Display/Monitor Connection Issue",
                "possible_causes": [
                    "Cable connection problem",
                    "Graphics driver issues",
                    "Incompatible resolution settings",
                    "Hardware failure"
                ],
                "recommended_steps": [
                    {"step_number": 1, "description": "Check cable connections between computer and monitor"},
                    {"step_number": 2, "description": "Try different ports (HDMI, DisplayPort, VGA)"},
                    {"step_number": 3, "description": "Update graphics drivers to the latest version"},
                    {"step_number": 4, "description": "Press Windows+P to check display projection settings"},
                    {"step_number": 5, "description": "Test with a different monitor if available"}
                ],
                "confidence_score": 0.8,
                "keywords": ["screen", "monitor", "display", "resolution", "graphics", "video", "hdmi", "vga"]
            },
            "performance": {
                "issue": "System Performance Issues",
                "possible_causes": [
                    "Too many background processes",
                    "Insufficient system resources",
                    "Outdated drivers",
                    "Malware infection",
                    "Hardware limitations"
                ],
                "recommended_steps": [
                    {"step_number": 1, "description": "Close unnecessary applications"},
                    {"step_number": 2, "description": "Restart your computer"},
                    {"step_number": 3, "description": "Check Task Manager for resource-intensive processes"},
                    {"step_number": 4, "description": "Update drivers and operating system"},
                    {"step_number": 5, "description": "Run a virus scan"}
                ],
                "confidence_score": 0.8,
                "keywords": ["slow", "performance", "lag", "freeze", "crash", "hang", "not responding"]
            },
            "audio": {
                "issue": "Audio/Sound Problem",
                "possible_causes": [
                    "Muted audio",
                    "Audio driver issues",
                    "Incorrect audio output selection",
                    "Hardware failure"
                ],
                "recommended_steps": [
                    {"step_number": 1, "description": "Check if device is muted - look for mute button or icon"},
                    {"step_number": 2, "description": "Verify volume is turned up"},
                    {"step_number": 3, "description": "Check audio output settings"},
                    {"step_number": 4, "description": "Update audio drivers"},
                    {"step_number": 5, "description": "Test with headphones or external speakers"}
                ],
                "confidence_score": 0.8,
                "keywords": ["sound", "audio", "speaker", "volume", "mute", "headphones", "microphone"]
            },
            "printer": {
                "issue": "Printer Connection or Functionality Problem",
                "possible_causes": [
                    "Printer offline or powered off",
                    "Connection issues (USB/network)",
                    "Driver problems",
                    "Print queue errors",
                    "Out of paper or ink"
                ],
                "recommended_steps": [
                    {"step_number": 1, "description": "Check if printer is powered on and connected"},
                    {"step_number": 2, "description": "Verify paper and ink/toner levels"},
                    {"step_number": 3, "description": "Restart the printer"},
                    {"step_number": 4, "description": "Clear the print queue"},
                    {"step_number": 5, "description": "Reinstall printer drivers"}
                ],
                "confidence_score": 0.8,
                "keywords": ["printer", "print", "scanning", "scanner", "ink", "toner"]
            },
            "battery": {
                "issue": "Battery Life or Charging Problem",
                "possible_causes": [
                    "Background apps consuming power",
                    "High screen brightness",
                    "WiFi/Bluetooth always on",
                    "Old or degraded battery",
                    "Power-hungry applications",
                    "Charging cable or port issues"
                ],
                "recommended_steps": [
                    {"step_number": 1, "description": "Check battery usage in Settings > Battery"},
                    {"step_number": 2, "description": "Close unnecessary background apps"},
                    {"step_number": 3, "description": "Reduce screen brightness"},
                    {"step_number": 4, "description": "Turn off WiFi/Bluetooth when not needed"},
                    {"step_number": 5, "description": "Check for battery health in device settings"},
                    {"step_number": 6, "description": "Use power saving mode when battery is low"}
                ],
                "confidence_score": 0.85,
                "keywords": ["battery", "charging", "power", "drain", "adapter", "charger", "draining", "drains", "quickly", "fast"]
            }
        }
        
        return templates
    
    def _get_greeting_response(self, query: str) -> Dict[str, Any]:
        """Generate appropriate greeting responses"""
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
        for greeting, response in greeting_responses.items():
            if greeting in query_lower:
                response_text = response
                break
        
        return {
            "success": True,
            "response": response_text,
            "solution": {
                "issue": "Greeting",
                "possible_causes": [],
                "recommended_steps": [],
                "confidence_score": 0.95
            },
            "type": "greeting",
            "confidence_score": 0.95,
            "source": "offline_template"
        }
    
    def _match_template(self, query: str) -> Optional[Dict[str, Any]]:
        """Match query to a troubleshooting template based on keywords"""
        query_lower = query.lower()
        
        best_match = None
        best_score = 0
        
        for template_name, template in self.troubleshooting_templates.items():
            score = 0
            keywords = template.get("keywords", [])
            
            # Count keyword matches
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
            
            # Calculate match score as percentage of keywords matched
            if keywords:
                match_score = score / len(keywords)
                
                # Update best match if score is higher
                if match_score > best_score and match_score > 0.1:  # At least one keyword must match
                    best_score = match_score
                    best_match = template.copy()
                    best_match["template_name"] = template_name
                    best_match["match_score"] = match_score
        
        return best_match
    
    def _detect_intent(self, query: str) -> str:
        """Detect intent of the query"""
        query_lower = query.lower().strip()
        
        # Check for greetings
        for pattern in self.greeting_patterns:
            if re.match(pattern, query_lower, re.IGNORECASE):
                return "greeting"
        
        # Default to technical query
        return "technical"
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a query using enhanced offline capabilities
        
        Args:
            query: The user's query
            context: Optional context information
            
        Returns:
            Dict with response data
        """
        if not self.available:
            return {
                "success": False,
                "error": "Enhanced offline assistant not available",
                "response": "I'm sorry, but the offline assistant is not available. Please check your installation.",
                "fallback_to_online": True
            }
        
        try:
            # Detect intent
            intent = self._detect_intent(query)
            
            # Handle greetings
            if intent == "greeting":
                return self._get_greeting_response(query)
            
            # Try to match a template first for common issues
            template_match = self._match_template(query)
            if template_match and template_match.get("match_score", 0) > 0.3:
                # Good template match found
                return {
                    "success": True,
                    "response": f"I've found a solution for your {template_match['issue'].lower()}. {self._format_template_response(template_match)}",
                    "solution": template_match,
                    "type": "technical_solution",
                    "confidence_score": template_match.get("confidence_score", 0.7) * 100,
                    "source": "offline_template",
                    "template_name": template_match.get("template_name")
                }
            
            # Fall back to LLM assistant for more complex queries
            llm_response = self.llm_assistant.process_query(query)
            
            # Update conversation history
            self.conversation_history.append({
                "user": query,
                "assistant": llm_response
            })
            
            # Format the response
            return {
                "success": True,
                "response": llm_response,
                "solution": self._extract_solution_from_llm_response(llm_response),
                "type": "technical_solution",
                "confidence_score": 75,  # Default confidence for LLM responses
                "source": "offline_llm"
            }
            
        except Exception as e:
            logger.error(f"Error processing query with enhanced offline assistant: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I'm sorry, but I encountered an error while processing your request in offline mode.",
                "fallback_to_online": True
            }
    
    def _format_template_response(self, template: Dict[str, Any]) -> str:
        """Format template into readable response"""
        possible_causes = template.get("possible_causes", [])
        steps = template.get("recommended_steps", [])
        
        response = ""
        
        # Add possible causes
        if possible_causes:
            if len(possible_causes) == 1:
                response += f"The likely cause is {possible_causes[0]}. "
            else:
                response += f"Possible causes include {possible_causes[0]}"
                if len(possible_causes) > 1:
                    response += f" or {possible_causes[1]}"
                response += ". "
        
        # Add recommended steps
        if steps:
            response += "Here's what you should do: "
            for step in steps[:3]:  # Include only first 3 steps for brevity
                response += f"{step.get('step_number', 0)}. {step.get('description', '')}. "
        
        return response
    
    def _extract_solution_from_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """Extract structured solution from LLM response text"""
        # Simple extraction of issue from first sentence
        issue = llm_response.split('.')[0] if '.' in llm_response else llm_response[:50]
        
        # Extract steps using regex
        step_pattern = r'(\d+)\.\s+([^.]+)'
        steps = []
        
        for match in re.finditer(step_pattern, llm_response):
            step_num = int(match.group(1))
            description = match.group(2).strip()
            steps.append({
                "step_number": step_num,
                "description": description
            })
        
        # Extract possible causes
        causes = []
        if "cause" in llm_response.lower():
            causes_text = llm_response.lower().split("cause", 1)[1].split(".")[0]
            causes = [causes_text.strip()]
        
        return {
            "issue": issue,
            "possible_causes": causes,
            "recommended_steps": steps,
            "confidence_score": 0.75
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the enhanced offline assistant"""
        return {
            "available": self.available,
            "status": "ready" if self.available else "unavailable",
            "llm_available": self.llm_assistant is not None,
            "templates_available": len(self.troubleshooting_templates) > 0,
            "conversation_history_length": len(self.conversation_history)
        }

# Create singleton instance
enhanced_offline_assistant = EnhancedOfflineAssistant()

def get_enhanced_offline_assistant() -> EnhancedOfflineAssistant:
    """Get the enhanced offline assistant instance"""
    return enhanced_offline_assistant
