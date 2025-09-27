#!/usr/bin/env python
# llm_assistant.py - Enhanced assistant with local LLM for natural dialog and reasoning
import os
import sys
import json
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

# Suppress FAISS warnings about AVX support
import warnings
warnings.filterwarnings("ignore", message=".*AVX.*")

import faiss
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
ASSISTANT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ASSISTANT_DIR, "data", "troubleshooting_solutions_1000plus.json")
INDEX_PATH = os.path.join(ASSISTANT_DIR, "faiss_index", "troubleshoot.index")
META_PATH = os.path.join(ASSISTANT_DIR, "faiss_index", "meta.json")
LLM_MODEL_PATH = os.path.join(ASSISTANT_DIR, "models", "llama-3-8b-instruct.gguf")

class LLMAssistant:
    """Enhanced assistant with local LLM for natural dialog and reasoning"""
    
    def __init__(self):
        """Initialize the LLM assistant"""
        self.load_resources()
        self.conversation_history = []
        self.llm_available = self._check_llm_available()
    
    def load_resources(self):
        """Load the embedding model, FAISS index, and metadata"""
        logger.info("Loading embedding model...")
        self.emb_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        
        # Check if index exists
        if not os.path.exists(INDEX_PATH):
            logger.error(f"Index file not found: {INDEX_PATH}")
            logger.info("Please run build_index.py first to create the index")
            # Don't exit, just set a flag to indicate the index is missing
            self.index_available = False
            return
            
        self.index_available = True
        
        logger.info(f"Loading FAISS index from {INDEX_PATH}...")
        self.index = faiss.read_index(INDEX_PATH)
        
        logger.info(f"Loading metadata from {META_PATH}...")
        with open(META_PATH, "r", encoding="utf-8") as f:
            self.meta = json.load(f)
        
        logger.info(f"Assistant ready with {len(self.meta)} solutions in knowledge base")
    
    def _check_llm_available(self) -> bool:
        """Check if the LLM is available and load it if possible"""
        try:
            if not os.path.exists(LLM_MODEL_PATH):
                logger.info("LLM model not configured - Running in RAG-only mode (offline search only)")
                return False
            
            logger.info("Loading LLM model...")
            from llama_cpp import Llama
            
            self.llm = Llama(
                model_path=LLM_MODEL_PATH,
                n_ctx=4096,
                n_threads=4,
                n_batch=512
            )
            logger.info("LLM loaded successfully")
            return True
            
        except ImportError:
            logger.warning("llama-cpp-python not installed. Running in RAG-only mode.")
            return False
        except Exception as e:
            logger.error(f"Error loading LLM: {e}")
            return False
    
    def embed(self, query: str) -> np.ndarray:
        """Embed a query using the embedding model"""
        vector = self.emb_model.encode([query], convert_to_numpy=True)[0]
        vector = vector / np.linalg.norm(vector)  # Normalize for cosine similarity
        return vector.astype("float32").reshape(1, -1)
    
    def retrieve(self, query: str, k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        """Retrieve the top k most relevant solutions for a query"""
        # Check if index is available
        if not hasattr(self, 'index_available') or not self.index_available:
            logger.warning("Index not available, returning empty results")
            return []
            
        vector = self.embed(query)
        scores, indices = self.index.search(vector, k)
        
        hits = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.meta):  # Ensure valid index
                m = self.meta[idx]
                hits.append((float(score), m))
        
        return hits
    
    def format_rag_response(self, query: str, hits: List[Tuple[float, Dict[str, Any]]]) -> str:
        """Generate a RAG-based response from the retrieved hits"""
        if not hits:
            return "I couldn't find any relevant solutions for your problem."
        
        # Get the best match
        best_score, best_match = hits[0]
        
        # Format confidence as percentage
        confidence = f"{best_match.get('confidence_score', 0) * 100:.0f}%"
        
        # Get solution steps
        solution_steps = best_match.get("solution_steps", [])
        
        # Create a concise response
        response = (
            f"I've found a solution for your issue with {best_match.get('problem_text', 'your device')}.\n\n"
            f"Most common symptoms: {best_match.get('symptoms', 'Various issues')}\n"
            f"Confidence: {confidence}\n\n"
            f"Here are the recommended steps to fix it:"
        )
        
        # Return only the response text - the solution steps will be returned separately
        return response
    
    def synthesize_llm_response(self, query: str, hits: List[Tuple[float, Dict[str, Any]]]) -> str:
        """Generate a response using the LLM based on retrieved context"""
        if not self.llm_available or not hits:
            return self.format_rag_response(query, hits)
        
        # Build context from top hits
        context = ""
        for i, (score, m) in enumerate(hits[:3], 1):
            context += f"\n### Doc {i}\n"
            context += f"Problem: {m.get('problem_text', '')}\n"
            context += f"Device: {m.get('device_category', '')} | Type: {m.get('problem_type', '')}\n"
            context += f"Symptoms: {m.get('symptoms', '')}\n"
            
            if m.get("error_codes"):
                context += f"Error codes: {', '.join(m.get('error_codes', []))}\n"
            
            context += f"Steps: \n"
            for j, step in enumerate(m.get("solution_steps", []), 1):
                context += f"{j}. {step}\n"
            
            context += f"Confidence: {m.get('confidence_score', 0)}, Success rate: {m.get('success_rate', 0)}\n"
        
        # Build prompt with conversation history
        history_context = ""
        if self.conversation_history:
            history_context = "Previous conversation:\n"
            for turn in self.conversation_history[-3:]:  # Last 3 turns
                history_context += f"User: {turn['user']}\n"
                history_context += f"Assistant: {turn['assistant']}\n"
        
        # Create the prompt
        prompt = f"""You are a technical troubleshooting assistant for SmartFix AI. Use ONLY the information in the CONTEXT section to help solve the user's problem. If you don't have enough information, ask clarifying questions.

{history_context}

CONTEXT:
{context}

User issue: {query}

Respond with a friendly, helpful answer. Include numbered steps for solutions. If multiple solutions are possible, explain which one to try first and why. If you need more information to diagnose the problem correctly, ask 1-2 specific questions.
"""
        
        # Generate response
        try:
            output = self.llm(
                prompt=prompt,
                max_tokens=512,
                temperature=0.2,
                top_p=0.9,
                stop=["</s>", "User:", "CONTEXT:"],
                echo=False
            )
            response = output["choices"][0]["text"].strip()
            return response
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return self.format_rag_response(query, hits)
    
    def process_query(self, query: str, k: int = 5) -> str:
        """Process a user query and return an answer"""
        start_time = time.time()
        
        # Check if index is available
        if not hasattr(self, 'index_available') or not self.index_available:
            logger.warning("Index not available, returning fallback response")
            return "I'm sorry, but my knowledge base is currently unavailable. Please make sure the index has been built by running build_index.py."
        
        # Retrieve relevant solutions
        hits = self.retrieve(query, k=k)
        
        # Generate response
        if self.llm_available:
            answer = self.synthesize_llm_response(query, hits)
        else:
            answer = self.format_rag_response(query, hits)
        
        # Update conversation history
        self.conversation_history.append({
            "user": query,
            "assistant": answer
        })
        
        elapsed = time.time() - start_time
        logger.info(f"Query processed in {elapsed:.2f} seconds")
        
        return answer

def main():
    """Main function to run the LLM assistant"""
    assistant = LLMAssistant()
    
    print("\n" + "="*50)
    print("SmartFix AI LLM-Enhanced Troubleshooting Assistant")
    print("="*50)
    if assistant.llm_available:
        print("Running with local LLM for enhanced responses")
    else:
        print("Running in RAG-only mode (no LLM)")
    print("Ask a troubleshooting question (type 'exit' to quit)")
    print("="*50 + "\n")
    
    while True:
        query = input("\nYou: ").strip()
        if query.lower() in ("exit", "quit", "bye"):
            print("\nThank you for using SmartFix AI. Goodbye!")
            break
        
        if not query:
            continue
        
        answer = assistant.process_query(query)
        print("\nAssistant:\n" + answer)

if __name__ == "__main__":
    main()
