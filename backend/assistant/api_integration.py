#!/usr/bin/env python
# api_integration.py - Integration with FastAPI backend
import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional

# Add the assistant directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the LLM assistant
from assistant.llm_assistant import LLMAssistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AssistantAPI:
    """API integration for the SmartFix AI assistant"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance is created"""
        if cls._instance is None:
            cls._instance = super(AssistantAPI, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the assistant API"""
        if self._initialized:
            return
        
        logger.info("Initializing Assistant API...")
        self.assistant = LLMAssistant()
        self._initialized = True
        logger.info("Assistant API initialized")
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a query and return the response"""
        try:
            # Enhance query with context if provided
            enhanced_query = query
            if context:
                device_info = context.get("device_info", {})
                if device_info:
                    device_type = device_info.get("type", "")
                    os_info = device_info.get("os", "")
                    if device_type or os_info:
                        enhanced_query = f"{query} [Device: {device_type}, OS: {os_info}]"
            
            # Process the query
            answer = self.assistant.process_query(enhanced_query)
            
            # Get the top hit for solution steps and confidence
            hits = self.assistant.retrieve(enhanced_query, k=1)
            
            solution_steps = []
            confidence = 0.0
            
            if hits:
                _, meta = hits[0]
                # Get solution steps directly from the metadata
                solution_steps = meta.get('solution_steps', [])
                confidence = meta.get('confidence_score', 0.0)
            
            # If no solution steps were found in metadata, try to extract from answer
            if not solution_steps:
                for line in answer.split('\n'):
                    if line.strip().startswith('-') or (line.strip() and line.strip()[0].isdigit() and '.' in line[:3]):
                        solution_steps.append(line.strip().lstrip('- ').lstrip('0123456789. '))
            
            # Limit to top 5 most important steps for better UX
            if len(solution_steps) > 5:
                solution_steps = solution_steps[:5]
            
            return {
                "success": True,
                "query": query,
                "answer": answer,
                "solution_steps": solution_steps,
                "confidence": confidence,
                "offline_mode": True
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "offline_mode": True
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the assistant"""
        return {
            "status": "ready" if self._initialized else "initializing",
            "llm_available": self.assistant.llm_available if self._initialized else False,
            "knowledge_base_size": len(self.assistant.meta) if self._initialized else 0,
            "offline_mode": True
        }

# Create a global instance
assistant_api = AssistantAPI()

def get_assistant_api() -> AssistantAPI:
    """Get the assistant API instance"""
    return assistant_api
