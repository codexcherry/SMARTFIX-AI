# huggingface_service.py (enhanced)
import requests
import aiohttp
from typing import Dict, List, Any, Optional, Union
import json
import base64
import asyncio

from ..core.config import settings

class HuggingFaceService:
    def __init__(self, api_key: str = settings.HUGGINGFACE_API_KEY):
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.base_url = "https://api-inference.huggingface.co/models"
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    
    async def text_summarization(self, text: str) -> str:
        """Summarize text using Hugging Face model"""
        model_id = "facebook/bart-large-cnn"
        api_url = f"{self.base_url}/{model_id}"
        
        payload = {
            "inputs": text[:1024],  # Limit input size
            "parameters": {
                "max_length": 100,
                "min_length": 30,
                "do_sample": False
            }
        }
        
        try:
            session = await self._get_session()
            async with session.post(api_url, json=payload) as response:
                response.raise_for_status()
                result = await response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("summary_text", "")
                return ""
        except Exception as e:
            print(f"Error in text_summarization: {e}")
            return ""
    
    async def image_to_text(self, image_data: bytes) -> str:
        """Extract text from image using Hugging Face model"""
        model_id = "Salesforce/blip-image-captioning-large"
        api_url = f"{self.base_url}/{model_id}"
        
        try:
            session = await self._get_session()
            async with session.post(api_url, data=image_data) as response:
                response.raise_for_status()
                result = await response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
                return result.get("generated_text", "")
        except Exception as e:
            print(f"Error in image_to_text: {e}")
            return ""
    
    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text using Hugging Face model"""
        model_id = "sentence-transformers/all-MiniLM-L6-v2"
        api_url = f"{self.base_url}/{model_id}"
        
        payload = {
            "inputs": text[:512]  # Limit input size
        }
        
        try:
            session = await self._get_session()
            async with session.post(api_url, json=payload) as response:
                response.raise_for_status()
                result = await response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]
                return []
        except Exception as e:
            print(f"Error in generate_embeddings: {e}")
            return []
    
    async def rank_solutions(self, issue: str, solutions: List[str]) -> List[Dict[str, Any]]:
        """Rank solutions based on relevance to the issue"""
        if not solutions:
            return []
        
        try:
            ranked_solutions = []
            
            # Use a zero-shot classification model
            model_id = "facebook/bart-large-mnli"
            api_url = f"{self.base_url}/{model_id}"
            
            for solution in solutions:
                payload = {
                    "inputs": solution,
                    "parameters": {
                        "candidate_labels": [f"relevant to {issue}", "not relevant"]
                    }
                }
                
                try:
                    session = await self._get_session()
                    async with session.post(api_url, json=payload) as response:
                        response.raise_for_status()
                        result = await response.json()
                        
                        # Get score for the "relevant" label
                        scores = result.get("scores", [0.5, 0.5])
                        labels = result.get("labels", ["relevant", "not relevant"])
                        
                        relevant_idx = 0
                        for i, label in enumerate(labels):
                            if "relevant" in label.lower():
                                relevant_idx = i
                                break
                        
                        score = scores[relevant_idx]
                        
                        ranked_solutions.append({
                            "solution": solution,
                            "score": score
                        })
                except Exception as e:
                    print(f"Error ranking solution '{solution[:20]}...': {e}")
                    ranked_solutions.append({
                        "solution": solution,
                        "score": 0.5  # Default score
                    })
            
            # Sort by score in descending order
            ranked_solutions.sort(key=lambda x: x["score"], reverse=True)
            return ranked_solutions
        
        except Exception as e:
            print(f"Error in rank_solutions: {e}")
            return [{"solution": s, "score": 0.5} for s in solutions]