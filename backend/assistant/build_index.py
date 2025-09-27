#!/usr/bin/env python
# build_index.py - Creates a FAISS vector index from troubleshooting database
import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
DB_PATH = os.path.join("data", "troubleshooting_solutions_1000plus.json")
INDEX_PATH = os.path.join("faiss_index", "troubleshoot.index")
EMB_PATH = os.path.join("faiss_index", "embeddings.npy")
META_PATH = os.path.join("faiss_index", "meta.json")

def main():
    logger.info("Loading embedding model...")
    # Small but effective model that can run offline after first download
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    logger.info(f"Loading troubleshooting database from {DB_PATH}...")
    with open(DB_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)
    
    logger.info(f"Processing {len(records)} troubleshooting records...")
    texts = []
    meta = []
    
    for i, record in enumerate(records):
        # Combine useful fields for retrieval
        chunk = f"{record.get('device_category', '')} | {record.get('problem_type', '')}\n" \
                f"Problem: {record.get('problem_text', '')}\n" \
                f"Symptoms: {record.get('symptoms', '')}\n" \
                f"Error codes: {', '.join(record.get('error_codes', []))}"
        
        texts.append(chunk)
        meta.append({
            "idx": i,
            "problem_text": record.get("problem_text"),
            "solution_steps": record.get("solution_steps", []),
            "device_category": record.get("device_category"),
            "problem_type": record.get("problem_type"),
            "confidence_score": record.get("confidence_score"),
            "success_rate": record.get("success_rate"),
            "symptoms": record.get("symptoms", ""),
            "error_codes": record.get("error_codes", [])
        })
    
    logger.info(f"Generating embeddings for {len(texts)} texts...")
    embeddings = model.encode(
        texts, 
        batch_size=32, 
        convert_to_numpy=True, 
        show_progress_bar=True
    )
    
    # Normalize embeddings for cosine similarity
    logger.info("Normalizing embeddings...")
    embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    # Create and save FAISS index
    logger.info("Creating FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings_norm.astype("float32"))
    
    logger.info(f"Saving index to {INDEX_PATH}...")
    faiss.write_index(index, INDEX_PATH)
    
    logger.info(f"Saving embeddings to {EMB_PATH}...")
    np.save(EMB_PATH, embeddings_norm)
    
    logger.info(f"Saving metadata to {META_PATH}...")
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Index built successfully with {len(meta)} items")
    logger.info(f"Index dimension: {dimension}")

if __name__ == "__main__":
    main()
