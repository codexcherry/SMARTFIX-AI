import numpy as np
import time
import threading
import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import psutil
import subprocess
import platform

# Optional imports for gesture control
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    mp = None

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None

# Windows-specific audio control imports
try:
    if platform.system() == "Windows":
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        WINDOWS_AUDIO_AVAILABLE = True
    else:
        WINDOWS_AUDIO_AVAILABLE = False
except ImportError:
    WINDOWS_AUDIO_AVAILABLE = False

logger = logging.getLogger(__name__)

class GestureControlService:
    """
    Backend Gesture Control Service for SmartFix-AI
    Automatically activates when mouse is not working or after 15 seconds of inactivity
    """
    
    def __init__(self):
        self.is_active = False
        self.is_running = False
        self.auto_activate = True
        self.inactivity_threshold = 15  # seconds
        self.last_mouse_activity = time.time()
        self.mouse_check_interval = 1  # seconds
        
        # Check if required dependencies are available
        self.dependencies_available = CV2_AVAILABLE and MEDIAPIPE_AVAILABLE and PYAUTOGUI_AVAILABLE
        
        if not self.dependencies_available:
            logger.warning("Gesture control dependencies not available. Service will run in limited mode.")
            self.audio_available = False
            self.screen_width, self.screen_height = 1920, 1080  # Default values
            return
        
        # Initialize audio control
        try:
            if WINDOWS_AUDIO_AVAILABLE:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume = cast(interface, POINTER(IAudioEndpointVolume))
                vol_range = self.volume.GetVolumeRange()
                self.min_vol, self.max_vol = vol_range[0], vol_range[1]
                self.audio_available = True
            else:
                self.audio_available = False
                self.volume = None
                self.min_vol, self.max_vol = -65.25, 0.0
        except Exception as e:
            logger.warning(f"Audio initialization error: {e}")
            self.volume = None
            self.min_vol, self.max_vol = -65.25, 0.0
            self.audio_available = False

        # Prevent mouse from going to screen corners
        if PYAUTOGUI_AVAILABLE:
            pyautogui.FAILSAFE = False
            pyautogui.MINIMUM_DURATION = 0
            pyautogui.PAUSE = 0.01
            self.screen_width, self.screen_height = pyautogui.size()
        else:
            self.screen_width, self.screen_height = 1920, 1080

        # Initialize MediaPipe Hand and Face tracking
        if MEDIAPIPE_AVAILABLE:
            self.mp_hands = mp.solutions.hands
            self.mp_face_mesh = mp.solutions.face_mesh
            self.hands = self.mp_hands.Hands(
                max_num_hands=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            )
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.mp_draw = mp.solutions.drawing_utils
        else:
            self.mp_hands = None
            self.mp_face_mesh = None
            self.hands = None
            self.face_mesh = None
            self.mp_draw = None

        # Initialize camera
        self.cam = None

        # Initialize smoothing variables
        self.smoothing = 0.5
        self.prev_x, self.prev_y = self.screen_width/2, self.screen_height/2

        # Initialize gesture tracking
        self.scroll_cooldown = 0
        self.SCROLL_COOLDOWN_TIME = 0.2
        self.SCROLL_AMOUNT = 50

        # Initialize eye blink detection
        self.BLINK_THRESHOLD = 0.25
        self.last_blink_time = time.time()
        self.MIN_BLINK_INTERVAL = 0.3
        self.last_ear = 1.0

        # Hand height range for click detection
        self.HAND_HEIGHT_MIN = 0.2
        self.HAND_HEIGHT_MAX = 0.6

        # Status variables
        self.show_ui_guides = True
        self.show_debug = True
        self.gesture_thread = None
        self.monitor_thread = None
        
        # SmartFix-AI UI elements
        self.ui_elements = {
            "assistant": {"x": self.screen_width * 0.5, "y": self.screen_height * 0.3},
            "voice_assistant": {"x": self.screen_width * 0.7, "y": self.screen_height * 0.3},
            "device_analyzer": {"x": self.screen_width * 0.3, "y": self.screen_height * 0.3},
            "text_processing": {"x": self.screen_width * 0.5, "y": self.screen_height * 0.6},
            "image_analysis": {"x": self.screen_width * 0.7, "y": self.screen_height * 0.6},
            "logs": {"x": self.screen_width * 0.3, "y": self.screen_height * 0.6},
        }

    def check_mouse_activity(self) -> bool:
        """Check if mouse is working by detecting movement"""
        try:
            # Get current mouse position
            current_pos = pyautogui.position()
            
            # Check if mouse position has changed
            if hasattr(self, 'last_mouse_pos'):
                if current_pos != self.last_mouse_pos:
                    self.last_mouse_activity = time.time()
                    self.last_mouse_pos = current_pos
                    return True
            else:
                self.last_mouse_pos = current_pos
                return True
                
            # Check if mouse is responsive by trying to get position
            pyautogui.position()
            return True
            
        except Exception as e:
            logger.warning(f"Mouse check failed: {e}")
            return False

    def check_mouse_inactivity(self) -> bool:
        """Check if mouse has been inactive for too long"""
        return (time.time() - self.last_mouse_activity) > self.inactivity_threshold

    def should_activate_gesture_control(self) -> bool:
        """Determine if gesture control should be activated"""
        if not self.auto_activate:
            return False
            
        # Check if mouse is not working
        if not self.check_mouse_activity():
            logger.info("Mouse not working, activating gesture control")
            return True
            
        # Check if mouse has been inactive for too long
        if self.check_mouse_inactivity():
            logger.info("Mouse inactive for too long, activating gesture control")
            return True
            
        return False

    def check_fingers_up(self, hand_landmarks):
        """Count fingers that are up"""
        finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
        finger_bases = [5, 9, 13, 17]
        count = 0
        
        # Check thumb separately
        if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
            count += 1
        
        # Check other fingers
        for tip, base in zip(finger_tips, finger_bases):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[base].y:
                count += 1
                
        return count

    def calculate_eye_aspect_ratio(self, landmarks, left_eye_indices, right_eye_indices):
        """Calculate eye aspect ratio for blink detection"""
        def get_distance(p1, p2):
            return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
        
        # Left eye EAR
        left_vertical1 = get_distance(landmarks[left_eye_indices[1]], landmarks[left_eye_indices[5]])
        left_vertical2 = get_distance(landmarks[left_eye_indices[2]], landmarks[left_eye_indices[4]])
        left_horizontal = get_distance(landmarks[left_eye_indices[0]], landmarks[left_eye_indices[3]])
        left_ear = (left_vertical1 + left_vertical2) / (2.0 * left_horizontal)
        
        # Right eye EAR
        right_vertical1 = get_distance(landmarks[right_eye_indices[1]], landmarks[right_eye_indices[5]])
        right_vertical2 = get_distance(landmarks[right_eye_indices[2]], landmarks[right_eye_indices[4]])
        right_horizontal = get_distance(landmarks[right_eye_indices[0]], landmarks[right_eye_indices[3]])
        right_ear = (right_vertical1 + right_vertical2) / (2.0 * right_horizontal)
        
        # Average EAR
        ear = (left_ear + right_ear) / 2.0
        return ear

    def detect_blink(self, face_landmarks) -> bool:
        """Detect eye blink using eye aspect ratio"""
        # MediaPipe Face Mesh eye indices
        LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        
        try:
            ear = self.calculate_eye_aspect_ratio(face_landmarks.landmark, LEFT_EYE_INDICES, RIGHT_EYE_INDICES)
            current_time = time.time()
            
            # Check if blink detected and enough time has passed since last blink
            if ear < self.BLINK_THRESHOLD and self.last_ear >= self.BLINK_THRESHOLD:
                if current_time - self.last_blink_time > self.MIN_BLINK_INTERVAL:
                    self.last_blink_time = current_time
                    self.last_ear = ear
                    return True
            
            self.last_ear = ear
            return False
            
        except Exception as e:
            logger.warning(f"Blink detection error: {e}")
            return False

    def calculate_hand_height(self, hand_landmarks) -> float:
        """Calculate normalized hand height from landmarks"""
        wrist_y = hand_landmarks.landmark[0].y
        middle_mcp_y = hand_landmarks.landmark[9].y
        return (wrist_y + middle_mcp_y) / 2

    def perform_click(self, hand_landmarks):
        """Perform mouse click based on hand gesture"""
        hand_height = self.calculate_hand_height(hand_landmarks)
        
        # Map hand height to click type
        if hand_height < self.HAND_HEIGHT_MIN:
            # Low position - right click
            pyautogui.rightClick()
            logger.info("Right click performed")
            
        elif hand_height > self.HAND_HEIGHT_MAX:
            # High position - left click
            pyautogui.click()
            logger.info("Left click performed")
            
        else:
            # Middle position - no click
            pass

    def control_volume(self, hand_landmarks, is_right_hand: bool):
        """Control system volume based on hand position"""
        if not self.audio_available:
            return
            
        # Use thumb tip position for volume control
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        
        # Calculate vertical position (0-1 range)
        hand_y = (thumb_tip.y + index_tip.y) / 2
        
        # Map hand position to volume (0-100%)
        volume_level = 1.0 - max(0, min(1, hand_y))
        
        # Convert to dB range
        db_level = self.min_vol + (volume_level * (self.max_vol - self.min_vol))
        self.volume.SetMasterVolumeLevel(db_level, None)

    def scroll_based_on_gesture(self, hand_landmarks):
        """Scroll based on hand gesture"""
        current_time = time.time()
        if current_time - self.scroll_cooldown < self.SCROLL_COOLDOWN_TIME:
            return
            
        # Check for scroll gesture (peace sign - index and middle finger up)
        fingers_up = self.check_fingers_up(hand_landmarks)
        
        if fingers_up == 2:  # Peace sign
            # Determine scroll direction based on hand orientation
            wrist_y = hand_landmarks.landmark[0].y
            middle_tip_y = hand_landmarks.landmark[12].y
            
            if middle_tip_y < wrist_y:  # Hand facing up - scroll up
                pyautogui.scroll(self.SCROLL_AMOUNT)
                logger.info("Scrolled up")
            else:  # Hand facing down - scroll down
                pyautogui.scroll(-self.SCROLL_AMOUNT)
                logger.info("Scrolled down")
                
            self.scroll_cooldown = current_time

    def navigate_ui_elements(self, x: int, y: int):
        """Navigate SmartFix-AI UI elements based on cursor position"""
        for element_name, element_pos in self.ui_elements.items():
            elem_x, elem_y = element_pos["x"], element_pos["y"]
            distance = np.sqrt((x - elem_x)**2 + (y - elem_y)**2)
            
            # If cursor is near a UI element, highlight it (simulated)
            if distance < 100:  # 100 pixel radius
                logger.info(f"Hovering over {element_name}")
                # Here you would typically send a signal to the frontend
                # to highlight the UI element
                break

    def process_gestures(self, frame):
        """Process hand and face gestures from camera frame"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand_results = self.hands.process(rgb_frame)
        face_results = self.face_mesh.process(rgb_frame)
        
        # Process hand gestures
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # Get hand center for cursor control
                wrist = hand_landmarks.landmark[0]
                index_mcp = hand_landmarks.landmark[5]
                
                # Calculate hand center
                hand_x = (wrist.x + index_mcp.x) / 2
                hand_y = (wrist.y + index_mcp.y) / 2
                
                # Convert to screen coordinates with smoothing
                screen_x = int(hand_x * self.screen_width)
                screen_y = int(hand_y * self.screen_height)
                
                # Apply smoothing
                smooth_x = int(self.prev_x * self.smoothing + screen_x * (1 - self.smoothing))
                smooth_y = int(self.prev_y * self.smoothing + screen_y * (1 - self.smoothing))
                
                # Move mouse cursor
                pyautogui.moveTo(smooth_x, smooth_y, duration=0.01)
                self.prev_x, self.prev_y = smooth_x, smooth_y
                
                # Navigate UI elements
                self.navigate_ui_elements(smooth_x, smooth_y)
                
                # Check for gestures
                fingers_up = self.check_fingers_up(hand_landmarks)
                
                if fingers_up == 0:  # Fist - click
                    self.perform_click(hand_landmarks)
                elif fingers_up == 1:  # Pointing - volume control
                    self.control_volume(hand_landmarks, True)
                elif fingers_up == 2:  # Peace - scroll
                    self.scroll_based_on_gesture(hand_landmarks)
                elif fingers_up == 5:  # Open hand - activate/deactivate
                    self.toggle_activation()
        
        # Process face gestures (blink for special actions)
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                if self.detect_blink(face_landmarks):
                    # Double blink for emergency action
                    current_time = time.time()
                    if current_time - self.last_blink_time < 0.5:
                        logger.info("Emergency action triggered")
                        # Perform emergency action (e.g., open help menu)
                        pyautogui.hotkey('win', 'h')  # Windows help

    def start_camera(self):
        """Start camera capture"""
        try:
            self.cam = cv2.VideoCapture(0)
            if not self.cam.isOpened():
                logger.error("Cannot open camera")
                return False
            return True
        except Exception as e:
            logger.error(f"Camera start error: {e}")
            return False

    def stop_camera(self):
        """Stop camera capture"""
        if self.cam:
            self.cam.release()
        cv2.destroyAllWindows()

    def gesture_control_loop(self):
        """Main gesture control loop"""
        if not self.start_camera():
            logger.error("Failed to start camera")
            return
            
        logger.info("Gesture control activated")
        
        while self.is_active and self.is_running:
            ret, frame = self.cam.read()
            if not ret:
                logger.warning("Failed to capture frame")
                continue
                
            # Process gestures
            self.process_gestures(frame)
            
            # Display debug info if enabled
            if self.show_debug:
                cv2.putText(frame, "Gesture Control Active", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow('Gesture Control', frame)
                
            # Check for exit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        self.stop_camera()
        logger.info("Gesture control deactivated")

    def monitor_mouse_activity(self):
        """Monitor mouse activity and auto-activate gesture control"""
        while self.is_running:
            if self.should_activate_gesture_control() and not self.is_active:
                self.activate_gesture_control()
                
            time.sleep(self.mouse_check_interval)

    def activate_gesture_control(self):
        """Activate gesture control"""
        if not self.is_active:
            self.is_active = True
            logger.info("Gesture control activated")
            
            # Start gesture control in a separate thread
            self.gesture_thread = threading.Thread(target=self.gesture_control_loop)
            self.gesture_thread.daemon = True
            self.gesture_thread.start()

    def deactivate_gesture_control(self):
        """Deactivate gesture control"""
        if self.is_active:
            self.is_active = False
            logger.info("Gesture control deactivated")

    def toggle_activation(self):
        """Toggle gesture control activation"""
        if self.is_active:
            self.deactivate_gesture_control()
        else:
            self.activate_gesture_control()

    def start_service(self):
        """Start the gesture control service"""
        if self.is_running:
            logger.warning("Service already running")
            return
            
        self.is_running = True
        logger.info("Starting Gesture Control Service")
        
        # Start mouse monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_mouse_activity)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_service(self):
        """Stop the gesture control service"""
        if not self.is_running:
            logger.warning("Service not running")
            return
            
        self.is_running = False
        self.deactivate_gesture_control()
        logger.info("Gesture Control Service stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get current service status"""
        return {
            "is_running": self.is_running,
            "is_active": self.is_active,
            "auto_activate": self.auto_activate,
            "inactivity_threshold": self.inactivity_threshold,
            "last_mouse_activity": self.last_mouse_activity,
            "audio_available": self.audio_available
        }

    def update_settings(self, auto_activate: Optional[bool] = None, 
                       inactivity_threshold: Optional[int] = None):
        """Update service settings"""
        if auto_activate is not None:
            self.auto_activate = auto_activate
        if inactivity_threshold is not None:
            self.inactivity_threshold = inactivity_threshold

# Singleton instance for the service
gesture_service = GestureControlService()

async def start_gesture_service():
    """Async function to start the gesture service"""
    gesture_service.start_service()
    return {"status": "started", "message": "Gesture control service started"}

async def stop_gesture_service():
    """Async function to stop the gesture service"""
    gesture_service.stop_service()
    return {"status": "stopped", "message": "Gesture control service stopped"}

async def get_service_status():
    """Async function to get service status"""
    return gesture_service.get_status()

async def update_service_settings(auto_activate: Optional[bool] = None, 
                                 inactivity_threshold: Optional[int] = None):
    """Async function to update service settings"""
    gesture_service.update_settings(auto_activate, inactivity_threshold)
    return {"status": "updated", "message": "Service settings updated"}