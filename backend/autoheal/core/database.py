"""
Real Database System for Galaxy Autopilot

Implements actual SQLite database with real tables for storing system metrics,
healing actions, ML models, and user behavior data.
"""

import asyncio
import logging
import sqlite3
import json
import pickle
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import os

logger = logging.getLogger(__name__)

@dataclass
class HealingAction:
    """Healing action record"""
    id: Optional[int]
    action_type: str
    layer: str
    target: str
    parameters: Dict[str, Any]
    success: bool
    timestamp: datetime
    duration_ms: int
    improvement_score: float
    user_feedback: Optional[int]
    error_message: Optional[str]

@dataclass
class SystemSnapshot:
    """System snapshot record"""
    id: Optional[int]
    timestamp: datetime
    metrics_data: Dict[str, Any]
    health_score: float
    issues_detected: List[Dict[str, Any]]
    healing_actions_taken: List[str]

@dataclass
class MLModel:
    """ML model record"""
    id: Optional[int]
    model_name: str
    model_type: str
    version: str
    accuracy: float
    training_data_size: int
    last_trained: datetime
    model_data: bytes
    is_active: bool

@dataclass
class UserBehavior:
    """User behavior record"""
    id: Optional[int]
    timestamp: datetime
    action_type: str
    context: Dict[str, Any]
    device_state: Dict[str, Any]
    user_feedback: Optional[int]
    success: bool

class GalaxyAutopilotDatabase:
    """
    Real database system for Galaxy Autopilot
    """
    
    def __init__(self, db_path: str = "./galaxy_autopilot.db"):
        self.db_path = Path(db_path)
        self.connection = None
        self.is_initialized = False
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize the database with all required tables"""
        try:
            self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            # Create tables
            await self._create_tables()
            
            # Create indexes for better performance
            await self._create_indexes()
            
            self.is_initialized = True
            logger.info(f"Database initialized successfully: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def _create_tables(self):
        """Create all required database tables"""
        cursor = self.connection.cursor()
        
        # System metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                device_id TEXT NOT NULL,
                cpu_percent REAL,
                memory_percent REAL,
                disk_percent REAL,
                temperature REAL,
                battery_percent REAL,
                network_bytes_sent INTEGER,
                network_bytes_recv INTEGER,
                processes_count INTEGER,
                health_score REAL,
                metrics_data TEXT,  -- JSON data
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Healing actions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS healing_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                layer TEXT NOT NULL,
                target TEXT NOT NULL,
                parameters TEXT,  -- JSON data
                success BOOLEAN NOT NULL,
                timestamp DATETIME NOT NULL,
                duration_ms INTEGER,
                improvement_score REAL,
                user_feedback INTEGER,
                error_message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # System snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                device_id TEXT NOT NULL,
                metrics_data TEXT,  -- JSON data
                health_score REAL,
                issues_detected TEXT,  -- JSON data
                healing_actions_taken TEXT,  -- JSON data
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ML models table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ml_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL UNIQUE,
                model_type TEXT NOT NULL,
                version TEXT NOT NULL,
                accuracy REAL,
                training_data_size INTEGER,
                last_trained DATETIME NOT NULL,
                model_data BLOB,  -- Pickled model data
                is_active BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User behavior table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_behavior (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                device_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                context TEXT,  -- JSON data
                device_state TEXT,  -- JSON data
                user_feedback INTEGER,
                success BOOLEAN,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Process information table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS process_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                device_id TEXT NOT NULL,
                pid INTEGER NOT NULL,
                name TEXT NOT NULL,
                cpu_percent REAL,
                memory_percent REAL,
                memory_rss INTEGER,
                memory_vms INTEGER,
                status TEXT,
                cmdline TEXT,  -- JSON data
                username TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Application crashes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_crashes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                device_id TEXT NOT NULL,
                app_name TEXT NOT NULL,
                pid INTEGER,
                crash_reason TEXT,
                stack_trace TEXT,
                memory_usage REAL,
                cpu_usage REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Performance predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                device_id TEXT NOT NULL,
                prediction_type TEXT NOT NULL,
                target TEXT NOT NULL,
                predicted_value REAL,
                confidence REAL,
                time_horizon INTEGER,
                actual_value REAL,
                accuracy REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # System events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                device_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                context TEXT,  -- JSON data
                resolved BOOLEAN DEFAULT FALSE,
                resolution_action TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
        logger.info("Database tables created successfully")
    
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        cursor = self.connection.cursor()
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_system_metrics_device ON system_metrics(device_id)",
            "CREATE INDEX IF NOT EXISTS idx_healing_actions_timestamp ON healing_actions(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_healing_actions_type ON healing_actions(action_type)",
            "CREATE INDEX IF NOT EXISTS idx_healing_actions_layer ON healing_actions(layer)",
            "CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON system_snapshots(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_snapshots_device ON system_snapshots(device_id)",
            "CREATE INDEX IF NOT EXISTS idx_ml_models_name ON ml_models(model_name)",
            "CREATE INDEX IF NOT EXISTS idx_ml_models_active ON ml_models(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_user_behavior_timestamp ON user_behavior(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_user_behavior_device ON user_behavior(device_id)",
            "CREATE INDEX IF NOT EXISTS idx_process_info_timestamp ON process_info(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_process_info_pid ON process_info(pid)",
            "CREATE INDEX IF NOT EXISTS idx_app_crashes_timestamp ON app_crashes(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_app_crashes_app ON app_crashes(app_name)",
            "CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON performance_predictions(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_predictions_type ON performance_predictions(prediction_type)",
            "CREATE INDEX IF NOT EXISTS idx_system_events_timestamp ON system_events(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_system_events_type ON system_events(event_type)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        self.connection.commit()
        logger.info("Database indexes created successfully")
    
    async def save_system_metrics(self, device_id: str, metrics_data: Dict[str, Any], health_score: float):
        """Save system metrics to database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO system_metrics 
                (timestamp, device_id, cpu_percent, memory_percent, disk_percent, 
                 temperature, battery_percent, network_bytes_sent, network_bytes_recv, 
                 processes_count, health_score, metrics_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now(),
                device_id,
                metrics_data.get('cpu_percent', 0),
                metrics_data.get('memory_percent', 0),
                metrics_data.get('disk_percent', 0),
                metrics_data.get('temperature'),
                metrics_data.get('battery_percent'),
                metrics_data.get('network_bytes_sent', 0),
                metrics_data.get('network_bytes_recv', 0),
                metrics_data.get('processes_count', 0),
                health_score,
                json.dumps(metrics_data)
            ))
            self.connection.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"Error saving system metrics: {e}")
            return None
    
    async def save_healing_action(self, action: HealingAction) -> int:
        """Save healing action to database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO healing_actions 
                (action_type, layer, target, parameters, success, timestamp, 
                 duration_ms, improvement_score, user_feedback, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                action.action_type,
                action.layer,
                action.target,
                json.dumps(action.parameters),
                action.success,
                action.timestamp,
                action.duration_ms,
                action.improvement_score,
                action.user_feedback,
                action.error_message
            ))
            self.connection.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"Error saving healing action: {e}")
            return -1
    
    async def save_system_snapshot(self, device_id: str, snapshot: SystemSnapshot) -> int:
        """Save system snapshot to database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO system_snapshots 
                (timestamp, device_id, metrics_data, health_score, issues_detected, healing_actions_taken)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                snapshot.timestamp,
                device_id,
                json.dumps(snapshot.metrics_data),
                snapshot.health_score,
                json.dumps(snapshot.issues_detected),
                json.dumps(snapshot.healing_actions_taken)
            ))
            self.connection.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"Error saving system snapshot: {e}")
            return -1
    
    async def save_ml_model(self, model: MLModel) -> int:
        """Save ML model to database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO ml_models 
                (model_name, model_type, version, accuracy, training_data_size, 
                 last_trained, model_data, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                model.model_name,
                model.model_type,
                model.version,
                model.accuracy,
                model.training_data_size,
                model.last_trained,
                model.model_data,
                model.is_active
            ))
            self.connection.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"Error saving ML model: {e}")
            return -1
    
    async def save_user_behavior(self, device_id: str, behavior: UserBehavior) -> int:
        """Save user behavior to database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO user_behavior 
                (timestamp, device_id, action_type, context, device_state, user_feedback, success)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                behavior.timestamp,
                device_id,
                behavior.action_type,
                json.dumps(behavior.context),
                json.dumps(behavior.device_state),
                behavior.user_feedback,
                behavior.success
            ))
            self.connection.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"Error saving user behavior: {e}")
            return -1
    
    async def get_healing_actions(self, limit: int = 100, layer: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get healing actions from database"""
        try:
            cursor = self.connection.cursor()
            
            if layer:
                cursor.execute("""
                    SELECT * FROM healing_actions 
                    WHERE layer = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (layer, limit))
            else:
                cursor.execute("""
                    SELECT * FROM healing_actions 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
            
            rows = cursor.fetchall()
            actions = []
            
            for row in rows:
                action = dict(row)
                action['parameters'] = json.loads(action['parameters']) if action['parameters'] else {}
                actions.append(action)
            
            return actions
            
        except Exception as e:
            logger.error(f"Error getting healing actions: {e}")
            return []
    
    async def get_system_metrics_history(self, device_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get system metrics history"""
        try:
            cursor = self.connection.cursor()
            since = datetime.now() - timedelta(hours=hours)
            
            cursor.execute("""
                SELECT * FROM system_metrics 
                WHERE device_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            """, (device_id, since))
            
            rows = cursor.fetchall()
            metrics = []
            
            for row in rows:
                metric = dict(row)
                metric['metrics_data'] = json.loads(metric['metrics_data']) if metric['metrics_data'] else {}
                metrics.append(metric)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting system metrics history: {e}")
            return []
    
    async def get_ml_model(self, model_name: str) -> Optional[MLModel]:
        """Get ML model from database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM ml_models 
                WHERE model_name = ? AND is_active = TRUE
                ORDER BY last_trained DESC
                LIMIT 1
            """, (model_name,))
            
            row = cursor.fetchone()
            if row:
                return MLModel(
                    id=row['id'],
                    model_name=row['model_name'],
                    model_type=row['model_type'],
                    version=row['version'],
                    accuracy=row['accuracy'],
                    training_data_size=row['training_data_size'],
                    last_trained=datetime.fromisoformat(row['last_trained']),
                    model_data=row['model_data'],
                    is_active=bool(row['is_active'])
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting ML model: {e}")
            return None
    
    async def get_healing_success_rate(self, layer: Optional[str] = None, days: int = 7) -> float:
        """Get healing action success rate"""
        try:
            cursor = self.connection.cursor()
            since = datetime.now() - timedelta(days=days)
            
            if layer:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                    FROM healing_actions 
                    WHERE layer = ? AND timestamp >= ?
                """, (layer, since))
            else:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                    FROM healing_actions 
                    WHERE timestamp >= ?
                """, (since,))
            
            row = cursor.fetchone()
            if row and row['total'] > 0:
                return (row['successful'] / row['total']) * 100
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting healing success rate: {e}")
            return 0.0
    
    async def cleanup_old_data(self, days: int = 30):
        """Clean up old data to prevent database bloat"""
        try:
            cursor = self.connection.cursor()
            cutoff_date = datetime.now() - timedelta(days=days)
            
            tables_to_cleanup = [
                'system_metrics',
                'healing_actions', 
                'system_snapshots',
                'user_behavior',
                'process_info',
                'app_crashes',
                'performance_predictions',
                'system_events'
            ]
            
            for table in tables_to_cleanup:
                cursor.execute(f"DELETE FROM {table} WHERE timestamp < ?", (cutoff_date,))
                deleted = cursor.rowcount
                if deleted > 0:
                    logger.info(f"Cleaned up {deleted} old records from {table}")
            
            self.connection.commit()
            
            # Vacuum database to reclaim space
            cursor.execute("VACUUM")
            logger.info("Database cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during database cleanup: {e}")
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            cursor = self.connection.cursor()
            
            stats = {}
            tables = [
                'system_metrics', 'healing_actions', 'system_snapshots',
                'ml_models', 'user_behavior', 'process_info', 'app_crashes',
                'performance_predictions', 'system_events'
            ]
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                stats[table] = count
            
            # Database file size
            stats['database_size_mb'] = self.db_path.stat().st_size / (1024 * 1024)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

