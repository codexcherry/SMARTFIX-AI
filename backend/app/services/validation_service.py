"""
Advanced Validation Service for SmartFix-AI
Validates all responses from AI services to ensure accuracy and relevance
"""

import re
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import hashlib

from .serpapi_service import SerpAPIService
from .automation_service import AutomationService
from ..core.config import settings

logger = logging.getLogger(__name__)

class ValidationService:
    """
    Comprehensive validation service that ensures response accuracy and relevance
    """
    
    def __init__(self):
        self.serp_service = SerpAPIService()
        self.automation_service = AutomationService()
        
        # Intent classification patterns
        self.greeting_patterns = [
            r'^(hi|hello|hey|good\s+(morning|afternoon|evening)|greetings?)\.?$',
            r'^(how\s+are\s+you|what\'?s\s+up|sup)\.?$',
            r'^(thanks?|thank\s+you|thx)\.?$',
            r'^(bye|goodbye|see\s+you|farewell)\.?$'
        ]
        
        self.technical_keywords = [
            'error', 'broken', 'not working', 'issue', 'problem', 'fix', 'repair',
            'screen', 'display', 'monitor', 'keyboard', 'mouse', 'wifi', 'internet',
            'computer', 'laptop', 'phone', 'device', 'software', 'hardware',
            'crash', 'freeze', 'slow', 'virus', 'malware', 'update', 'install'
        ]
        
        # Network diagnostic commands for OS integration
        self.network_commands = {
            'ping': 'ping -c 4 {target}',
            'traceroute': 'traceroute {target}',
            'nslookup': 'nslookup {target}',
            'netstat': 'netstat -tuln',
            'arp': 'arp -a'
        }
        
        # System diagnostic commands
        self.system_commands = {
            'cpu_info': 'cat /proc/cpuinfo',
            'memory_info': 'free -h',
            'disk_usage': 'df -h',
            'process_list': 'ps aux',
            'system_load': 'uptime'
        }
    
    async def validate_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Classify query intent to prevent inappropriate responses
        """
        query_lower = query.lower().strip()
        
        # Check for greetings
        for pattern in self.greeting_patterns:
            if re.match(pattern, query_lower, re.IGNORECASE):
                return {
                    "intent": "greeting",
                    "confidence": 0.95,
                    "requires_technical_response": False,
                    "suggested_response": self._get_greeting_response(query_lower)
                }
        
        # Check for technical keywords
        technical_score = 0
        for keyword in self.technical_keywords:
            if keyword in query_lower:
                technical_score += 1
        
        if technical_score > 0:
            return {
                "intent": "technical_query",
                "confidence": min(technical_score * 0.2, 0.9),
                "requires_technical_response": True,
                "technical_keywords": [kw for kw in self.technical_keywords if kw in query_lower]
            }
        
        # Check for networking queries
        network_keywords = ['ping', 'internet', 'wifi', 'network', 'connection', 'dns', 'ip']
        if any(kw in query_lower for kw in network_keywords):
            return {
                "intent": "network_diagnostic",
                "confidence": 0.8,
                "requires_technical_response": True,
                "diagnostic_type": "network"
            }
        
        # Check for system queries
        system_keywords = ['cpu', 'memory', 'disk', 'performance', 'slow', 'process']
        if any(kw in query_lower for kw in system_keywords):
            return {
                "intent": "system_diagnostic",
                "confidence": 0.8,
                "requires_technical_response": True,
                "diagnostic_type": "system"
            }
        
        # Default to general query
        return {
            "intent": "general_query",
            "confidence": 0.5,
            "requires_technical_response": True
        }
    
    def _get_greeting_response(self, query: str) -> str:
        """Generate appropriate greeting responses"""
        greetings_map = {
            'hi': "Hi! I'm SmartFix AI, your technical troubleshooting assistant. How can I help you with your device today?",
            'hello': "Hello! I'm here to help you solve technical issues. What problem can I assist you with?",
            'hey': "Hey there! Ready to fix some tech problems? What's bothering your device?",
            'good morning': "Good morning! I'm SmartFix AI. What technical issue can I help you resolve today?",
            'good afternoon': "Good afternoon! How can I assist you with your technical problems?",
            'good evening': "Good evening! What device issue can I help you troubleshoot?",
            'how are you': "I'm doing great and ready to help! What technical problem can I solve for you?",
            'thanks': "You're welcome! Feel free to ask if you need help with any other technical issues.",
            'bye': "Goodbye! Don't hesitate to come back if you need technical support!"
        }
        
        for key, response in greetings_map.items():
            if key in query.lower():
                return response
        
        return "Hello! I'm SmartFix AI. How can I help you with your technical issues today?"
    
    async def validate_response_accuracy(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate response accuracy using multiple methods
        """
        validation_result = {
            "is_valid": True,
            "confidence_score": response.get("solution", {}).get("confidence_score", 0.5),
            "validation_methods": [],
            "issues_found": [],
            "enhanced_response": None
        }
        
        try:
            # Method 1: Cross-reference with SerpAPI for external validation
            if settings.SERPAPI_AVAILABLE:
                external_validation = await self._validate_with_serpapi(query, response)
                validation_result["validation_methods"].append("serpapi")
                
                if external_validation["matches_found"] < 2:
                    validation_result["issues_found"].append("Low external validation")
                    validation_result["confidence_score"] *= 0.7
            
            # Method 2: Technical keyword validation
            technical_validation = self._validate_technical_keywords(query, response)
            validation_result["validation_methods"].append("technical_keywords")
            
            if not technical_validation["keywords_match"]:
                validation_result["issues_found"].append("Keywords don't match solution")
                validation_result["confidence_score"] *= 0.8
            
            # Method 3: Solution step validation
            step_validation = self._validate_solution_steps(response)
            validation_result["validation_methods"].append("solution_steps")
            
            if not step_validation["steps_valid"]:
                validation_result["issues_found"].append("Invalid solution steps")
                validation_result["confidence_score"] *= 0.6
            
            # Method 4: Response length optimization
            optimized_response = self._optimize_response_length(response)
            validation_result["enhanced_response"] = optimized_response
            
            # Final validation decision
            if validation_result["confidence_score"] < 0.3 or len(validation_result["issues_found"]) > 2:
                validation_result["is_valid"] = False
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error in response validation: {e}")
            validation_result["is_valid"] = False
            validation_result["issues_found"].append(f"Validation error: {str(e)}")
            return validation_result
    
    async def _validate_with_serpapi(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response using SerpAPI external search"""
        try:
            # Extract key terms from the solution
            solution = response.get("solution", {})
            issue = solution.get("issue", "")
            
            # Search for similar solutions online
            search_results = await self.serp_service.search_solutions(f"{issue} fix solution")
            
            matches_found = 0
            for result in search_results:
                # Simple keyword matching (can be enhanced with NLP)
                if any(word in result["snippet"].lower() for word in issue.lower().split()):
                    matches_found += 1
            
            return {
                "matches_found": matches_found,
                "external_sources": search_results[:3]  # Top 3 matches
            }
            
        except Exception as e:
            logger.error(f"SerpAPI validation error: {e}")
            return {"matches_found": 0, "external_sources": []}
    
    def _validate_technical_keywords(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that response keywords match query intent"""
        query_words = set(query.lower().split())
        solution = response.get("solution", {})
        
        # Extract words from solution
        solution_text = f"{solution.get('issue', '')} {' '.join([step.get('description', '') for step in solution.get('recommended_steps', [])])}"
        solution_words = set(solution_text.lower().split())
        
        # Check for keyword overlap
        common_words = query_words.intersection(solution_words)
        match_ratio = len(common_words) / len(query_words) if query_words else 0
        
        return {
            "keywords_match": match_ratio > 0.3,
            "match_ratio": match_ratio,
            "common_keywords": list(common_words)
        }
    
    def _validate_solution_steps(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate solution steps for completeness and logic"""
        solution = response.get("solution", {})
        steps = solution.get("recommended_steps", [])
        
        issues = []
        
        # Check if steps exist
        if not steps:
            issues.append("No solution steps provided")
        
        # Check step numbering
        for i, step in enumerate(steps):
            expected_num = i + 1
            actual_num = step.get("step_number", 0)
            if actual_num != expected_num:
                issues.append(f"Step numbering error: expected {expected_num}, got {actual_num}")
        
        # Check step descriptions
        for step in steps:
            description = step.get("description", "")
            if len(description) < 10:
                issues.append("Step description too short")
        
        return {
            "steps_valid": len(issues) == 0,
            "issues": issues,
            "step_count": len(steps)
        }
    
    def _optimize_response_length(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize response to be concise like ChatGPT"""
        solution = response.get("solution", {})
        
        # Shorten issue description
        issue = solution.get("issue", "")
        if len(issue) > 100:
            issue = issue[:97] + "..."
        
        # Optimize steps to be more concise
        steps = solution.get("recommended_steps", [])
        optimized_steps = []
        
        for step in steps:
            description = step.get("description", "")
            # Keep descriptions under 80 characters for conciseness
            if len(description) > 80:
                description = description[:77] + "..."
            
            optimized_steps.append({
                "step_number": step.get("step_number", 1),
                "description": description
            })
        
        # Create optimized response
        optimized_solution = {
            **solution,
            "issue": issue,
            "recommended_steps": optimized_steps[:5]  # Limit to 5 steps max
        }
        
        return {
            **response,
            "solution": optimized_solution
        }
    
    async def perform_network_diagnostic(self, query: str) -> Dict[str, Any]:
        """Perform network diagnostics based on query"""
        query_lower = query.lower()
        results = {}
        
        try:
            # Determine which network tests to run
            if 'ping' in query_lower or 'connectivity' in query_lower:
                # Default ping test
                ping_result = await self.automation_service.execute_command("ping -c 4 8.8.8.8")
                results['ping_test'] = ping_result
            
            if 'dns' in query_lower:
                dns_result = await self.automation_service.execute_command("nslookup google.com")
                results['dns_test'] = dns_result
            
            if 'port' in query_lower or 'connection' in query_lower:
                netstat_result = await self.automation_service.execute_command("netstat -tuln")
                results['port_scan'] = netstat_result
            
            return {
                "diagnostic_type": "network",
                "results": results,
                "summary": self._generate_network_summary(results)
            }
            
        except Exception as e:
            return {
                "diagnostic_type": "network",
                "error": str(e),
                "summary": "Network diagnostic failed"
            }
    
    async def perform_system_diagnostic(self, query: str) -> Dict[str, Any]:
        """Perform system diagnostics based on query"""
        query_lower = query.lower()
        results = {}
        
        try:
            if 'cpu' in query_lower or 'performance' in query_lower:
                cpu_result = await self.automation_service.execute_command("cat /proc/cpuinfo | head -20")
                load_result = await self.automation_service.execute_command("uptime")
                results['cpu_info'] = cpu_result
                results['system_load'] = load_result
            
            if 'memory' in query_lower or 'ram' in query_lower:
                memory_result = await self.automation_service.execute_command("free -h")
                results['memory_info'] = memory_result
            
            if 'disk' in query_lower or 'storage' in query_lower:
                disk_result = await self.automation_service.execute_command("df -h")
                results['disk_usage'] = disk_result
            
            return {
                "diagnostic_type": "system",
                "results": results,
                "summary": self._generate_system_summary(results)
            }
            
        except Exception as e:
            return {
                "diagnostic_type": "system",
                "error": str(e),
                "summary": "System diagnostic failed"
            }
    
    def _generate_network_summary(self, results: Dict[str, Any]) -> str:
        """Generate concise network diagnostic summary"""
        summaries = []
        
        if 'ping_test' in results:
            ping_result = results['ping_test']
            if ping_result.get('success'):
                summaries.append("✓ Internet connectivity working")
            else:
                summaries.append("✗ Internet connectivity issues detected")
        
        if 'dns_test' in results:
            dns_result = results['dns_test']
            if dns_result.get('success'):
                summaries.append("✓ DNS resolution working")
            else:
                summaries.append("✗ DNS resolution problems")
        
        return " | ".join(summaries) if summaries else "Network diagnostic completed"
    
    def _generate_system_summary(self, results: Dict[str, Any]) -> str:
        """Generate concise system diagnostic summary"""
        summaries = []
        
        if 'memory_info' in results:
            summaries.append("Memory usage checked")
        
        if 'cpu_info' in results:
            summaries.append("CPU performance analyzed")
        
        if 'disk_usage' in results:
            summaries.append("Disk usage evaluated")
        
        return " | ".join(summaries) if summaries else "System diagnostic completed"

# Create singleton instance
validation_service = ValidationService()

def get_validation_service() -> ValidationService:
    """Get the validation service instance"""
    return validation_service
