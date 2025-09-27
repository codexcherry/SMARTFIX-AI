from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Pydantic models
class AssistantQuery(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class AssistantResponse(BaseModel):
    success: bool
    query: str
    answer: str
    solution_steps: Optional[List[str]] = None
    confidence: Optional[float] = None
    offline_mode: bool = True
    error: Optional[str] = None

class AssistantStatus(BaseModel):
    status: str
    llm_available: bool
    knowledge_base_size: int
    offline_mode: bool

# Mock responses for testing the frontend integration
@router.post("/local", response_model=AssistantResponse)
async def query_local_assistant(query: AssistantQuery):
    """
    Query the local AI assistant (simplified mock version)
    """
    try:
        # Log the query
        logger.info(f"Received query: {query.query}")
        
        # Create a mock response
        mock_answer = f"I understand you're asking about: {query.query}. Here's what I can tell you about this issue."
        
        # Add some mock solution steps
        solution_steps = [
            "Check if the device is properly connected",
            "Ensure all drivers are up to date",
            "Try restarting the system",
            "If the problem persists, check for hardware issues"
        ]
        
        return {
            "success": True,
            "query": query.query,
            "answer": mock_answer,
            "solution_steps": solution_steps,
            "confidence": 0.85,
            "offline_mode": True
        }
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return {
            "success": False,
            "query": query.query,
            "answer": "Sorry, I encountered an error processing your query.",
            "error": str(e),
            "offline_mode": True
        }

@router.get("/status", response_model=AssistantStatus)
async def get_assistant_status():
    """
    Get the status of the local AI assistant (simplified mock version)
    """
    return {
        "status": "ready",
        "llm_available": True,
        "knowledge_base_size": 1000,
        "offline_mode": True
    }
