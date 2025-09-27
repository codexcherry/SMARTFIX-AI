import os
import sys
import subprocess
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
logger = logging.getLogger(__name__)

# Track the gesture control process
gesture_process = None

class GestureControlResponse(BaseModel):
    success: bool
    message: str
    pid: Optional[int] = None


@router.post("/start-gesture-control", response_model=GestureControlResponse)
async def start_gesture_control(background_tasks: BackgroundTasks):
    """Start the gesture control system"""
    global gesture_process
    
    try:
        # Check if gesture control is already running
        if gesture_process is not None and gesture_process.poll() is None:
            return {
                "success": True,
                "message": "Gesture control is already running",
                "pid": gesture_process.pid
            }
            
        # Get the absolute path to the gesture_control.py script
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../gesture_control.py"))
        
        # Check if the script exists
        if not os.path.exists(script_path):
            raise HTTPException(status_code=404, detail=f"Gesture control script not found at {script_path}")
            
        # Start the gesture control process
        logger.info(f"Starting gesture control from {script_path}")
        
        # Use Python executable from the current environment
        python_executable = sys.executable
        
        # Start the process
        gesture_process = subprocess.Popen(
            [python_executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        # Define a background task to log output
        def log_output():
            for line in gesture_process.stdout:
                logger.info(f"Gesture control: {line.strip()}")
            for line in gesture_process.stderr:
                logger.error(f"Gesture control error: {line.strip()}")
                
        # Start the background task
        background_tasks.add_task(log_output)
        
        return {
            "success": True,
            "message": "Gesture control started successfully",
            "pid": gesture_process.pid
        }
        
    except Exception as e:
        logger.error(f"Error starting gesture control: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start gesture control: {str(e)}")


@router.post("/stop-gesture-control", response_model=GestureControlResponse)
async def stop_gesture_control():
    """Stop the gesture control system"""
    global gesture_process
    
    try:
        if gesture_process is None:
            return {
                "success": True,
                "message": "Gesture control is not running",
                "pid": None
            }
            
        # Check if the process is still running
        if gesture_process.poll() is None:
            # Process is running, terminate it
            gesture_process.terminate()
            try:
                # Wait for the process to terminate
                gesture_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate
                gesture_process.kill()
                
        pid = gesture_process.pid
        gesture_process = None
        
        return {
            "success": True,
            "message": "Gesture control stopped successfully",
            "pid": pid
        }
        
    except Exception as e:
        logger.error(f"Error stopping gesture control: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop gesture control: {str(e)}")


@router.get("/gesture-control-status", response_model=GestureControlResponse)
async def get_gesture_control_status():
    """Check if gesture control is running"""
    global gesture_process
    
    if gesture_process is None:
        return {
            "success": True,
            "message": "Gesture control is not running",
            "pid": None
        }
        
    # Check if the process is still running
    if gesture_process.poll() is None:
        return {
            "success": True,
            "message": "Gesture control is running",
            "pid": gesture_process.pid
        }
    else:
        # Process has terminated
        gesture_process = None
        return {
            "success": True,
            "message": "Gesture control has terminated",
            "pid": None
        }
