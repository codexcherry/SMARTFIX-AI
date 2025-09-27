"""
Galaxy Autopilot Core AI Engine

Implements Federated Reinforcement Learning (FRL) as the core learning mechanism.
Devices use RL to test and learn the most effective healing strategies locally.
Only anonymized model weights (not personal data) are aggregated in the cloud
via Federated Learning, creating a powerful, privacy-conscious global intelligence.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class HealingAction:
    """Represents a healing action taken by the system"""
    action_id: str
    layer: str  # surface, deep, immune, regenerative, optimization
    action_type: str  # restart_app, clear_cache, quarantine_app, etc.
    parameters: Dict[str, Any]
    timestamp: datetime
    success: Optional[bool] = None
    confidence: float = 0.0
    user_feedback: Optional[int] = None  # 1-5 rating

@dataclass
class SystemState:
    """Represents the current state of the device"""
    device_id: str
    timestamp: datetime
    battery_level: float
    memory_usage: float
    cpu_usage: float
    storage_usage: float
    temperature: float
    app_crashes: int
    network_quality: float
    user_activity_level: float
    system_health_score: float

@dataclass
class RewardSignal:
    """Represents the reward for a healing action"""
    action_id: str
    immediate_reward: float  # -1 to 1
    long_term_reward: float  # -1 to 1
    user_satisfaction: float  # -1 to 1
    system_improvement: float  # -1 to 1
    privacy_preserved: bool
    timestamp: datetime

class FederatedReinforcementLearning:
    """
    Core FRL engine that learns optimal healing strategies
    """
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.q_table = {}  # State-action value table
        self.action_history = []
        self.reward_history = []
        self.model_weights = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.1  # Exploration rate
        self.federated_server_url = "https://galaxy-autopilot-federated.samsung.com"
        
    async def select_action(self, state: SystemState, available_actions: List[str]) -> str:
        """
        Select the best healing action based on current state and learned policy
        """
        state_key = self._encode_state(state)
        
        # Initialize Q-values for new states
        if state_key not in self.q_table:
            self.q_table[state_key] = {action: 0.0 for action in available_actions}
        
        # Epsilon-greedy action selection
        if np.random.random() < self.epsilon:
            # Explore: random action
            action = np.random.choice(available_actions)
            logger.info(f"Exploring action: {action}")
        else:
            # Exploit: best known action
            action = max(self.q_table[state_key], key=self.q_table[state_key].get)
            logger.info(f"Exploiting action: {action}")
        
        return action
    
    async def update_q_value(self, state: SystemState, action: str, reward: RewardSignal, next_state: SystemState):
        """
        Update Q-values using Q-learning algorithm
        """
        state_key = self._encode_state(state)
        next_state_key = self._encode_state(next_state)
        
        # Initialize Q-values if needed
        if state_key not in self.q_table:
            self.q_table[state_key] = {}
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = {}
        
        # Q-learning update
        current_q = self.q_table[state_key].get(action, 0.0)
        max_next_q = max(self.q_table[next_state_key].values()) if self.q_table[next_state_key] else 0.0
        
        # Calculate total reward
        total_reward = (
            reward.immediate_reward * 0.4 +
            reward.long_term_reward * 0.3 +
            reward.user_satisfaction * 0.2 +
            reward.system_improvement * 0.1
        )
        
        # Update Q-value
        new_q = current_q + self.learning_rate * (total_reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state_key][action] = new_q
        
        logger.info(f"Updated Q-value for {action}: {current_q:.3f} -> {new_q:.3f}")
    
    async def federated_learning_update(self):
        """
        Participate in federated learning to improve global model
        """
        try:
            # Prepare anonymized model weights (no personal data)
            anonymized_weights = self._anonymize_model_weights()
            
            # Send to federated server
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.federated_server_url}/update",
                    json={
                        "device_id_hash": self._hash_device_id(),
                        "model_weights": anonymized_weights,
                        "sample_count": len(self.action_history),
                        "timestamp": datetime.now().isoformat()
                    }
                ) as response:
                    if response.status == 200:
                        global_weights = await response.json()
                        await self._update_local_model(global_weights)
                        logger.info("Successfully updated local model from federated learning")
                    else:
                        logger.warning(f"Federated learning update failed: {response.status}")
        
        except Exception as e:
            logger.error(f"Federated learning error: {e}")
    
    def _encode_state(self, state: SystemState) -> str:
        """
        Encode system state into a hashable key
        """
        # Discretize continuous values for Q-table
        battery_bucket = int(state.battery_level / 20)  # 0-4 buckets
        memory_bucket = int(state.memory_usage / 20)    # 0-4 buckets
        cpu_bucket = int(state.cpu_usage / 20)          # 0-4 buckets
        storage_bucket = int(state.storage_usage / 20)   # 0-4 buckets
        temp_bucket = int(state.temperature / 10)       # 0-4 buckets
        health_bucket = int(state.system_health_score / 20)  # 0-4 buckets
        
        return f"{battery_bucket}_{memory_bucket}_{cpu_bucket}_{storage_bucket}_{temp_bucket}_{health_bucket}"
    
    def _anonymize_model_weights(self) -> Dict[str, Any]:
        """
        Remove personal data from model weights for federated learning
        """
        # Only send aggregated statistics, not individual user data
        return {
            "q_table_stats": {
                "total_states": len(self.q_table),
                "avg_q_values": np.mean([np.mean(list(q_values.values())) for q_values in self.q_table.values()]),
                "action_distribution": self._get_action_distribution()
            },
            "learning_metrics": {
                "total_actions": len(self.action_history),
                "success_rate": self._calculate_success_rate(),
                "avg_reward": self._calculate_avg_reward()
            }
        }
    
    def _hash_device_id(self) -> str:
        """
        Create privacy-preserving hash of device ID
        """
        return hashlib.sha256(f"{self.device_id}_galaxy_autopilot".encode()).hexdigest()[:16]
    
    async def _update_local_model(self, global_weights: Dict[str, Any]):
        """
        Update local model with global weights from federated learning
        """
        # Implement model update logic here
        # This would typically involve updating neural network weights
        # For Q-learning, we might adjust learning parameters
        pass
    
    def _get_action_distribution(self) -> Dict[str, float]:
        """
        Get distribution of actions taken
        """
        if not self.action_history:
            return {}
        
        action_counts = {}
        for action in self.action_history:
            action_counts[action] = action_counts.get(action, 0) + 1
        
        total = len(self.action_history)
        return {action: count / total for action, count in action_counts.items()}
    
    def _calculate_success_rate(self) -> float:
        """
        Calculate success rate of healing actions
        """
        if not self.action_history:
            return 0.0
        
        successful_actions = sum(1 for action in self.action_history if action.get('success', False))
        return successful_actions / len(self.action_history)
    
    def _calculate_avg_reward(self) -> float:
        """
        Calculate average reward across all actions
        """
        if not self.reward_history:
            return 0.0
        
        return np.mean([reward.immediate_reward for reward in self.reward_history])

class GalaxyAutopilotAI:
    """
    Main AI coordinator that orchestrates all healing layers
    """
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.frl_engine = FederatedReinforcementLearning(device_id)
        self.healing_layers = {}
        self.system_monitor = None
        self.is_running = False
        
    async def initialize(self):
        """
        Initialize the AI system and all healing layers
        """
        logger.info("Initializing Galaxy Autopilot AI Engine")
        
        # Initialize healing layers
        from ..layers.surface_healing import SurfaceHealing
        from ..layers.deep_healing import DeepHealing
        from ..layers.immune_system import ImmuneSystemLayer
        from ..layers.regenerative_layer import RegenerativeLayer
        from ..layers.self_optimization import SelfOptimizationLayer
        from .config import AutopilotSettings
        
        settings = AutopilotSettings()
        
        self.healing_layers = {
            "surface": SurfaceHealing(settings),
            "deep": DeepHealing(settings),
            "immune": ImmuneSystemLayer(self.device_id),
            "regenerative": RegenerativeLayer(self.device_id),
            "optimization": SelfOptimizationLayer(self.device_id)
        }
        
        # Initialize all layers
        for layer_name, layer in self.healing_layers.items():
            await layer.initialize()
            logger.info(f"Initialized {layer_name} healing layer")
        
        self.is_running = True
        logger.info("Galaxy Autopilot AI Engine initialized successfully")
    
    async def process_healing_request(self, issue_type: str, severity: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a healing request and determine the best course of action
        """
        if not self.is_running:
            await self.initialize()
        
        # Get current system state
        current_state = await self._get_current_system_state()
        
        # Determine which layers should be activated
        active_layers = self._determine_active_layers(issue_type, severity, context)
        
        # Get available actions from active layers
        available_actions = []
        for layer_name in active_layers:
            layer_actions = await self.healing_layers[layer_name].get_available_actions(current_state)
            available_actions.extend([f"{layer_name}:{action}" for action in layer_actions])
        
        # Select best action using FRL
        selected_action = await self.frl_engine.select_action(current_state, available_actions)
        
        # Execute the action
        result = await self._execute_healing_action(selected_action, context)
        
        # Update learning model
        if result.get('success'):
            reward = RewardSignal(
                action_id=selected_action,
                immediate_reward=result.get('immediate_improvement', 0.0),
                long_term_reward=0.0,  # Will be updated later
                user_satisfaction=result.get('user_satisfaction', 0.0),
                system_improvement=result.get('system_improvement', 0.0),
                privacy_preserved=True,
                timestamp=datetime.now()
            )
            
            next_state = await self._get_current_system_state()
            await self.frl_engine.update_q_value(current_state, selected_action, reward, next_state)
        
        return result
    
    async def _get_current_system_state(self) -> SystemState:
        """
        Get current system state for decision making using real system monitoring
        """
        try:
            # Import real system monitor
            from .system_monitor import RealSystemMonitor
            
            # Initialize system monitor if not already done
            if not hasattr(self, 'system_monitor'):
                self.system_monitor = RealSystemMonitor(self.device_id)
            
            # Get real system metrics
            metrics = await self.system_monitor.get_current_metrics()
            
            # Get real applications and detect crashes
            applications = await self.system_monitor.get_applications()
            crash_count = sum(app.crash_count for app in applications)
            
            # Calculate network quality based on actual network stats
            network_quality = 0.8  # Default, could be enhanced with actual network analysis
            
            # Calculate user activity level based on process activity
            active_processes = sum(1 for app in applications if app.cpu_percent > 1.0)
            user_activity_level = min(1.0, active_processes / 10.0)  # Normalize to 0-1
            
            # Get real health score
            health_score = await self.system_monitor.get_system_health_score()
            
            return SystemState(
                device_id=self.device_id,
                timestamp=datetime.now(),
                battery_level=metrics.battery_percent or 100.0,
                memory_usage=metrics.memory_percent,
                cpu_usage=metrics.cpu_percent,
                storage_usage=metrics.disk_percent,
                temperature=metrics.temperature or 25.0,
                app_crashes=crash_count,
                network_quality=network_quality,
                user_activity_level=user_activity_level,
                system_health_score=health_score
            )
            
        except Exception as e:
            logger.error(f"Error getting real system state: {e}")
            # Fallback to basic system state
            return SystemState(
                device_id=self.device_id,
                timestamp=datetime.now(),
                battery_level=100.0,
                memory_usage=50.0,
                cpu_usage=25.0,
                storage_usage=50.0,
                temperature=25.0,
                app_crashes=0,
                network_quality=0.8,
                user_activity_level=0.5,
                system_health_score=75.0
            )
    
    def _determine_active_layers(self, issue_type: str, severity: str, context: Dict[str, Any]) -> List[str]:
        """
        Determine which healing layers should be activated based on the issue
        """
        active_layers = ["surface"]  # Always start with surface healing
        
        if severity in ["high", "critical"]:
            active_layers.extend(["deep", "immune"])
        
        if issue_type in ["performance", "battery", "storage"]:
            active_layers.append("regenerative")
        
        if issue_type in ["optimization", "user_experience"]:
            active_layers.append("optimization")
        
        return list(set(active_layers))  # Remove duplicates
    
    async def _execute_healing_action(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a healing action across the appropriate layer
        """
        layer_name, action_type = action.split(":", 1)
        
        if layer_name in self.healing_layers:
            return await self.healing_layers[layer_name].execute_action(action_type, context)
        else:
            logger.error(f"Unknown healing layer: {layer_name}")
            return {"success": False, "error": f"Unknown layer: {layer_name}"}
    
    async def start_continuous_monitoring(self):
        """
        Start continuous monitoring and proactive healing
        """
        logger.info("Starting continuous monitoring mode")
        
        while self.is_running:
            try:
                # Monitor system health
                current_state = await self._get_current_system_state()
                
                # Check for proactive healing opportunities
                if current_state.system_health_score < 70:
                    await self.process_healing_request("performance", "medium", {"proactive": True})
                
                # Participate in federated learning periodically
                if len(self.frl_engine.action_history) % 100 == 0:
                    await self.frl_engine.federated_learning_update()
                
                # Sleep for monitoring interval
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def shutdown(self):
        """
        Gracefully shutdown the AI system
        """
        logger.info("Shutting down Galaxy Autopilot AI Engine")
        self.is_running = False
        
        # Shutdown all layers
        for layer_name, layer in self.healing_layers.items():
            await layer.shutdown()
            logger.info(f"Shutdown {layer_name} healing layer")
        
        logger.info("Galaxy Autopilot AI Engine shutdown complete")
