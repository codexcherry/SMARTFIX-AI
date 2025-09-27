"""
Explainable AI (XAI) Interface

Provides transparent explanations for AI decisions to build user trust
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class AIExplanation:
    """AI explanation data structure"""
    explanation_id: str
    decision_type: str  # healing_action, optimization, prediction
    decision: str
    confidence: float
    reasoning: List[str]
    factors: Dict[str, float]
    impact: str
    alternatives: List[str]
    timestamp: datetime

@dataclass
class UserFeedback:
    """User feedback data structure"""
    feedback_id: str
    explanation_id: str
    rating: int  # 1-5
    helpful: bool
    comments: str
    timestamp: datetime

class XAIInterface:
    """
    Explainable AI interface for user trust and transparency
    """
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.is_initialized = False
        
        # Explanation configuration
        self.config = {
            "explanation_levels": ["simple", "detailed", "technical"],
            "default_level": "simple",
            "feedback_threshold": 0.7,
            "explanation_cache_size": 100
        }
        
        # Explanation templates
        self.explanation_templates = {
            "healing_action": {
                "simple": "Fixed {issue} to improve {benefit}",
                "detailed": "Detected {issue} and applied {action} to resolve it, resulting in {benefit}",
                "technical": "Identified {issue} through {detection_method}, executed {action} with {confidence}% confidence, achieving {benefit}"
            },
            "optimization": {
                "simple": "Optimized {component} for better {goal}",
                "detailed": "Analyzed {component} performance and applied {optimization} to improve {goal}",
                "technical": "Evaluated {component} metrics, implemented {optimization} algorithm, resulting in {improvement}% improvement in {goal}"
            },
            "prediction": {
                "simple": "Predicted {outcome} based on {factors}",
                "detailed": "Analyzed {factors} and predicted {outcome} with {confidence}% confidence",
                "technical": "Applied {model_type} model to {data_points} data points, predicting {outcome} with {confidence}% confidence based on {factors}"
            }
        }
        
        # Explanation cache
        self.explanation_cache = {}
        self.user_feedback = []
    
    async def initialize(self):
        """Initialize the XAI interface"""
        try:
            logger.info("Initializing XAI Interface")
            
            # Load explanation templates
            await self._load_explanation_templates()
            
            # Initialize explanation cache
            await self._initialize_explanation_cache()
            
            # Start feedback collection
            await self._start_feedback_collection()
            
            self.is_initialized = True
            logger.info("XAI Interface initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize XAI Interface: {e}")
            raise
    
    async def _load_explanation_templates(self):
        """Load explanation templates"""
        try:
            # Templates are already loaded in __init__
            logger.info("Explanation templates loaded")
            
        except Exception as e:
            logger.error(f"Failed to load explanation templates: {e}")
    
    async def _initialize_explanation_cache(self):
        """Initialize explanation cache"""
        try:
            self.explanation_cache = {}
            logger.info("Explanation cache initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize explanation cache: {e}")
    
    async def _start_feedback_collection(self):
        """Start feedback collection process"""
        asyncio.create_task(self._collect_user_feedback())
        asyncio.create_task(self._analyze_feedback_patterns())
        
        logger.info("Feedback collection started")
    
    async def generate_explanation(self, decision_type: str, decision_data: Dict[str, Any], 
                                 explanation_level: str = "simple") -> Dict[str, Any]:
        """Generate explanation for AI decision"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Check cache first
            cache_key = self._generate_cache_key(decision_type, decision_data, explanation_level)
            if cache_key in self.explanation_cache:
                return self.explanation_cache[cache_key]
            
            # Generate explanation
            explanation = await self._create_explanation(decision_type, decision_data, explanation_level)
            
            # Cache explanation
            self.explanation_cache[cache_key] = explanation
            
            # Maintain cache size
            await self._maintain_cache_size()
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_explanation(self, decision_type: str, decision_data: Dict[str, Any], 
                                explanation_level: str) -> Dict[str, Any]:
        """Create explanation for decision"""
        try:
            # Get template for decision type and level
            template = self.explanation_templates.get(decision_type, {}).get(explanation_level, "")
            
            if not template:
                template = "AI decision: {decision}"
            
            # Generate explanation text
            explanation_text = await self._format_explanation(template, decision_data)
            
            # Create explanation object
            explanation = AIExplanation(
                explanation_id=f"explanation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                decision_type=decision_type,
                decision=decision_data.get("decision", "unknown"),
                confidence=decision_data.get("confidence", 0.0),
                reasoning=await self._generate_reasoning(decision_type, decision_data),
                factors=await self._extract_factors(decision_type, decision_data),
                impact=await self._assess_impact(decision_type, decision_data),
                alternatives=await self._generate_alternatives(decision_type, decision_data),
                timestamp=datetime.now()
            )
            
            return {
                "success": True,
                "explanation": explanation_text,
                "explanation_id": explanation.explanation_id,
                "decision_type": decision_type,
                "confidence": explanation.confidence,
                "reasoning": explanation.reasoning,
                "factors": explanation.factors,
                "impact": explanation.impact,
                "alternatives": explanation.alternatives,
                "level": explanation_level
            }
            
        except Exception as e:
            logger.error(f"Error creating explanation: {e}")
            return {"success": False, "error": str(e)}
    
    async def _format_explanation(self, template: str, decision_data: Dict[str, Any]) -> str:
        """Format explanation using template"""
        try:
            # Replace placeholders in template
            explanation = template.format(
                issue=decision_data.get("issue", "system issue"),
                action=decision_data.get("action", "optimization"),
                benefit=decision_data.get("benefit", "performance improvement"),
                component=decision_data.get("component", "system"),
                goal=decision_data.get("goal", "performance"),
                optimization=decision_data.get("optimization", "algorithm"),
                improvement=decision_data.get("improvement", 10),
                outcome=decision_data.get("outcome", "improvement"),
                factors=decision_data.get("factors", "system metrics"),
                confidence=decision_data.get("confidence", 85),
                model_type=decision_data.get("model_type", "ML model"),
                data_points=decision_data.get("data_points", 1000),
                detection_method=decision_data.get("detection_method", "analysis"),
                decision=decision_data.get("decision", "AI decision")
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error formatting explanation: {e}")
            return "AI decision was made to improve system performance."
    
    async def _generate_reasoning(self, decision_type: str, decision_data: Dict[str, Any]) -> List[str]:
        """Generate reasoning for decision"""
        try:
            reasoning = []
            
            if decision_type == "healing_action":
                reasoning.extend([
                    f"Detected {decision_data.get('issue', 'issue')} through system monitoring",
                    f"Applied {decision_data.get('action', 'action')} based on historical success rate",
                    f"Expected improvement: {decision_data.get('benefit', 'performance gain')}"
                ])
            elif decision_type == "optimization":
                reasoning.extend([
                    f"Analyzed {decision_data.get('component', 'component')} performance metrics",
                    f"Identified optimization opportunity in {decision_data.get('area', 'system')}",
                    f"Applied {decision_data.get('optimization', 'optimization')} for {decision_data.get('goal', 'improvement')}"
                ])
            elif decision_type == "prediction":
                reasoning.extend([
                    f"Analyzed {decision_data.get('data_points', 1000)} data points",
                    f"Applied {decision_data.get('model_type', 'ML model')} for prediction",
                    f"Predicted {decision_data.get('outcome', 'outcome')} with {decision_data.get('confidence', 85)}% confidence"
                ])
            
            return reasoning
            
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            return ["AI decision based on system analysis"]
    
    async def _extract_factors(self, decision_type: str, decision_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract factors that influenced the decision"""
        try:
            factors = {}
            
            if decision_type == "healing_action":
                factors = {
                    "system_health": decision_data.get("system_health", 0.7),
                    "issue_severity": decision_data.get("severity", 0.8),
                    "action_success_rate": decision_data.get("success_rate", 0.9),
                    "user_impact": decision_data.get("user_impact", 0.6)
                }
            elif decision_type == "optimization":
                factors = {
                    "performance_metrics": decision_data.get("performance", 0.8),
                    "resource_usage": decision_data.get("resource_usage", 0.7),
                    "user_preferences": decision_data.get("user_preferences", 0.5),
                    "system_constraints": decision_data.get("constraints", 0.6)
                }
            elif decision_type == "prediction":
                factors = {
                    "historical_data": decision_data.get("historical_data", 0.9),
                    "current_conditions": decision_data.get("current_conditions", 0.8),
                    "model_accuracy": decision_data.get("model_accuracy", 0.85),
                    "data_quality": decision_data.get("data_quality", 0.7)
                }
            
            return factors
            
        except Exception as e:
            logger.error(f"Error extracting factors: {e}")
            return {"system_analysis": 0.8}
    
    async def _assess_impact(self, decision_type: str, decision_data: Dict[str, Any]) -> str:
        """Assess impact of the decision"""
        try:
            if decision_type == "healing_action":
                return f"Resolves {decision_data.get('issue', 'issue')} and improves {decision_data.get('benefit', 'performance')}"
            elif decision_type == "optimization":
                return f"Optimizes {decision_data.get('component', 'system')} for better {decision_data.get('goal', 'performance')}"
            elif decision_type == "prediction":
                return f"Provides early warning for {decision_data.get('outcome', 'potential issue')}"
            else:
                return "Improves overall system performance and user experience"
                
        except Exception as e:
            logger.error(f"Error assessing impact: {e}")
            return "Improves system performance"
    
    async def _generate_alternatives(self, decision_type: str, decision_data: Dict[str, Any]) -> List[str]:
        """Generate alternative actions that could have been taken"""
        try:
            alternatives = []
            
            if decision_type == "healing_action":
                alternatives = [
                    "Wait for user intervention",
                    "Apply different healing strategy",
                    "Schedule maintenance for later"
                ]
            elif decision_type == "optimization":
                alternatives = [
                    "Manual optimization",
                    "Different optimization algorithm",
                    "Defer optimization to off-peak hours"
                ]
            elif decision_type == "prediction":
                alternatives = [
                    "Use different prediction model",
                    "Collect more data before predicting",
                    "Use simpler prediction method"
                ]
            
            return alternatives
            
        except Exception as e:
            logger.error(f"Error generating alternatives: {e}")
            return ["Alternative approach available"]
    
    async def collect_user_feedback(self, explanation_id: str, rating: int, 
                                  helpful: bool, comments: str = "") -> Dict[str, Any]:
        """Collect user feedback on explanation"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Create feedback object
            feedback = UserFeedback(
                feedback_id=f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                explanation_id=explanation_id,
                rating=rating,
                helpful=helpful,
                comments=comments,
                timestamp=datetime.now()
            )
            
            # Store feedback
            self.user_feedback.append(feedback)
            
            # Analyze feedback for improvement
            await self._analyze_feedback(feedback)
            
            return {
                "success": True,
                "feedback_id": feedback.feedback_id,
                "message": "Thank you for your feedback!"
            }
            
        except Exception as e:
            logger.error(f"Error collecting user feedback: {e}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_feedback(self, feedback: UserFeedback):
        """Analyze user feedback for improvement"""
        try:
            # Check if feedback indicates explanation needs improvement
            if feedback.rating < 3 or not feedback.helpful:
                logger.info(f"Low feedback rating for explanation {feedback.explanation_id}")
                # This would trigger explanation improvement process
            
        except Exception as e:
            logger.error(f"Error analyzing feedback: {e}")
    
    async def _collect_user_feedback(self):
        """Collect user feedback continuously"""
        while True:
            try:
                # This would collect actual user feedback
                # For now, simulate feedback collection
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error collecting user feedback: {e}")
                await asyncio.sleep(3600)
    
    async def _analyze_feedback_patterns(self):
        """Analyze feedback patterns for improvement"""
        while True:
            try:
                # Analyze feedback patterns
                if len(self.user_feedback) > 10:
                    await self._analyze_feedback_trends()
                
                await asyncio.sleep(86400)  # Analyze every day
                
            except Exception as e:
                logger.error(f"Error analyzing feedback patterns: {e}")
                await asyncio.sleep(86400)
    
    async def _analyze_feedback_trends(self):
        """Analyze feedback trends"""
        try:
            # Calculate average rating
            avg_rating = sum(f.rating for f in self.user_feedback) / len(self.user_feedback)
            
            # Calculate helpfulness rate
            helpful_rate = sum(1 for f in self.user_feedback if f.helpful) / len(self.user_feedback)
            
            logger.info(f"Feedback trends - Avg rating: {avg_rating:.2f}, Helpful rate: {helpful_rate:.2f}")
            
        except Exception as e:
            logger.error(f"Error analyzing feedback trends: {e}")
    
    def _generate_cache_key(self, decision_type: str, decision_data: Dict[str, Any], 
                          explanation_level: str) -> str:
        """Generate cache key for explanation"""
        try:
            key_data = f"{decision_type}_{explanation_level}_{decision_data.get('decision', 'unknown')}"
            return hashlib.md5(key_data.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Error generating cache key: {e}")
            return "default"
    
    async def _maintain_cache_size(self):
        """Maintain explanation cache size"""
        try:
            if len(self.explanation_cache) > self.config["explanation_cache_size"]:
                # Remove oldest entries
                oldest_keys = list(self.explanation_cache.keys())[:10]
                for key in oldest_keys:
                    del self.explanation_cache[key]
            
        except Exception as e:
            logger.error(f"Error maintaining cache size: {e}")
    
    async def get_explanation_analytics(self) -> Dict[str, Any]:
        """Get explanation analytics"""
        try:
            return {
                "success": True,
                "total_explanations": len(self.explanation_cache),
                "total_feedback": len(self.user_feedback),
                "average_rating": sum(f.rating for f in self.user_feedback) / len(self.user_feedback) if self.user_feedback else 0,
                "helpfulness_rate": sum(1 for f in self.user_feedback if f.helpful) / len(self.user_feedback) if self.user_feedback else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting explanation analytics: {e}")
            return {"success": False, "error": str(e)}
    
    async def shutdown(self):
        """Shutdown the XAI interface"""
        logger.info("Shutting down XAI Interface")
        self.is_initialized = False
        logger.info("XAI Interface shutdown complete")
