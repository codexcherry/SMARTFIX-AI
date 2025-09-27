import google.generativeai as genai
from typing import Dict, List, Any, Optional
import base64
import json
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, api_key: str = settings.GEMINI_API_KEY):
        self.api_key = api_key
        try:
            genai.configure(api_key=self.api_key)
            logger.info(f"Gemini API configured with key: {self.api_key[:10]}...")
            
            # Try different model versions in order of preference
            model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
            self.model = None
            self.vision_model = None
            
            for model_name in model_names:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    self.vision_model = genai.GenerativeModel(model_name)
                    logger.info(f"Successfully initialized Gemini with model: {model_name}")
                    break
                except Exception as model_error:
                    logger.warning(f"Failed to initialize with {model_name}: {model_error}")
                    continue
                    
            if not self.model:
                raise Exception("No compatible Gemini model found")
                
        except Exception as e:
            logger.error(f"Error initializing Gemini service: {e}")
            self.model = None
            self.vision_model = None
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text input to identify issues and solutions"""
        if not self.model:
            return {
                "issue": "Gemini service unavailable",
                "possible_causes": ["API key not configured", "Service initialization failed"],
                "confidence_score": 0.1,
                "recommended_steps": [
                    {"step_number": 1, "description": "Check Gemini API key configuration"}
                ]
            }
            
        prompt = f"""
        You are an AI troubleshooting assistant. Analyze the following technical issue description:
        
        "{text}"
        
        Provide a structured analysis in JSON format with the following fields:
        - issue: A concise summary of the problem
        - possible_causes: List of potential causes
        - confidence_score: A number between 0 and 1 indicating confidence in your analysis
        - recommended_steps: List of troubleshooting steps, each with a step_number and description
        
        Return ONLY the JSON object, no additional text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text
            # Handle case where response might have markdown code blocks
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].strip()
            else:
                json_str = response_text.strip()
            
            try:
                result = json.loads(json_str)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response manually
                return {
                    "issue": text[:50] + "..." if len(text) > 50 else text,
                    "possible_causes": ["Unable to parse response from Gemini API"],
                    "confidence_score": 0.3,
                    "recommended_steps": [
                        {"step_number": 1, "description": "Please try with a more specific description of the issue"}
                    ]
                }
            
            # Ensure the response has the expected structure
            if not isinstance(result.get("recommended_steps"), list):
                result["recommended_steps"] = []
            
            # Convert recommended_steps to the expected format if it's just a list of strings
            steps = []
            for i, step in enumerate(result["recommended_steps"]):
                if isinstance(step, str):
                    steps.append({"step_number": i+1, "description": step})
                elif isinstance(step, dict) and "description" in step:
                    if "step_number" not in step:
                        step["step_number"] = i+1
                    steps.append(step)
            
            result["recommended_steps"] = steps
            return result
        
        except Exception as e:
            logger.error(f"Error in analyze_text: {e}")
            # Provide more helpful fallback responses based on common issues
            issue_lower = text.lower()
            
            # Phone-related issues
            if any(keyword in issue_lower for keyword in ['phone', 'mobile', 'device', 'smartphone']):
                return {
                    "issue": "Phone/Device Issue",
                    "possible_causes": [
                        "Battery drained or charging issues",
                        "Software glitch or crash",
                        "Hardware malfunction",
                        "Network connectivity problems",
                        "App conflicts or crashes"
                    ],
                    "confidence_score": 0.7,
                    "recommended_steps": [
                        {"step_number": 1, "description": "Try charging your device for at least 30 minutes"},
                        {"step_number": 2, "description": "Perform a force restart (hold power + volume down for 10-20 seconds)"},
                        {"step_number": 3, "description": "Check for physical damage or water exposure"},
                        {"step_number": 4, "description": "Try booting in safe mode to isolate app issues"},
                        {"step_number": 5, "description": "Contact device manufacturer or service center if issues persist"}
                    ]
                }
            
            # General fallback
            return {
                "issue": text[:50] + "..." if len(text) > 50 else text,
                "possible_causes": ["Unable to determine causes", f"Error: {str(e)}"],
                "confidence_score": 0.1,
                "recommended_steps": [
                    {"step_number": 1, "description": "Please provide more details about the issue"}
                ]
            }
    
    async def analyze_image(self, image_data: bytes, text_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Analyze image to identify issues and solutions"""
        if not self.vision_model:
            return {
                "issue": "Gemini Vision service unavailable",
                "possible_causes": ["API key not configured", "Service initialization failed"],
                "confidence_score": 0.1,
                "recommended_steps": [
                    {"step_number": 1, "description": "Check Gemini API key configuration"}
                ]
            }
            
        if not text_prompt:
            text_prompt = "Analyze this image and identify any technical issues or error messages visible."
        
        prompt = f"""
        You are an AI troubleshooting assistant. Analyze the following image showing a technical issue.
        {text_prompt}
        
        Provide a structured analysis in JSON format with the following fields:
        - issue: A concise summary of the problem visible in the image
        - possible_causes: List of potential causes
        - confidence_score: A number between 0 and 1 indicating confidence in your analysis
        - recommended_steps: List of troubleshooting steps, each with a step_number and description
        
        Return ONLY the JSON object, no additional text.
        """
        
        try:
            # Handle image data safely
            try:
                response = self.vision_model.generate_content([prompt, image_data])
                
                # Extract JSON from response
                response_text = response.text
                # Handle case where response might have markdown code blocks
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].strip()
                else:
                    json_str = response_text.strip()
                
                try:
                    result = json.loads(json_str)
                except json.JSONDecodeError:
                    # If JSON parsing fails, create a structured response manually
                    return {
                        "issue": "Unable to parse image analysis results",
                        "possible_causes": ["Complex image content", "Non-standard error format"],
                        "confidence_score": 0.3,
                        "recommended_steps": [
                            {"step_number": 1, "description": "Please provide a clearer image of the error"}
                        ]
                    }
                
                # Ensure the response has the expected structure
                if not isinstance(result.get("recommended_steps"), list):
                    result["recommended_steps"] = []
                
                # Convert recommended_steps to the expected format if it's just a list of strings
                steps = []
                for i, step in enumerate(result["recommended_steps"]):
                    if isinstance(step, str):
                        steps.append({"step_number": i+1, "description": step})
                    elif isinstance(step, dict) and "description" in step:
                        if "step_number" not in step:
                            step["step_number"] = i+1
                        steps.append(step)
                
                result["recommended_steps"] = steps
                return result
            except ValueError as ve:
                print(f"Invalid image data: {ve}")
                return {
                    "issue": "Invalid image data",
                    "possible_causes": ["Corrupted image file", "Unsupported image format"],
                    "confidence_score": 0.1,
                    "recommended_steps": [
                        {"step_number": 1, "description": "Please upload the image in a standard format (JPEG, PNG)"}
                    ]
                }
        
        except Exception as e:
            print(f"Error in analyze_image: {e}")
            # Fallback for non-JSON responses
            return {
                "issue": "Unable to analyze image",
                "possible_causes": ["Image quality issues", "Unrecognized error format", f"Error: {str(e)}"],
                "confidence_score": 0.1,
                "recommended_steps": [
                    {"step_number": 1, "description": "Please provide a clearer image or additional context"}
                ]
            }
    
    async def analyze_logs(self, log_content: str) -> Dict[str, Any]:
        """Analyze log files to identify issues and solutions"""
        if not self.model:
            return {
                "issue": "Gemini service unavailable",
                "possible_causes": ["API key not configured", "Service initialization failed"],
                "confidence_score": 0.1,
                "recommended_steps": [
                    {"step_number": 1, "description": "Check Gemini API key configuration"}
                ]
            }
            
        # Safely limit log content to avoid token limits
        safe_log_content = log_content[:2000] if log_content else "Empty log content"
        
        prompt = f"""
        You are an AI troubleshooting assistant specializing in log analysis. Analyze the following log content:
        
        ```
        {safe_log_content}
        ```
        
        Provide a structured analysis in JSON format with the following fields:
        - issue: A concise summary of any errors or issues found in the logs
        - possible_causes: List of potential causes for the identified issues
        - confidence_score: A number between 0 and 1 indicating confidence in your analysis
        - recommended_steps: List of troubleshooting steps, each with a step_number and description
        
        Return ONLY the JSON object, no additional text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text
            # Handle case where response might have markdown code blocks
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].strip()
            else:
                json_str = response_text.strip()
            
            try:
                result = json.loads(json_str)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response manually
                return {
                    "issue": "Unable to parse log analysis results",
                    "possible_causes": ["Complex log format", "Non-standard error format"],
                    "confidence_score": 0.3,
                    "recommended_steps": [
                        {"step_number": 1, "description": "Please provide a more specific section of the logs containing errors"}
                    ]
                }
            
            # Ensure the response has the expected structure
            if not isinstance(result.get("recommended_steps"), list):
                result["recommended_steps"] = []
            
            # Convert recommended_steps to the expected format if it's just a list of strings
            steps = []
            for i, step in enumerate(result["recommended_steps"]):
                if isinstance(step, str):
                    steps.append({"step_number": i+1, "description": step})
                elif isinstance(step, dict) and "description" in step:
                    if "step_number" not in step:
                        step["step_number"] = i+1
                    steps.append(step)
            
            result["recommended_steps"] = steps
            return result
        
        except Exception as e:
            print(f"Error in analyze_logs: {e}")
            # Fallback for non-JSON responses
            return {
                "issue": "Log analysis error",
                "possible_causes": ["Complex log format", "Insufficient context in logs", f"Error: {str(e)}"],
                "confidence_score": 0.1,
                "recommended_steps": [
                    {"step_number": 1, "description": "Please provide more context about the system generating these logs"}
                ]
            }