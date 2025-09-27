#!/usr/bin/env python3
"""
SmartFix-AI Backend - Main Entry Point
A comprehensive AI-powered troubleshooting assistant backend
"""

import os
import sys
import uvicorn

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    # Import the app directly to avoid multiprocessing issues
    try:
        from app.main import app
        print("✓ App imported successfully")
    except Exception as e:
        print(f"✗ Error importing app: {e}")
        sys.exit(1)
    
    # Run with minimal multiprocessing
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to avoid multiprocessing issues
        log_level="info",
        workers=1,
        loop="asyncio"
    )
