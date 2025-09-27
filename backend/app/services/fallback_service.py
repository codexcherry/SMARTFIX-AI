"""
Fallback Service - Provides basic functionality when external APIs are not available
"""
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class FallbackService:
    """
    Provides basic troubleshooting functionality without external APIs
    """
    
    def __init__(self):
        self.common_solutions = self._load_common_solutions()
        logger.info("Fallback service initialized with offline solutions")
    
    def _load_common_solutions(self) -> Dict[str, Dict[str, Any]]:
        """Load common troubleshooting solutions"""
        return {
            # Computer/Laptop Issues
            "slow": {
                "issue": "Computer running slowly",
                "possible_causes": ["Too many programs running", "Low disk space", "Malware", "Outdated hardware"],
                "recommended_steps": [
                    {"step_number": 1, "description": "Close unnecessary programs and browser tabs"},
                    {"step_number": 2, "description": "Run disk cleanup to free up space"},
                    {"step_number": 3, "description": "Run antivirus scan to check for malware"},
                    {"step_number": 4, "description": "Restart your computer to clear memory"},
                    {"step_number": 5, "description": "Check for Windows updates"}
                ],
                "confidence_score": 0.85
            },
            "freeze": {
                "issue": "Computer freezing or hanging",
                "possible_causes": ["Overheating", "RAM issues", "Software conflicts", "Driver problems"],
                "recommended_steps": [
                    {"step_number": 1, "description": "Force restart by holding power button for 10 seconds"},
                    {"step_number": 2, "description": "Check if computer is overheating - clean vents"},
                    {"step_number": 3, "description": "Boot in safe mode to identify software issues"},
                    {"step_number": 4, "description": "Update device drivers"},
                    {"step_number": 5, "description": "Run memory diagnostic test"}
                ],
                "confidence_score": 0.80
            },
            "wifi": {
                "issue": "WiFi connection problems",
                "possible_causes": ["Router issues", "Network adapter problems", "Incorrect password", "Signal interference"],
                "recommended_steps": [
                    {"step_number": 1, "description": "Restart your router and modem"},
                    {"step_number": 2, "description": "Forget and reconnect to the WiFi network"},
                    {"step_number": 3, "description": "Update network adapter drivers"},
                    {"step_number": 4, "description": "Move closer to the router"},
                    {"step_number": 5, "description": "Try connecting other devices to test the network"}
                ],
                "confidence_score": 0.90
            },
            "battery": {
                "issue": "Battery draining quickly",
                "possible_causes": ["Background apps", "High screen brightness", "Old battery", "Power-hungry applications"],
                "recommended_steps": [
                    {"step_number": 1, "description": "Check battery usage in settings"},
                    {"step_number": 2, "description": "Close background applications"},
                    {"step_number": 3, "description": "Reduce screen brightness"},
                    {"step_number": 4, "description": "Turn off unnecessary features (Bluetooth, WiFi when not needed)"},
                    {"step_number": 5, "description": "Consider battery replacement if device is old"}
                ],
                "confidence_score": 0.85
            },
            "startup": {
                "issue": "Computer won't start or boot",
                "possible_causes": ["Power supply issues", "Hardware failure", "Corrupted system files", "BIOS settings"],
                "recommended_steps": [
                    {"step_number": 1, "description": "Check power cable and connections"},
                    {"step_number": 2, "description": "Try a different power outlet"},
                    {"step_number": 3, "description": "Remove battery (if laptop) and try power adapter only"},
                    {"step_number": 4, "description": "Try booting from safe mode"},
                    {"step_number": 5, "description": "Contact technical support for hardware diagnosis"}
                ],
                "confidence_score": 0.75
            },
            "audio": {
                "issue": "No sound or audio problems",
                "possible_causes": ["Muted audio", "Driver issues", "Hardware problems", "Incorrect output device"],
                "recommended_steps": [
                    {"step_number": 1, "description": "Check if audio is muted or volume is too low"},
                    {"step_number": 2, "description": "Try different audio output device"},
                    {"step_number": 3, "description": "Update audio drivers"},
                    {"step_number": 4, "description": "Run Windows audio troubleshooter"},
                    {"step_number": 5, "description": "Test with headphones to isolate the issue"}
                ],
                "confidence_score": 0.88
            },
            "display": {
                "issue": "Display or screen problems",
                "possible_causes": ["Cable issues", "Graphics driver problems", "Monitor settings", "Hardware failure"],
                "recommended_steps": [
                    {"step_number": 1, "description": "Check all cable connections"},
                    {"step_number": 2, "description": "Try a different monitor or display"},
                    {"step_number": 3, "description": "Update graphics drivers"},
                    {"step_number": 4, "description": "Adjust display resolution settings"},
                    {"step_number": 5, "description": "Test with external monitor (for laptops)"}
                ],
                "confidence_score": 0.82
            }
        }
    
    def analyze_query(self, query_text: str) -> Dict[str, Any]:
        """
        Analyze a query and provide fallback solution
        """
        query_lower = query_text.lower()
        
        # Find the best matching solution
        best_match = None
        best_score = 0
        
        for keyword, solution in self.common_solutions.items():
            # Simple keyword matching
            if keyword in query_lower:
                score = 1.0
            else:
                # Check for related words
                related_words = {
                    "slow": ["performance", "lag", "laggy", "sluggish"],
                    "freeze": ["hang", "stuck", "unresponsive", "crash"],
                    "wifi": ["internet", "network", "connection", "online"],
                    "battery": ["power", "charge", "charging"],
                    "startup": ["boot", "start", "turn on", "power on"],
                    "audio": ["sound", "speaker", "music", "volume"],
                    "display": ["screen", "monitor", "video", "graphics"]
                }
                
                score = 0
                for word in related_words.get(keyword, []):
                    if word in query_lower:
                        score = 0.8
                        break
            
            if score > best_score:
                best_score = score
                best_match = solution
        
        # If no specific match, provide general troubleshooting
        if not best_match or best_score < 0.5:
            best_match = {
                "issue": "General troubleshooting assistance",
                "possible_causes": ["Various technical issues", "Software or hardware problems"],
                "recommended_steps": [
                    {"step_number": 1, "description": "Restart your device to clear temporary issues"},
                    {"step_number": 2, "description": "Check for system updates"},
                    {"step_number": 3, "description": "Run built-in troubleshooting tools"},
                    {"step_number": 4, "description": "Check device documentation or support website"},
                    {"step_number": 5, "description": "Contact technical support for specific assistance"}
                ],
                "confidence_score": 0.6
            }
        
        return {
            "query_id": f"fallback_{hash(query_text) % 10000}",
            "solution": {
                "issue": best_match["issue"],
                "possible_causes": best_match["possible_causes"],
                "confidence_score": best_match["confidence_score"],
                "recommended_steps": best_match["recommended_steps"],
                "external_sources": [],
                "additional_info": "This solution is provided by the offline fallback system."
            },
            "source": "fallback_service",
            "query_text": query_text
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get fallback service status"""
        return {
            "service": "fallback",
            "status": "active",
            "available_solutions": len(self.common_solutions),
            "mode": "offline"
        }

# Global instance
fallback_service = FallbackService()

def get_fallback_service() -> FallbackService:
    """Get the fallback service instance"""
    return fallback_service

