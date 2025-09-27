#!/usr/bin/env python
# run_assistant.py - Simple RAG-based Q&A system using the troubleshooting database
import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import logging
import sys
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
DB_PATH = os.path.join("data", "troubleshooting_solutions_1000plus.json")
INDEX_PATH = os.path.join("faiss_index", "troubleshoot.index")
META_PATH = os.path.join("faiss_index", "meta.json")

class TroubleshootingAssistant:
    def __init__(self):
        """Initialize the troubleshooting assistant"""
        self.load_resources()
    
    def load_resources(self):
        """Load the embedding model, FAISS index, and metadata"""
        logger.info("Loading embedding model...")
        self.emb_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        
        # Check if index exists
        if not os.path.exists(INDEX_PATH):
            logger.error(f"Index file not found: {INDEX_PATH}")
            logger.info("Please run build_index.py first to create the index")
            sys.exit(1)
        
        logger.info(f"Loading FAISS index from {INDEX_PATH}...")
        self.index = faiss.read_index(INDEX_PATH)
        
        logger.info(f"Loading metadata from {META_PATH}...")
        with open(META_PATH, "r", encoding="utf-8") as f:
            self.meta = json.load(f)
        
        logger.info(f"Assistant ready with {len(self.meta)} solutions in knowledge base")
    
    def embed(self, query):
        """Embed a query using the embedding model"""
        vector = self.emb_model.encode([query], convert_to_numpy=True)[0]
        vector = vector / np.linalg.norm(vector)  # Normalize for cosine similarity
        return vector.astype("float32").reshape(1, -1)
    
    def retrieve(self, query, k=5):
        """Retrieve the top k most relevant solutions for a query"""
        vector = self.embed(query)
        scores, indices = self.index.search(vector, k)
        
        hits = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.meta):  # Ensure valid index
                m = self.meta[idx]
                hits.append((float(score), m))
        
        return hits
    
    def answer_from_hits(self, query, hits):
        """Generate an answer from the retrieved hits"""
        if not hits:
            return "I couldn't find any relevant solutions for your problem."
        
        lines = [f"Query: {query}", "\nTop suggestions:"]
        
        for i, (score, m) in enumerate(hits, 1):
            # Format confidence and success rate as percentages
            confidence = f"{m.get('confidence_score', 0) * 100:.0f}%"
            success_rate = f"{m.get('success_rate', 0) * 100:.0f}%"
            
            # Format solution steps
            steps = "\n  - " + "\n  - ".join(m.get("solution_steps", []))
            
            # Format error codes if available
            error_codes = ""
            if m.get("error_codes"):
                error_codes = f"\nError codes: {', '.join(m.get('error_codes', []))}"
            
            lines.append(
                f"\n[{i}] [{m.get('device_category', 'unknown')} / {m.get('problem_type', 'general')}] "
                f"{m.get('problem_text', '')}"
                f"\nSymptoms: {m.get('symptoms', 'Not specified')}"
                f"{error_codes}"
                f"\nConfidence: {confidence}, Success rate: {success_rate}"
                f"\nSolution:{steps}"
            )
        
        return "\n".join(lines)
    
    def process_query(self, query, k=5):
        """Process a user query and return an answer"""
        start_time = time.time()
        hits = self.retrieve(query, k=k)
        answer = self.answer_from_hits(query, hits)
        elapsed = time.time() - start_time
        
        logger.info(f"Query processed in {elapsed:.2f} seconds")
        return answer

def main():
    """Main function to run the assistant"""
    assistant = TroubleshootingAssistant()
    
    print("\n" + "="*50)
    print("SmartFix AI Troubleshooting Assistant")
    print("="*50)
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
