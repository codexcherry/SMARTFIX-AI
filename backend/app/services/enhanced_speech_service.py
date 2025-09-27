"""
Enhanced Speech Recognition Service for SmartFix-AI
Provides advanced speech recognition with confidence scoring and validation
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)

class EnhancedSpeechService:
    """
    Enhanced speech recognition service with confidence scoring and validation
    """
    
    def __init__(self):
        """Initialize the enhanced speech service"""
        # Common technical terms and phrases for validation
        self.technical_terms = {
            "computer": ["computer", "pc", "laptop", "desktop", "machine", "system"],
            "network": ["network", "internet", "wifi", "connection", "ethernet", "router", "modem"],
            "display": ["screen", "monitor", "display", "resolution", "graphics", "video"],
            "audio": ["sound", "audio", "speaker", "volume", "microphone", "headphones"],
            "error": ["error", "issue", "problem", "bug", "crash", "freeze", "not working"],
            "device": ["device", "hardware", "equipment", "peripheral", "accessory"]
        }
        
        # Common phrases that are often misrecognized
        self.common_phrases = {
            "screen is broken": ["screen is broken", "screen broken", "broken screen", "display broken"],
            "internet not working": ["internet not working", "no internet", "wifi not working", "no connection"],
            "computer is slow": ["computer is slow", "pc is slow", "laptop is slow", "system slow"],
            "no sound": ["no sound", "no audio", "cannot hear", "sound not working", "audio not working"],
            "blue screen": ["blue screen", "blue screen of death", "bsod", "system crash"],
            "printer not working": ["printer not working", "can't print", "printer offline", "printer error"]
        }
        
        # Confidence thresholds
        self.high_confidence = 0.85
        self.medium_confidence = 0.6
        self.low_confidence = 0.3
    
    async def process_speech_input(self, 
                                  speech_text: str, 
                                  confidence: Optional[float] = None) -> Dict[str, Any]:
        """
        Process speech input with enhanced validation and confidence scoring
        
        Args:
            speech_text: The raw text from speech recognition
            confidence: Optional confidence score from the speech recognition system
            
        Returns:
            Dict with processed text, confidence score, and validation results
        """
        # Clean up the text
        cleaned_text = self._clean_text(speech_text)
        
        # Calculate confidence if not provided
        if confidence is None:
            confidence = self._estimate_confidence(cleaned_text)
        
        # Validate and correct the text
        validated_text, validation_score = self._validate_and_correct(cleaned_text)
        
        # Determine if confirmation is needed
        needs_confirmation = confidence < self.medium_confidence or validation_score < self.medium_confidence
        
        # Generate confirmation options if needed
        confirmation_options = []
        if needs_confirmation:
            confirmation_options = self._generate_confirmation_options(validated_text)
        
        # Classify the query type
        query_type = self._classify_query_type(validated_text)
        
        # Extract key entities
        entities = self._extract_entities(validated_text)
        
        return {
            "original_text": speech_text,
            "processed_text": validated_text,
            "confidence_score": confidence,
            "validation_score": validation_score,
            "needs_confirmation": needs_confirmation,
            "confirmation_options": confirmation_options,
            "query_type": query_type,
            "entities": entities
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean up the speech text"""
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Fix common speech recognition errors
        text = text.replace("eye", "i")
        text = text.replace("for", "four")
        text = text.replace("to", "two")
        text = text.replace("won", "one")
        
        # Fix common technical terms
        text = text.replace("wife i", "wifi")
        text = text.replace("why fi", "wifi")
        text = text.replace("why five", "wifi")
        text = text.replace("blue tooth", "bluetooth")
        text = text.replace("you as be", "usb")
        text = text.replace("you s b", "usb")
        
        return text
    
    def _estimate_confidence(self, text: str) -> float:
        """
        Estimate confidence score based on text characteristics
        """
        if not text:
            return 0.0
        
        base_confidence = 0.5  # Start with medium confidence
        
        # Check for very short text (likely incomplete)
        if len(text) < 5:
            base_confidence -= 0.2
        
        # Check for very long text (more likely to contain errors)
        if len(text) > 100:
            base_confidence -= 0.1
        
        # Check for technical terms (increases confidence)
        tech_term_count = 0
        for category, terms in self.technical_terms.items():
            if any(term in text for term in terms):
                tech_term_count += 1
        
        base_confidence += min(tech_term_count * 0.05, 0.25)  # Max bonus of 0.25
        
        # Check for common phrases (increases confidence)
        for phrase, variants in self.common_phrases.items():
            if any(variant in text for variant in variants):
                base_confidence += 0.1
                break
        
        # Cap confidence between 0 and 1
        return max(0.0, min(base_confidence, 1.0))
    
    def _validate_and_correct(self, text: str) -> Tuple[str, float]:
        """
        Validate and correct the speech text
        
        Returns:
            Tuple of (corrected_text, validation_score)
        """
        if not text:
            return "", 0.0
        
        # Start with the original text and a base validation score
        corrected_text = text
        validation_score = 0.5
        
        # Check for exact matches in common phrases
        for phrase, variants in self.common_phrases.items():
            for variant in variants:
                # Calculate similarity between input and variant
                similarity = self._calculate_similarity(text, variant)
                if similarity > 0.8:  # High similarity threshold
                    corrected_text = phrase  # Use the canonical phrase
                    validation_score = similarity
                    break
        
        # Fix common technical term errors
        words = corrected_text.split()
        for i, word in enumerate(words):
            # Fix common technical term errors
            if word in ["screen", "display"] and i+1 < len(words) and words[i+1] in ["broke", "broken", "break", "breaking"]:
                words[i:i+2] = ["screen is broken"]
                validation_score += 0.1
            elif word in ["no", "not"] and i+1 < len(words) and words[i+1] in ["internet", "connection", "wifi", "network"]:
                words[i:i+2] = ["internet not working"]
                validation_score += 0.1
            elif word in ["laptop", "computer", "pc"] and i+1 < len(words) and words[i+1] in ["slow", "sluggish", "hanging"]:
                words[i:i+2] = ["computer is slow"]
                validation_score += 0.1
        
        # Reconstruct the text
        corrected_text = " ".join(words)
        
        # Cap validation score between 0 and 1
        validation_score = max(0.0, min(validation_score, 1.0))
        
        return corrected_text, validation_score
    
    def _generate_confirmation_options(self, text: str) -> List[str]:
        """
        Generate confirmation options for low-confidence transcriptions
        """
        options = [text]  # Always include the original text
        
        # Find similar common phrases
        for phrase, variants in self.common_phrases.items():
            for variant in variants:
                similarity = self._calculate_similarity(text, variant)
                if similarity > 0.6 and phrase not in options:
                    options.append(phrase)
        
        # Limit to 3 options
        return options[:3]
    
    def _classify_query_type(self, text: str) -> str:
        """
        Classify the query type based on the text
        """
        text_lower = text.lower()
        
        # Check for greetings
        if re.search(r'\b(hi|hello|hey|good\s+morning|good\s+afternoon|good\s+evening)\b', text_lower):
            return "greeting"
        
        # Check for technical issue categories
        category_scores = {}
        
        for category, terms in self.technical_terms.items():
            score = sum(1 for term in terms if term in text_lower)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            # Return the category with the highest score
            return max(category_scores.items(), key=lambda x: x[1])[0]
        
        # Default to general query
        return "general"
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract key entities from the text
        """
        entities = {
            "devices": [],
            "issues": [],
            "actions": []
        }
        
        text_lower = text.lower()
        
        # Extract devices
        for device in ["computer", "laptop", "desktop", "monitor", "screen", "printer", 
                      "router", "modem", "phone", "tablet", "keyboard", "mouse"]:
            if device in text_lower:
                entities["devices"].append(device)
        
        # Extract issues
        for issue in ["broken", "not working", "error", "slow", "crash", "freeze", 
                     "blue screen", "black screen", "no sound", "no internet"]:
            if issue in text_lower:
                entities["issues"].append(issue)
        
        # Extract actions
        for action in ["fix", "repair", "troubleshoot", "solve", "help", "check", "restart"]:
            if action in text_lower:
                entities["actions"].append(action)
        
        return entities
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two strings using a simple algorithm
        """
        # Convert to sets of words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0.0
            
        return intersection / union

# Create singleton instance
enhanced_speech_service = EnhancedSpeechService()

def get_enhanced_speech_service() -> EnhancedSpeechService:
    """Get the enhanced speech service instance"""
    return enhanced_speech_service
