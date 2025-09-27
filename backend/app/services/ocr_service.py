import logging
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image
import io
import re
import os
import json
from collections import defaultdict

# Try to import optional dependencies
try:
    import cv2
    import numpy as np
    import pytesseract
    OCR_AVAILABLE = True
except ImportError as e:
    OCR_AVAILABLE = False
    cv2 = None
    np = None
    pytesseract = None
    print(f"OCR dependencies not available: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRService:
    """
    Enhanced OCR service for extracting text, error codes, and analyzing error messages from images
    """
    
    def __init__(self, tesseract_cmd_path: Optional[str] = None):
        """
        Initialize the OCR service
        
        Args:
            tesseract_cmd_path (str, optional): Path to tesseract executable. 
                If not provided, will try to auto-detect.
        """
        if not OCR_AVAILABLE:
            logger.warning("OCR Service initialized but dependencies not available")
            self.tesseract_cmd_path = None
            self.error_patterns = {}
            self.device_patterns = {}
            return
            
        self.tesseract_cmd_path = tesseract_cmd_path
        self._setup_tesseract()
        
        # Error message patterns for specialized recognition
        self.error_patterns = {
            "sql_connection": [
                r"cannot\s+connect\s+to\s+(\w+)\s*server",
                r"sql\s+server\s+connection\s+error",
                r"network-related\s+or\s+instance-specific\s+error",
                r"named\s+pipes\s+provider",
                r"error\s+\d+",
                r"server\s+was\s+not\s+found",
                r"cannot\s+find\s+the\s+file\s+specified"
            ],
            "windows_error": [
                r"windows\s+error",
                r"system\s+error",
                r"application\s+error",
                r"exception\s+code",
                r"blue\s+screen",
                r"stop\s+code",
                r"BSOD"
            ],
            "network_error": [
                r"network\s+error",
                r"connection\s+failed",
                r"cannot\s+connect",
                r"no\s+internet",
                r"wifi\s+issue",
                r"ethernet\s+problem"
            ],
            "display_error": [
                r"monitor\s+not\s+detected",
                r"display\s+driver",
                r"graphics\s+card",
                r"screen\s+resolution",
                r"no\s+signal",
                r"display\s+adapter"
            ],
            "audio_error": [
                r"no\s+sound",
                r"audio\s+not\s+working",
                r"speaker\s+issue",
                r"volume\s+problem",
                r"muted",
                r"audio\s+driver"
            ]
        }
        
        # Load common error message templates for better recognition
        self.error_templates = self._load_error_templates()
    
    def _setup_tesseract(self):
        """Setup tesseract path"""
        if not OCR_AVAILABLE:
            return
            
        if self.tesseract_cmd_path and os.path.exists(self.tesseract_cmd_path):
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd_path
            logger.info(f"Tesseract configured at: {self.tesseract_cmd_path}")
            return
        
        # Try to auto-detect tesseract
        try:
            # For Windows
            if os.name == 'nt':
                possible_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                    r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', '')),
                ]
            # For Linux/Mac
            else:
                possible_paths = [
                    "/usr/bin/tesseract",
                    "/usr/local/bin/tesseract",
                    "/opt/homebrew/bin/tesseract",
                ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"Tesseract found at: {path}")
                    self.tesseract_cmd_path = path
                    break
            else:
                logger.warning("Tesseract not found in common locations. Please install Tesseract-OCR.")
        except Exception as e:
            logger.warning(f"Could not configure Tesseract path: {e}")
    
    def _load_error_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load common error message templates"""
        templates = {
            "sql_connection": {
                "issue": "SQL Server Connection Error",
                "possible_causes": [
                    "Server name is incorrect or server is offline",
                    "Network connectivity issues",
                    "SQL Server configuration problem",
                    "Firewall blocking connection"
                ],
                "recommended_steps": [
                    {"step_number": 1, "description": "Verify the server name is correct and the server is running"},
                    {"step_number": 2, "description": "Check network connectivity between client and server"},
                    {"step_number": 3, "description": "Ensure SQL Server is configured to allow remote connections"},
                    {"step_number": 4, "description": "Check firewall settings to allow SQL traffic (port 1433)"},
                    {"step_number": 5, "description": "Verify SQL Server credentials are correct"}
                ],
                "confidence_score": 0.9
            },
            "windows_error": {
                "issue": "Windows System Error",
                "possible_causes": [
                    "System file corruption",
                    "Driver conflicts",
                    "Hardware issues",
                    "Software incompatibility"
                ],
                "recommended_steps": [
                    {"step_number": 1, "description": "Restart your computer"},
                    {"step_number": 2, "description": "Run System File Checker (sfc /scannow)"},
                    {"step_number": 3, "description": "Update Windows and drivers"},
                    {"step_number": 4, "description": "Check for hardware issues"},
                    {"step_number": 5, "description": "Perform system restore if available"}
                ],
                "confidence_score": 0.85
            },
            "network_error": {
                "issue": "Network Connectivity Problem",
                "possible_causes": [
                    "Router/modem issues",
                    "ISP service disruption",
                    "Network adapter problems",
                    "Incorrect network configuration"
                ],
                "recommended_steps": [
                    {"step_number": 1, "description": "Restart your router and modem"},
                    {"step_number": 2, "description": "Check network cables are properly connected"},
                    {"step_number": 3, "description": "Reset network adapter on your device"},
                    {"step_number": 4, "description": "Verify IP address settings"},
                    {"step_number": 5, "description": "Contact your ISP if problems persist"}
                ],
                "confidence_score": 0.85
            },
            "display_error": {
                "issue": "Display/Monitor Connection Issue",
                "possible_causes": [
                    "Cable connection problem",
                    "Graphics driver issues",
                    "Incompatible resolution settings",
                    "Hardware failure"
                ],
                "recommended_steps": [
                    {"step_number": 1, "description": "Check cable connections between computer and monitor"},
                    {"step_number": 2, "description": "Try different ports (HDMI, DisplayPort, VGA)"},
                    {"step_number": 3, "description": "Update graphics drivers to the latest version"},
                    {"step_number": 4, "description": "Press Windows+P to check display projection settings"},
                    {"step_number": 5, "description": "Test with a different monitor if available"}
                ],
                "confidence_score": 0.8
            },
            "audio_error": {
                "issue": "Audio/Sound Problem",
                "possible_causes": [
                    "Muted audio",
                    "Audio driver issues",
                    "Incorrect audio output selection",
                    "Hardware failure"
                ],
                "recommended_steps": [
                    {"step_number": 1, "description": "Check if device is muted - look for mute button or icon"},
                    {"step_number": 2, "description": "Verify volume is turned up"},
                    {"step_number": 3, "description": "Check audio output settings"},
                    {"step_number": 4, "description": "Update audio drivers"},
                    {"step_number": 5, "description": "Test with headphones or external speakers"}
                ],
                "confidence_score": 0.8
            }
        }
        return templates
    
    def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Process image data to extract text and error codes
        
        Args:
            image_data (bytes): Raw image data
            
        Returns:
            dict: Extracted text and error codes
        """
        if not OCR_AVAILABLE:
            return {
                "success": False,
                "error": "OCR dependencies not available",
                "text": "",
                "error_codes": [],
                "confidence": 0.0
            }
            
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Preprocess the image
            processed_image = self._preprocess_image(opencv_image)
            
            # Extract text using OCR
            extracted_text = self._extract_text(processed_image)
            
            # Extract error codes from the text
            error_codes = self._extract_error_codes(extracted_text)
            
            # Analyze error message type
            error_analysis = self._analyze_error_message(extracted_text, error_codes)
            
            # Extract UI elements (buttons, input fields, etc.)
            ui_elements = self._extract_ui_elements(opencv_image)
            
            return {
                "extracted_text": extracted_text,
                "error_codes": error_codes,
                "error_analysis": error_analysis,
                "ui_elements": ui_elements,
                "success": True
            }
        
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return {
                "extracted_text": "",
                "error_codes": [],
                "error_analysis": {"error_type": "unknown", "confidence": 0},
                "ui_elements": [],
                "success": False,
                "error": str(e)
            }
    
    def _preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Try different thresholding methods
            # Method 1: Otsu's thresholding
            _, thresh_otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Method 2: Adaptive thresholding
            thresh_adaptive = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply morphological operations to clean up the image
            kernel = np.ones((1, 1), np.uint8)
            cleaned_otsu = cv2.morphologyEx(thresh_otsu, cv2.MORPH_CLOSE, kernel)
            cleaned_adaptive = cv2.morphologyEx(thresh_adaptive, cv2.MORPH_CLOSE, kernel)
            
            # Return both and let the extract_text method decide which works better
            return {
                "otsu": cleaned_otsu,
                "adaptive": cleaned_adaptive
            }
        
        except Exception as e:
            logger.warning(f"Error in image preprocessing: {e}")
            return {"original": image}
    
    def _extract_text(self, processed_images):
        """Extract text from preprocessed images"""
        best_text = ""
        best_confidence = 0
        
        # Configure OCR parameters
        custom_config = r'--oem 3 --psm 6'
        
        for method, image in processed_images.items():
            try:
                # Extract text with confidence data
                data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
                
                # Calculate average confidence for non-empty text
                confidences = [int(conf) for i, conf in enumerate(data['conf']) 
                              if int(conf) > 0 and data['text'][i].strip()]
                
                if confidences:
                    avg_confidence = sum(confidences) / len(confidences)
                    text = ' '.join([t for t in data['text'] if t.strip()])
                    
                    # Keep the text with highest confidence
                    if avg_confidence > best_confidence:
                        best_confidence = avg_confidence
                        best_text = text
            except Exception as e:
                logger.warning(f"Error extracting text with {method} method: {e}")
                continue
        
        # Clean up the text
        best_text = best_text.strip()
        best_text = re.sub(r'\s+', ' ', best_text)  # Replace multiple spaces with single space
        
        return best_text
    
    def _analyze_error_message(self, text: str, error_codes: List[str]) -> Dict[str, Any]:
        """
        Analyze error message text to determine error type and provide solutions
        """
        if not text:
            return {"error_type": "unknown", "confidence": 0}
        
        text_lower = text.lower()
        
        # Score each error type based on pattern matches
        error_scores = defaultdict(float)
        
        # Check for each error pattern
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    error_scores[error_type] += 0.2  # Add score for each matching pattern
        
        # Check for specific error codes that indicate certain error types
        for code in error_codes:
            code_lower = code.lower()
            if "sql" in code_lower or code_lower.startswith(("db", "odbc", "oledb")):
                error_scores["sql_connection"] += 0.3
            elif code_lower.startswith(("0x", "0x0", "0x00")):
                error_scores["windows_error"] += 0.3
            elif "net" in code_lower or code_lower.startswith(("tcp", "ip", "http")):
                error_scores["network_error"] += 0.3
            elif "disp" in code_lower or code_lower.startswith(("vga", "hdmi", "gpu")):
                error_scores["display_error"] += 0.3
            elif "audio" in code_lower or code_lower.startswith(("snd", "wav", "mp3")):
                error_scores["audio_error"] += 0.3
        
        # Find the most likely error type
        if error_scores:
            best_error_type = max(error_scores.items(), key=lambda x: x[1])
            if best_error_type[1] >= 0.2:  # Minimum confidence threshold
                error_type = best_error_type[0]
                confidence = min(best_error_type[1], 1.0)  # Cap at 1.0
                
                # Get template for this error type
                template = self.error_templates.get(error_type, {}).copy()
                
                # Extract specific details if possible
                if error_type == "sql_connection":
                    server_match = re.search(r"server\s+['\"](.*?)['\"]", text_lower)
                    if server_match:
                        template["server_name"] = server_match.group(1)
                
                return {
                    "error_type": error_type,
                    "confidence": confidence,
                    "template": template
                }
        
        # No clear error type detected
        return {"error_type": "unknown", "confidence": 0}
    
    def _extract_ui_elements(self, image) -> List[Dict[str, Any]]:
        """
        Extract UI elements like buttons, input fields, etc. from the image
        """
        ui_elements = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Find potential buttons using contour detection
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Process contours to identify buttons
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by size (buttons are usually of certain dimensions)
                if w > 50 and h > 20 and w < 300 and h < 100:
                    # Extract the potential button region
                    button_roi = image[y:y+h, x:x+w]
                    
                    # Try to extract text from this region
                    button_text = pytesseract.image_to_string(button_roi).strip()
                    
                    # Common button texts
                    button_keywords = ["ok", "cancel", "yes", "no", "submit", "close", "next", "back", "continue"]
                    
                    # Check if the text matches common button labels
                    if button_text and any(keyword in button_text.lower() for keyword in button_keywords):
                        ui_elements.append({
                            "type": "button",
                            "text": button_text,
                            "position": {"x": x, "y": y, "width": w, "height": h}
                        })
            
            # Look for dialog boxes (usually rectangles with title bars)
            # This is a simplified approach - real implementation would be more complex
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
            
            if lines is not None and len(lines) > 10:  # Likely has UI elements with straight lines
                ui_elements.append({
                    "type": "dialog_box",
                    "detected": True
                })
            
            return ui_elements
            
        except Exception as e:
            logger.warning(f"Error extracting UI elements: {e}")
            return []
    
    def _extract_error_codes(self, text: str) -> List[str]:
        """Extract error codes from text using enhanced regex patterns"""
        error_codes = []
        
        if not text:
            return error_codes
        
        # Enhanced error code patterns
        patterns = [
            # SQL Server errors
            r'\b(error|exception|fault|failure|alert|warning|code)[\s:]+([A-Za-z0-9\-_]+)\b',
            r'SQL\s+Server\s+Error\s+(\d+)',
            r'Error\s+Number\s*:\s*(\d+)',
            
            # Windows errors
            r'\b([A-Z][0-9]{3,6})\b',  # Common format like E1234, E12345
            r'\b([A-Z]-[0-9]{2,5})\b',  # Format like E-123
            r'\b([A-Z]{2,5}[0-9]{2,5})\b',  # Format like ERR123, ERROR123
            r'\b([A-Z]{2,5}-[0-9]{2,5})\b',  # Format like ERR-123, ERROR-123
            r'\b(0x[0-9A-Fa-f]{2,8})\b',  # Hexadecimal error codes
            
            # Network errors
            r'HTTP\s+(\d{3})',  # HTTP status codes
            r'Error\s+(\d{3,6})',  # Numeric error codes
            
            # Named errors
            r'\b(HRESULT|NTSTATUS|DWORD|SCODE):\s*([A-Za-z0-9\-_]+)\b',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # For patterns with capture groups, take the error code part
                    error_code = match[1] if len(match) > 1 else match[0]
                else:
                    error_code = match
                
                # Filter out very short or common false positives
                if len(error_code) >= 3 and error_code.lower() not in ['the', 'and', 'for', 'not', 'error']:
                    error_codes.append(error_code.upper())
        
        # Remove duplicates and return
        return sorted(list(set(error_codes)))