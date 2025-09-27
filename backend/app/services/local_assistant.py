"""
Local Assistant Service - Provides offline-first AI capabilities using local models
"""
import os
import sys
import logging
from typing import Dict, Any, List, Optional
import asyncio
import time

# Add the assistant directory to the path
assistant_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assistant")
if assistant_path not in sys.path:
    sys.path.append(assistant_path)

# Import the assistant API if available
try:
    from assistant.api_integration import get_assistant_api
    ASSISTANT_AVAILABLE = True
except ImportError:
    ASSISTANT_AVAILABLE = False
    get_assistant_api = None

from ..core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class LocalAssistantService:
    """Service for interacting with the local assistant"""
    
    def __init__(self):
        """Initialize the local assistant service"""
        self.assistant_api = None
        self.available = ASSISTANT_AVAILABLE
        
        if self.available and get_assistant_api:
            try:
                self.assistant_api = get_assistant_api()
                logger.info("Local assistant service initialized")
            except Exception as e:
                logger.error(f"Error initializing local assistant: {e}")
                self.available = False
        else:
            logger.info("Local assistant not available - using fallback mode")
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a query using the local assistant"""
        if not self.available or not self.assistant_api:
            logger.warning("Local assistant not available")
            return {
                "success": False,
                "error": "Local assistant not available",
                "fallback_to_online": True
            }
        
        try:
            start_time = time.time()
            result = await self.assistant_api.process_query(query, context)
            elapsed = time.time() - start_time
            
            logger.info(f"Local assistant processed query in {elapsed:.2f} seconds")
            
            # Add processing time to result
            result["processing_time"] = elapsed
            
            return result
        except Exception as e:
            logger.error(f"Error processing query with local assistant: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_to_online": True
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the local assistant"""
        if not self.available or not self.assistant_api:
            return {
                "available": False,
                "status": "unavailable",
                "error": "Local assistant not available"
            }
        
        try:
            status = await self.assistant_api.get_status()
            status["available"] = True
            return status
        except Exception as e:
            logger.error(f"Error getting local assistant status: {e}")
            return {
                "available": False,
                "status": "error",
                "error": str(e)
            }

# Create a singleton instance
local_assistant_service = LocalAssistantService()

def get_local_assistant_service() -> LocalAssistantService:
    """Get the local assistant service instance"""
    return local_assistant_service
