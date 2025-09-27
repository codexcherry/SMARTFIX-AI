import requests
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
import json
from concurrent.futures import ThreadPoolExecutor

from ..core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class SerpAPIService:
    """Enhanced SerpAPI Service with advanced validation and error analysis capabilities"""
    
    def __init__(self, api_key: str = settings.SERPAPI_KEY):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
        
        # Common error patterns for validation
        self.error_patterns = {
            "sql_connection": [
                r"cannot\s+connect\s+to\s+(\w+)\s*server",
                r"sql\s+server\s+connection\s+error",
                r"network-related\s+or\s+instance-specific\s+error",
                r"named\s+pipes\s+provider",
                r"error\s+\d+",
            ],
            "network_error": [
                r"network\s+error",
                r"connection\s+failed",
                r"cannot\s+connect",
                r"no\s+internet",
                r"wifi\s+issue",
            ],
            "display_error": [
                r"monitor\s+not\s+detected",
                r"display\s+driver",
                r"graphics\s+card",
                r"screen\s+resolution",
                r"no\s+signal",
            ],
            "audio_error": [
                r"no\s+sound",
                r"audio\s+not\s+working",
                r"speaker\s+issue",
                r"volume\s+problem",
                r"muted",
            ]
        }
        
        # Error message templates for common issues
        self.error_templates = {
            "sql_connection": {
                "issue": "SQL Server Connection Error",
                "possible_causes": [
                    "Server name is incorrect or server is offline",
                    "Network connectivity issues",
                    "SQL Server configuration problem",
                    "Firewall blocking connection"
                ],
                "confidence_score": 0.9
            },
            "network_error": {
                "issue": "Network Connectivity Problem",
                "possible_causes": [
                    "Router/modem issues",
                    "ISP service disruption",
                    "Network adapter problems",
                    "Incorrect network configuration"
                ],
                "confidence_score": 0.85
            },
            "display_error": {
                "issue": "Display/Monitor Connection Issue",
                "possible_causes": [
                    "Cable connection problem",
                    "Graphics driver issues",
                    "Incompatible resolution settings",
                    "Hardware failure"
                ],
                "confidence_score": 0.8
            },
            "audio_error": {
                "issue": "Audio/Sound Problem",
                "possible_causes": [
                    "Muted audio",
                    "Audio driver issues",
                    "Incorrect audio output selection",
                    "Hardware failure"
                ],
                "confidence_score": 0.8
            }
        }
    
    async def search_solutions(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Search for solutions to a technical issue using SerpAPI with enhanced validation"""
        search_query = f"how to fix {query}"
        
        params = {
            "q": search_query,
            "api_key": self.api_key,
            "engine": "google",
            "num": str(num_results * 2),  # Request more results for better filtering
            "gl": "us",  # Country to search from
            "hl": "en"   # Language
        }
        
        try:
            logger.info(f"Searching for solutions: {search_query}")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            results = response.json()
            
            organic_results = results.get("organic_results", [])
            
            # Score and rank results based on relevance to query
            scored_results = []
            for result in organic_results:
                relevance_score = self._calculate_relevance_score(query, result)
                scored_results.append((relevance_score, result))
            
            # Sort by relevance score (highest first)
            scored_results.sort(reverse=True)
            
            # Format and return top results
            formatted_results = []
            for _, result in scored_results[:num_results]:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "url": result.get("link", ""),
                    "source": result.get("source", "web search"),
                    "relevance_score": self._calculate_relevance_score(query, result)
                })
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error in search_solutions: {e}")
            return []
            
    def _calculate_relevance_score(self, query: str, result: Dict[str, Any]) -> float:
        """Calculate relevance score of search result to query"""
        score = 0.0
        query_terms = set(query.lower().split())
        
        # Check title relevance
        title = result.get("title", "").lower()
        title_words = set(title.split())
        title_match_ratio = len(query_terms.intersection(title_words)) / max(len(query_terms), 1)
        score += title_match_ratio * 0.5  # Title matches are important
        
        # Check snippet relevance
        snippet = result.get("snippet", "").lower()
        for term in query_terms:
            if term in snippet:
                score += 0.1
        
        # Bonus for exact phrase match
        if query.lower() in title.lower() or query.lower() in snippet.lower():
            score += 0.3
            
        # Check for solution-oriented content
        solution_terms = ["how to", "fix", "solve", "troubleshoot", "repair", "solution"]
        for term in solution_terms:
            if term in title.lower() or term in snippet.lower():
                score += 0.1
                
        return min(score, 1.0)  # Cap at 1.0
    
    async def search_product_info(self, product_name: str) -> Dict[str, Any]:
        """Search for product information using SerpAPI"""
        search_query = f"{product_name} technical specifications"
        
        params = {
            "q": search_query,
            "api_key": self.api_key,
            "engine": "google",
            "num": "3",
            "gl": "us",
            "hl": "en"
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            results = response.json()
            
            knowledge_graph = results.get("knowledge_graph", {})
            if knowledge_graph:
                return {
                    "title": knowledge_graph.get("title", product_name),
                    "description": knowledge_graph.get("description", ""),
                    "attributes": knowledge_graph.get("attributes", {})
                }
            
            # Fallback to organic results if no knowledge graph
            organic_results = results.get("organic_results", [])
            if organic_results:
                return {
                    "title": product_name,
                    "description": organic_results[0].get("snippet", ""),
                    "url": organic_results[0].get("link", "")
                }
            
            return {
                "title": product_name,
                "description": "No information found",
                "url": ""
            }
        
        except Exception as e:
            print(f"Error in search_product_info: {e}")
            return {
                "title": product_name,
                "description": "Error retrieving product information",
                "url": ""
            }
    
    async def analyze_error_message(self, error_text: str, image_ocr_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze error message text and identify the type of error
        with specialized error pattern matching
        """
        combined_text = error_text.lower()
        if image_ocr_text:
            combined_text += " " + image_ocr_text.lower()
        
        # Check for SQL connection errors (high priority based on screenshot)
        if any(re.search(pattern, combined_text, re.IGNORECASE) for pattern in self.error_patterns["sql_connection"]):
            error_type = "sql_connection"
            template = self.error_templates[error_type].copy()
            
            # Extract specific details from the error message
            server_name_match = re.search(r"to\s+([A-Za-z0-9_\-\.\\]+)", combined_text)
            error_code_match = re.search(r"error\s+(\d+)", combined_text)
            
            # Enhance template with specific details
            if server_name_match:
                template["server_name"] = server_name_match.group(1)
            if error_code_match:
                template["error_code"] = error_code_match.group(1)
                
            # Add specific solution steps for SQL connection errors
            template["recommended_steps"] = [
                {"step_number": 1, "description": "Verify the server name is correct and the server is running"},
                {"step_number": 2, "description": "Check network connectivity between client and server"},
                {"step_number": 3, "description": "Ensure SQL Server is configured to allow remote connections"},
                {"step_number": 4, "description": "Check firewall settings to allow SQL traffic (port 1433)"},
                {"step_number": 5, "description": "Verify SQL Server credentials are correct"}
            ]
            
            return {
                "error_type": error_type,
                "analysis": template,
                "confidence_score": 0.95  # High confidence for SQL errors
            }
            
        # Check for display/monitor errors
        elif any(re.search(pattern, combined_text, re.IGNORECASE) for pattern in self.error_patterns["display_error"]):
            error_type = "display_error"
            template = self.error_templates[error_type].copy()
            
            # Add specific solution steps for display errors
            template["recommended_steps"] = [
                {"step_number": 1, "description": "Check cable connections between computer and monitor"},
                {"step_number": 2, "description": "Try different ports (HDMI, DisplayPort, VGA)"},
                {"step_number": 3, "description": "Update graphics drivers to the latest version"},
                {"step_number": 4, "description": "Press Windows+P to check display projection settings"},
                {"step_number": 5, "description": "Test with a different monitor if available"}
            ]
            
            return {
                "error_type": error_type,
                "analysis": template,
                "confidence_score": 0.9
            }
            
        # Check for audio errors
        elif any(re.search(pattern, combined_text, re.IGNORECASE) for pattern in self.error_patterns["audio_error"]):
            error_type = "audio_error"
            template = self.error_templates[error_type].copy()
            
            # Add specific solution steps for audio errors
            template["recommended_steps"] = [
                {"step_number": 1, "description": "Check if TV is muted - press mute button"},
                {"step_number": 2, "description": "Verify volume is turned up using TV remote"},
                {"step_number": 3, "description": "Check audio output settings in TV menu"},
                {"step_number": 4, "description": "Ensure external devices are properly connected"},
                {"step_number": 5, "description": "Test with different speakers or headphones"}
            ]
            
            return {
                "error_type": error_type,
                "analysis": template,
                "confidence_score": 0.85
            }
            
        # Check for network errors
        elif any(re.search(pattern, combined_text, re.IGNORECASE) for pattern in self.error_patterns["network_error"]):
            error_type = "network_error"
            template = self.error_templates[error_type].copy()
            
            # Add specific solution steps for network errors
            template["recommended_steps"] = [
                {"step_number": 1, "description": "Check ISP connection status"},
                {"step_number": 2, "description": "Restart modem and router"},
                {"step_number": 3, "description": "Verify network cables are properly connected"},
                {"step_number": 4, "description": "Reset network adapter on your device"},
                {"step_number": 5, "description": "Contact ISP support if problem persists"}
            ]
            
            return {
                "error_type": error_type,
                "analysis": template,
                "confidence_score": 0.85
            }
        
        # Fallback to generic error analysis with web search
        else:
            # Use web search to find potential solutions
            return await self._fallback_error_analysis(error_text)
    
    async def search_error_code(self, error_code: str, device_type: Optional[str] = None) -> List[Dict[str, str]]:
        """Search for information about a specific error code with enhanced validation"""
        search_query = f"{error_code} {device_type if device_type else ''} error code fix"
        
        params = {
            "q": search_query,
            "api_key": self.api_key,
            "engine": "google",
            "num": "10",  # Get more results for better filtering
            "gl": "us",
            "hl": "en"
        }
        
        try:
            logger.info(f"Searching for error code: {error_code}")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            results = response.json()
            
            organic_results = results.get("organic_results", [])
            
            # Score and filter results based on relevance to error code
            scored_results = []
            for result in organic_results:
                # Check if the error code appears in the result
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                
                # Calculate score based on exact error code match
                score = 0.0
                if error_code in title:
                    score += 0.6
                if error_code in snippet:
                    score += 0.4
                    
                # Boost score for solution-oriented content
                solution_terms = ["fix", "solve", "solution", "resolve", "troubleshoot"]
                for term in solution_terms:
                    if term in title.lower() or term in snippet.lower():
                        score += 0.1
                
                # Include device type in scoring if provided
                if device_type and (device_type.lower() in title.lower() or device_type.lower() in snippet.lower()):
                    score += 0.2
                
                scored_results.append((score, result))
            
            # Sort by relevance score
            scored_results.sort(reverse=True)
            
            # Format and return top results
            formatted_results = []
            for score, result in scored_results[:5]:
                if score > 0.2:  # Only include reasonably relevant results
                    formatted_results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "url": result.get("link", ""),
                        "relevance_score": score
                    })
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error in search_error_code: {e}")
            return []
            
    async def _fallback_error_analysis(self, error_text: str) -> Dict[str, Any]:
        """Fallback error analysis when specific patterns don't match"""
        # Search for solutions online
        search_results = await self.search_solutions(error_text, num_results=3)
        
        # Create generic analysis
        generic_analysis = {
            "issue": "Unidentified Technical Issue",
            "possible_causes": [
                "Software configuration problem",
                "Hardware compatibility issue",
                "System resource limitation",
                "Corrupted system files"
            ],
            "recommended_steps": [
                {"step_number": 1, "description": "Restart the affected application"},
                {"step_number": 2, "description": "Update to the latest software version"},
                {"step_number": 3, "description": "Check system requirements"},
                {"step_number": 4, "description": "Run system diagnostics"},
                {"step_number": 5, "description": "Contact technical support"}
            ],
            "confidence_score": 0.5,
            "external_sources": search_results
        }
        
        return {
            "error_type": "generic",
            "analysis": generic_analysis,
            "confidence_score": 0.5
        }
