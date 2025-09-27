"""
Habit Analyzer

AI-powered user habit analysis for predictive app preloading and optimization
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import numpy as np
import json

logger = logging.getLogger(__name__)

@dataclass
class UserHabit:
    """User habit data structure"""
    habit_id: str
    app_package: str
    usage_pattern: str  # daily, weekly, hourly
    frequency: float
    duration: float
    time_of_day: List[int]  # hours
    confidence: float
    last_updated: datetime
    context: Dict[str, Any]

@dataclass
class UsageEvent:
    """App usage event data"""
    event_id: str
    app_package: str
    timestamp: datetime
    duration: float
    context: str  # foreground, background, notification
    user_interaction: bool

class HabitAnalyzer:
    """
    AI-powered habit analyzer for user behavior prediction
    """
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.is_initialized = False
        
        # Habit database
        self.user_habits = {}
        self.usage_events = []
        
        # Analysis configuration
        self.config = {
            "min_events_for_habit": 5,
            "confidence_threshold": 0.7,
            "pattern_window_days": 7,
            "prediction_horizon_hours": 24
        }
        
        # Pattern recognition
        self.pattern_models = {}
        
    async def initialize(self):
        """Initialize the habit analyzer"""
        try:
            logger.info("Initializing Habit Analyzer")
            
            # Load existing habits
            await self._load_existing_habits()
            
            # Initialize pattern recognition models
            await self._initialize_pattern_models()
            
            # Start habit learning process
            await self._start_habit_learning()
            
            self.is_initialized = True
            logger.info("Habit Analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Habit Analyzer: {e}")
            raise
    
    async def _load_existing_habits(self):
        """Load existing user habits from storage"""
        try:
            # This would load from database
            # For now, initialize with empty habits
            self.user_habits = {}
            
            logger.info("Existing habits loaded")
            
        except Exception as e:
            logger.error(f"Failed to load existing habits: {e}")
    
    async def _initialize_pattern_models(self):
        """Initialize pattern recognition models"""
        try:
            # Initialize models for different pattern types
            pattern_types = ["temporal", "frequency", "duration", "context"]
            
            for pattern_type in pattern_types:
                self.pattern_models[pattern_type] = await self._create_pattern_model(pattern_type)
            
            logger.info("Pattern recognition models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize pattern models: {e}")
    
    async def _start_habit_learning(self):
        """Start continuous habit learning process"""
        asyncio.create_task(self._monitor_app_usage())
        asyncio.create_task(self._analyze_patterns())
        asyncio.create_task(self._update_habits())
        
        logger.info("Habit learning process started")
    
    async def learn_habits(self, learning_period: int = 7) -> Dict[str, Any]:
        """Learn user habits from usage data"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Get usage events for the learning period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=learning_period)
            
            relevant_events = [
                event for event in self.usage_events
                if start_date <= event.timestamp <= end_date
            ]
            
            # Analyze patterns for each app
            learned_habits = []
            confidence_scores = []
            
            apps = list(set(event.app_package for event in relevant_events))
            
            for app_package in apps:
                app_events = [event for event in relevant_events if event.app_package == app_package]
                
                if len(app_events) >= self.config["min_events_for_habit"]:
                    habit = await self._analyze_app_habits(app_package, app_events)
                    if habit and habit.confidence >= self.config["confidence_threshold"]:
                        learned_habits.append(habit)
                        confidence_scores.append(habit.confidence)
            
            # Update habit database
            await self._update_habit_database(learned_habits)
            
            return {
                "success": True,
                "learning_period": learning_period,
                "learned_habits": [habit.__dict__ for habit in learned_habits],
                "confidence_scores": confidence_scores,
                "total_events_analyzed": len(relevant_events)
            }
            
        except Exception as e:
            logger.error(f"Error learning habits: {e}")
            return {"success": False, "error": str(e)}
    
    async def predict_app_usage(self) -> Dict[str, Any]:
        """Predict which apps will be used in the next 24 hours"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Get current time context
            current_hour = datetime.now().hour
            current_day = datetime.now().weekday()
            
            # Predict apps for next 24 hours
            predicted_apps = []
            
            for app_package, habit in self.user_habits.items():
                # Check if app is likely to be used based on habit
                usage_probability = await self._calculate_usage_probability(habit, current_hour, current_day)
                
                if usage_probability > 0.5:  # 50% threshold
                    predicted_apps.append({
                        "app_package": app_package,
                        "usage_probability": usage_probability,
                        "predicted_times": await self._predict_usage_times(habit, current_hour),
                        "confidence": habit.confidence
                    })
            
            # Sort by usage probability
            predicted_apps.sort(key=lambda x: x["usage_probability"], reverse=True)
            
            return {
                "success": True,
                "predicted_apps": predicted_apps,
                "prediction_horizon": self.config["prediction_horizon_hours"],
                "total_predictions": len(predicted_apps)
            }
            
        except Exception as e:
            logger.error(f"Error predicting app usage: {e}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_app_habits(self, app_package: str, events: List[UsageEvent]) -> Optional[UserHabit]:
        """Analyze habits for a specific app"""
        try:
            if len(events) < self.config["min_events_for_habit"]:
                return None
            
            # Analyze temporal patterns
            temporal_pattern = await self._analyze_temporal_pattern(events)
            
            # Analyze frequency patterns
            frequency_pattern = await self._analyze_frequency_pattern(events)
            
            # Analyze duration patterns
            duration_pattern = await self._analyze_duration_pattern(events)
            
            # Analyze context patterns
            context_pattern = await self._analyze_context_pattern(events)
            
            # Calculate overall confidence
            confidence = await self._calculate_habit_confidence(
                temporal_pattern, frequency_pattern, duration_pattern, context_pattern
            )
            
            # Create habit object
            habit = UserHabit(
                habit_id=f"habit_{app_package}_{datetime.now().strftime('%Y%m%d')}",
                app_package=app_package,
                usage_pattern=temporal_pattern.get("pattern_type", "daily"),
                frequency=frequency_pattern.get("frequency", 0.0),
                duration=duration_pattern.get("avg_duration", 0.0),
                time_of_day=temporal_pattern.get("peak_hours", []),
                confidence=confidence,
                last_updated=datetime.now(),
                context={
                    "temporal": temporal_pattern,
                    "frequency": frequency_pattern,
                    "duration": duration_pattern,
                    "context": context_pattern
                }
            )
            
            return habit
            
        except Exception as e:
            logger.error(f"Error analyzing app habits: {e}")
            return None
    
    async def _analyze_temporal_pattern(self, events: List[UsageEvent]) -> Dict[str, Any]:
        """Analyze temporal usage patterns"""
        try:
            # Extract hours from events
            hours = [event.timestamp.hour for event in events]
            
            # Calculate hour distribution
            hour_counts = {}
            for hour in hours:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
            # Find peak hours
            peak_hours = sorted(hour_counts.keys(), key=lambda h: hour_counts[h], reverse=True)[:3]
            
            # Determine pattern type
            if len(peak_hours) == 1:
                pattern_type = "hourly"
            elif len(peak_hours) <= 3:
                pattern_type = "daily"
            else:
                pattern_type = "weekly"
            
            return {
                "pattern_type": pattern_type,
                "peak_hours": peak_hours,
                "hour_distribution": hour_counts,
                "consistency": np.std(hours) / np.mean(hours) if hours else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing temporal pattern: {e}")
            return {}
    
    async def _analyze_frequency_pattern(self, events: List[UsageEvent]) -> Dict[str, Any]:
        """Analyze frequency patterns"""
        try:
            # Calculate daily frequency
            days = set(event.timestamp.date() for event in events)
            daily_frequency = len(events) / len(days) if days else 0.0
            
            # Calculate weekly frequency
            weeks = set(event.timestamp.isocalendar()[1] for event in events)
            weekly_frequency = len(events) / len(weeks) if weeks else 0.0
            
            # Calculate frequency consistency
            daily_counts = {}
            for event in events:
                day = event.timestamp.date()
                daily_counts[day] = daily_counts.get(day, 0) + 1
            
            frequency_consistency = 1.0 - (np.std(list(daily_counts.values())) / np.mean(list(daily_counts.values()))) if daily_counts else 0.0
            
            return {
                "frequency": daily_frequency,
                "daily_frequency": daily_frequency,
                "weekly_frequency": weekly_frequency,
                "consistency": frequency_consistency
            }
            
        except Exception as e:
            logger.error(f"Error analyzing frequency pattern: {e}")
            return {}
    
    async def _analyze_duration_pattern(self, events: List[UsageEvent]) -> Dict[str, Any]:
        """Analyze duration patterns"""
        try:
            durations = [event.duration for event in events]
            
            return {
                "avg_duration": np.mean(durations) if durations else 0.0,
                "median_duration": np.median(durations) if durations else 0.0,
                "max_duration": np.max(durations) if durations else 0.0,
                "min_duration": np.min(durations) if durations else 0.0,
                "duration_consistency": 1.0 - (np.std(durations) / np.mean(durations)) if durations else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing duration pattern: {e}")
            return {}
    
    async def _analyze_context_pattern(self, events: List[UsageEvent]) -> Dict[str, Any]:
        """Analyze context patterns"""
        try:
            contexts = [event.context for event in events]
            interactions = [event.user_interaction for event in events]
            
            context_counts = {}
            for context in contexts:
                context_counts[context] = context_counts.get(context, 0) + 1
            
            interaction_rate = sum(interactions) / len(interactions) if interactions else 0.0
            
            return {
                "context_distribution": context_counts,
                "interaction_rate": interaction_rate,
                "primary_context": max(context_counts.keys(), key=lambda k: context_counts[k]) if context_counts else "unknown"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing context pattern: {e}")
            return {}
    
    async def _calculate_habit_confidence(self, temporal: Dict, frequency: Dict, duration: Dict, context: Dict) -> float:
        """Calculate overall habit confidence"""
        try:
            # Weight different pattern types
            temporal_weight = 0.4
            frequency_weight = 0.3
            duration_weight = 0.2
            context_weight = 0.1
            
            # Calculate individual confidences
            temporal_confidence = temporal.get("consistency", 0.0)
            frequency_confidence = frequency.get("consistency", 0.0)
            duration_confidence = duration.get("duration_consistency", 0.0)
            context_confidence = context.get("interaction_rate", 0.0)
            
            # Calculate weighted confidence
            overall_confidence = (
                temporal_confidence * temporal_weight +
                frequency_confidence * frequency_weight +
                duration_confidence * duration_weight +
                context_confidence * context_weight
            )
            
            return min(1.0, max(0.0, overall_confidence))
            
        except Exception as e:
            logger.error(f"Error calculating habit confidence: {e}")
            return 0.0
    
    async def _calculate_usage_probability(self, habit: UserHabit, current_hour: int, current_day: int) -> float:
        """Calculate probability of app usage based on habit"""
        try:
            # Base probability from frequency
            base_probability = habit.frequency / 24.0  # Normalize to hourly probability
            
            # Adjust based on time of day
            if current_hour in habit.time_of_day:
                time_multiplier = 2.0  # Double probability during peak hours
            else:
                time_multiplier = 0.5  # Half probability outside peak hours
            
            # Adjust based on pattern type
            if habit.usage_pattern == "daily":
                pattern_multiplier = 1.0
            elif habit.usage_pattern == "weekly":
                pattern_multiplier = 0.7
            else:  # hourly
                pattern_multiplier = 1.2
            
            # Calculate final probability
            probability = base_probability * time_multiplier * pattern_multiplier * habit.confidence
            
            return min(1.0, max(0.0, probability))
            
        except Exception as e:
            logger.error(f"Error calculating usage probability: {e}")
            return 0.0
    
    async def _predict_usage_times(self, habit: UserHabit, current_hour: int) -> List[int]:
        """Predict specific usage times for the next 24 hours"""
        try:
            predicted_times = []
            
            # Get peak hours from habit
            peak_hours = habit.time_of_day
            
            # Predict usage times for next 24 hours
            for hour in range(24):
                future_hour = (current_hour + hour) % 24
                if future_hour in peak_hours:
                    predicted_times.append(future_hour)
            
            return predicted_times
            
        except Exception as e:
            logger.error(f"Error predicting usage times: {e}")
            return []
    
    async def _create_pattern_model(self, pattern_type: str) -> Dict[str, Any]:
        """Create a pattern recognition model"""
        try:
            # This would create actual ML models
            # For now, return mock model structure
            return {
                "model_type": "statistical",
                "pattern_type": pattern_type,
                "parameters": {},
                "accuracy": 0.85
            }
            
        except Exception as e:
            logger.error(f"Error creating pattern model: {e}")
            return {}
    
    async def _update_habit_database(self, learned_habits: List[UserHabit]):
        """Update habit database with new habits"""
        try:
            for habit in learned_habits:
                self.user_habits[habit.app_package] = habit
            
            logger.info(f"Updated habit database with {len(learned_habits)} new habits")
            
        except Exception as e:
            logger.error(f"Error updating habit database: {e}")
    
    async def _monitor_app_usage(self):
        """Monitor app usage continuously"""
        while True:
            try:
                # This would monitor actual app usage
                # For now, simulate usage events
                await self._simulate_usage_events()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error monitoring app usage: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_patterns(self):
        """Analyze patterns continuously"""
        while True:
            try:
                # Analyze patterns for apps with enough data
                await self._analyze_all_app_patterns()
                
                await asyncio.sleep(3600)  # Analyze every hour
                
            except Exception as e:
                logger.error(f"Error analyzing patterns: {e}")
                await asyncio.sleep(3600)
    
    async def _update_habits(self):
        """Update habits continuously"""
        while True:
            try:
                # Update habits with new data
                await self.learn_habits(1)  # Learn from last day
                
                await asyncio.sleep(86400)  # Update every day
                
            except Exception as e:
                logger.error(f"Error updating habits: {e}")
                await asyncio.sleep(86400)
    
    async def _simulate_usage_events(self):
        """Simulate usage events for testing"""
        try:
            # Simulate some usage events
            apps = ["com.android.chrome", "com.whatsapp", "com.instagram.android"]
            
            for app in apps:
                if np.random.random() < 0.1:  # 10% chance of usage
                    event = UsageEvent(
                        event_id=f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        app_package=app,
                        timestamp=datetime.now(),
                        duration=np.random.uniform(30, 300),  # 30 seconds to 5 minutes
                        context="foreground",
                        user_interaction=True
                    )
                    self.usage_events.append(event)
            
        except Exception as e:
            logger.error(f"Error simulating usage events: {e}")
    
    async def _analyze_all_app_patterns(self):
        """Analyze patterns for all apps"""
        try:
            # Get unique apps from events
            apps = list(set(event.app_package for event in self.usage_events))
            
            for app in apps:
                app_events = [event for event in self.usage_events if event.app_package == app]
                
                if len(app_events) >= self.config["min_events_for_habit"]:
                    habit = await self._analyze_app_habits(app, app_events)
                    if habit and habit.confidence >= self.config["confidence_threshold"]:
                        self.user_habits[app] = habit
            
        except Exception as e:
            logger.error(f"Error analyzing all app patterns: {e}")
    
    async def shutdown(self):
        """Shutdown the habit analyzer"""
        logger.info("Shutting down Habit Analyzer")
        self.is_initialized = False
        logger.info("Habit Analyzer shutdown complete")
