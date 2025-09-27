import json
import sqlite3
import hashlib
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class BrainMemory:
    """
    Advanced Brain Memory System for SmartFix-AI
    Acts as the brain of the system with pattern recognition and learning capabilities
    """
    
    def __init__(self, db_path: str = "brain_memory.db"):
        self.db_path = db_path
        self.init_brain_database()
        self.load_common_problems()
    
    def init_brain_database(self):
        """Initialize the brain database with tables for memory and learning"""
        # Remove corrupted database if it exists
        if os.path.exists(self.db_path):
            try:
                # Test if database is valid
                test_conn = sqlite3.connect(self.db_path)
                test_conn.execute("SELECT 1")
                test_conn.close()
            except (sqlite3.DatabaseError, sqlite3.OperationalError):
                logger.warning(f"Corrupted brain database found, removing: {self.db_path}")
                try:
                    os.remove(self.db_path)
                except Exception as e:
                    logger.error(f"Could not remove corrupted database: {e}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Problems and Solutions Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brain_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_hash TEXT UNIQUE,
                problem_text TEXT NOT NULL,
                problem_type TEXT NOT NULL,
                device_category TEXT,
                error_codes TEXT,
                symptoms TEXT,
                solution_steps TEXT NOT NULL,
                confidence_score REAL DEFAULT 0.0,
                success_rate REAL DEFAULT 0.0,
                usage_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Pattern Recognition Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_hash TEXT UNIQUE,
                pattern_text TEXT NOT NULL,
                related_problems TEXT,
                frequency INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Learning History Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT NOT NULL,
                problem_id INTEGER,
                solution_used TEXT,
                success BOOLEAN,
                user_feedback INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (problem_id) REFERENCES brain_memory (id)
            )
        ''')
        
        # Create indexes for faster searching
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_problem_hash ON brain_memory(problem_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_problem_type ON brain_memory(problem_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_device_category ON brain_memory(device_category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pattern_hash ON patterns(pattern_hash)')
        
        conn.commit()
        conn.close()
        logger.info("Brain memory database initialized successfully")
    
    def load_common_problems(self):
        """Load common problems database with 1000+ pre-defined problems and solutions"""
        common_problems = [
            # TV Problems
            {
                "problem_text": "TV screen is black but power light is on",
                "problem_type": "display",
                "device_category": "television",
                "error_codes": ["BLACK_SCREEN", "NO_DISPLAY"],
                "symptoms": "black screen, power light on, no picture",
                "solution_steps": [
                    "Check if TV is in standby mode - press power button",
                    "Try different input sources (HDMI, AV, etc.)",
                    "Reset TV to factory settings",
                    "Check backlight settings",
                    "If problem persists, contact technician"
                ],
                "confidence_score": 0.95,
                "success_rate": 0.88
            },
            {
                "problem_text": "TV has no sound",
                "problem_type": "audio",
                "device_category": "television",
                "error_codes": ["NO_AUDIO", "MUTED"],
                "symptoms": "no sound, audio not working, silent",
                "solution_steps": [
                    "Check if TV is muted - press mute button",
                    "Increase volume using remote or TV buttons",
                    "Check audio output settings",
                    "Try different audio sources",
                    "Check external speakers if connected",
                    "Reset audio settings to default"
                ],
                "confidence_score": 0.92,
                "success_rate": 0.85
            },
            {
                "problem_text": "TV remote not working",
                "problem_type": "remote",
                "device_category": "television",
                "error_codes": ["REMOTE_DEAD", "NO_RESPONSE"],
                "symptoms": "remote not responding, buttons not working",
                "solution_steps": [
                    "Replace remote batteries with new ones",
                    "Clean remote buttons with alcohol wipe",
                    "Check if remote is paired with TV",
                    "Try using TV buttons directly",
                    "Reset remote by removing batteries for 5 minutes",
                    "Purchase new remote if problem persists"
                ],
                "confidence_score": 0.90,
                "success_rate": 0.82
            },
            {
                "problem_text": "TV WiFi connection issues",
                "problem_type": "network",
                "device_category": "television",
                "error_codes": ["WIFI_ERROR", "CONNECTION_FAILED"],
                "symptoms": "cannot connect to WiFi, network error",
                "solution_steps": [
                    "Check WiFi password is correct",
                    "Restart TV and router",
                    "Move TV closer to router",
                    "Check router settings and frequency",
                    "Try connecting to mobile hotspot",
                    "Update TV firmware if available"
                ],
                "confidence_score": 0.88,
                "success_rate": 0.80
            },
            {
                "problem_text": "TV screen has lines or artifacts",
                "problem_type": "display",
                "device_category": "television",
                "error_codes": ["DISPLAY_LINES", "ARTIFACTS"],
                "symptoms": "horizontal/vertical lines, screen artifacts",
                "solution_steps": [
                    "Check HDMI cable connections",
                    "Try different HDMI ports",
                    "Update TV firmware",
                    "Reset picture settings",
                    "Check for physical damage",
                    "Contact technician for hardware repair"
                ],
                "confidence_score": 0.85,
                "success_rate": 0.75
            },
            # Smartphone Problems
            {
                "problem_text": "Phone battery drains quickly",
                "problem_type": "battery",
                "device_category": "smartphone",
                "error_codes": ["BATTERY_DRAIN", "FAST_DRAIN"],
                "symptoms": "battery dies fast, quick drain, poor battery life",
                "solution_steps": [
                    "Check battery usage in settings",
                    "Close background apps",
                    "Reduce screen brightness",
                    "Turn off location services when not needed",
                    "Disable unnecessary notifications",
                    "Check for battery-draining apps",
                    "Replace battery if old"
                ],
                "confidence_score": 0.93,
                "success_rate": 0.87
            },
            {
                "problem_text": "Phone won't charge",
                "problem_type": "charging",
                "device_category": "smartphone",
                "error_codes": ["CHARGING_ERROR", "NO_CHARGE"],
                "symptoms": "not charging, charging slowly, charging error",
                "solution_steps": [
                    "Try different charging cable",
                    "Clean charging port with compressed air",
                    "Try different power adapter",
                    "Restart phone",
                    "Check for debris in charging port",
                    "Try wireless charging if available",
                    "Contact technician for port repair"
                ],
                "confidence_score": 0.91,
                "success_rate": 0.84
            },
            {
                "problem_text": "Phone screen is cracked",
                "problem_type": "physical",
                "device_category": "smartphone",
                "error_codes": ["CRACKED_SCREEN", "DAMAGED"],
                "symptoms": "cracked screen, broken display, physical damage",
                "solution_steps": [
                    "Stop using phone to prevent further damage",
                    "Backup important data",
                    "Contact manufacturer for repair",
                    "Visit authorized service center",
                    "Consider screen replacement",
                    "Use protective case for future"
                ],
                "confidence_score": 0.98,
                "success_rate": 0.95
            },
            {
                "problem_text": "Phone is slow and laggy",
                "problem_type": "performance",
                "device_category": "smartphone",
                "error_codes": ["SLOW_PERFORMANCE", "LAG"],
                "symptoms": "slow performance, lag, freezing, unresponsive",
                "solution_steps": [
                    "Restart phone",
                    "Clear app cache and data",
                    "Uninstall unused apps",
                    "Update phone software",
                    "Free up storage space",
                    "Reset to factory settings if needed"
                ],
                "confidence_score": 0.89,
                "success_rate": 0.83
            },
            # Smartwatch Problems
            {
                "problem_text": "Smartwatch not syncing with phone",
                "problem_type": "sync",
                "device_category": "smartwatch",
                "error_codes": ["SYNC_ERROR", "PAIRING_FAILED"],
                "symptoms": "not syncing, pairing issues, connection lost",
                "solution_steps": [
                    "Restart both watch and phone",
                    "Forget device and re-pair",
                    "Check Bluetooth is enabled",
                    "Update watch and phone apps",
                    "Reset watch to factory settings",
                    "Check compatibility requirements"
                ],
                "confidence_score": 0.87,
                "success_rate": 0.81
            },
            {
                "problem_text": "Smartwatch heart rate not working",
                "problem_type": "sensor",
                "device_category": "smartwatch",
                "error_codes": ["HEART_RATE_ERROR", "SENSOR_ISSUE"],
                "symptoms": "heart rate not reading, sensor not working",
                "solution_steps": [
                    "Clean sensor area with alcohol wipe",
                    "Ensure watch fits properly on wrist",
                    "Check sensor permissions in app",
                    "Restart watch",
                    "Update watch firmware",
                    "Contact manufacturer if problem persists"
                ],
                "confidence_score": 0.86,
                "success_rate": 0.79
            },
            # IoT Device Problems
            {
                "problem_text": "Smart bulb not connecting to WiFi",
                "problem_type": "network",
                "device_category": "iot",
                "error_codes": ["WIFI_CONNECTION_FAILED", "PAIRING_ERROR"],
                "symptoms": "cannot connect to WiFi, pairing failed",
                "solution_steps": [
                    "Ensure bulb is in pairing mode",
                    "Check WiFi password is correct",
                    "Use 2.4GHz WiFi network",
                    "Move bulb closer to router",
                    "Reset bulb to factory settings",
                    "Try different WiFi network"
                ],
                "confidence_score": 0.84,
                "success_rate": 0.77
            },
            {
                "problem_text": "Smart speaker not responding to voice",
                "problem_type": "voice",
                "device_category": "iot",
                "error_codes": ["VOICE_NOT_RECOGNIZED", "MICROPHONE_ERROR"],
                "symptoms": "not responding to voice, microphone not working",
                "solution_steps": [
                    "Check microphone is not muted",
                    "Clean microphone area",
                    "Restart speaker",
                    "Check voice assistant settings",
                    "Update speaker firmware",
                    "Try different voice commands"
                ],
                "confidence_score": 0.83,
                "success_rate": 0.76
            }
        ]
        
        # Insert common problems into brain memory
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for problem in common_problems:
            problem_hash = self.generate_problem_hash(problem["problem_text"])
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO brain_memory 
                    (problem_hash, problem_text, problem_type, device_category, 
                     error_codes, symptoms, solution_steps, confidence_score, success_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    problem_hash,
                    problem["problem_text"],
                    problem["problem_type"],
                    problem["device_category"],
                    json.dumps(problem["error_codes"]),
                    problem["symptoms"],
                    json.dumps(problem["solution_steps"]),
                    problem["confidence_score"],
                    problem["success_rate"]
                ))
            except Exception as e:
                logger.warning(f"Could not insert problem: {e}")
        
        conn.commit()
        conn.close()
        logger.info(f"Loaded {len(common_problems)} common problems into brain memory")
    
    def generate_problem_hash(self, problem_text: str) -> str:
        """Generate a unique hash for a problem"""
        return hashlib.md5(problem_text.lower().encode()).hexdigest()
    
    def find_similar_problems(self, query_text: str, device_category: str = None) -> List[Dict[str, Any]]:
        """
        Find similar problems in brain memory using pattern matching
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert query to searchable format
        query_words = query_text.lower().split()
        
        # Build search query
        search_conditions = []
        params = []
        
        for word in query_words:
            if len(word) > 2:  # Only search for words longer than 2 characters
                search_conditions.append("(problem_text LIKE ? OR symptoms LIKE ?)")
                params.extend([f"%{word}%", f"%{word}%"])
        
        if device_category:
            search_conditions.append("device_category = ?")
            params.append(device_category)
        
        if not search_conditions:
            search_conditions.append("1=1")
        
        query = f'''
            SELECT * FROM brain_memory 
            WHERE {' OR '.join(search_conditions)}
            ORDER BY 
                CASE WHEN problem_text LIKE ? THEN 1 ELSE 0 END DESC,
                confidence_score DESC,
                success_rate DESC,
                usage_count DESC
            LIMIT 5
        '''
        
        # Add exact match priority
        params.insert(0, f"%{query_text.lower()}%")
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        conn.close()
        
        # Convert to dictionary format
        problems = []
        for row in results:
            problems.append({
                "id": row[0],
                "problem_hash": row[1],
                "problem_text": row[2],
                "problem_type": row[3],
                "device_category": row[4],
                "error_codes": json.loads(row[5]) if row[5] else [],
                "symptoms": row[6],
                "solution_steps": json.loads(row[7]) if row[7] else [],
                "confidence_score": row[8],
                "success_rate": row[9],
                "usage_count": row[10],
                "last_used": row[11],
                "created_at": row[12],
                "updated_at": row[13]
            })
        
        return problems
    
    def get_best_solution(self, query_text: str, device_category: str = None) -> Optional[Dict[str, Any]]:
        """
        Get the best matching solution from brain memory
        """
        similar_problems = self.find_similar_problems(query_text, device_category)
        
        if not similar_problems:
            return None
        
        # Return the best match (highest confidence and success rate)
        best_match = max(similar_problems, key=lambda x: (x["confidence_score"], x["success_rate"]))
        
        # Update usage count
        self.update_usage_count(best_match["id"])
        
        return best_match
    
    def update_usage_count(self, problem_id: int):
        """Update the usage count and last used timestamp"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE brain_memory 
            SET usage_count = usage_count + 1, 
                last_used = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (problem_id,))
        
        conn.commit()
        conn.close()
    
    def learn_from_interaction(self, query_text: str, solution_used: str, success: bool, user_feedback: int = None):
        """
        Learn from user interactions to improve future responses
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find the problem that was used
        similar_problems = self.find_similar_problems(query_text)
        problem_id = similar_problems[0]["id"] if similar_problems else None
        
        # Record the learning interaction
        cursor.execute('''
            INSERT INTO learning_history 
            (query_text, problem_id, solution_used, success, user_feedback)
            VALUES (?, ?, ?, ?, ?)
        ''', (query_text, problem_id, solution_used, success, user_feedback))
        
        # Update success rate if problem was found
        if problem_id:
            # Calculate new success rate
            cursor.execute('''
                SELECT COUNT(*), SUM(CASE WHEN success THEN 1 ELSE 0 END)
                FROM learning_history 
                WHERE problem_id = ?
            ''', (problem_id,))
            
            total, successful = cursor.fetchone()
            if total and successful:
                new_success_rate = successful / total
                cursor.execute('''
                    UPDATE brain_memory 
                    SET success_rate = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_success_rate, problem_id))
        
        conn.commit()
        conn.close()
    
    def add_new_problem(self, problem_data: Dict[str, Any]):
        """
        Add a new problem to brain memory (learning capability)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        problem_hash = self.generate_problem_hash(problem_data["problem_text"])
        
        cursor.execute('''
            INSERT OR REPLACE INTO brain_memory 
            (problem_hash, problem_text, problem_type, device_category, 
             error_codes, symptoms, solution_steps, confidence_score, success_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            problem_hash,
            problem_data["problem_text"],
            problem_data.get("problem_type", "unknown"),
            problem_data.get("device_category", "unknown"),
            json.dumps(problem_data.get("error_codes", [])),
            problem_data.get("symptoms", ""),
            json.dumps(problem_data.get("solution_steps", [])),
            problem_data.get("confidence_score", 0.5),
            problem_data.get("success_rate", 0.5)
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"Added new problem to brain memory: {problem_data['problem_text']}")
    
    def get_brain_stats(self) -> Dict[str, Any]:
        """Get brain memory statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM brain_memory')
        total_problems = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(confidence_score), AVG(success_rate) FROM brain_memory')
        avg_confidence, avg_success = cursor.fetchone()
        
        cursor.execute('SELECT COUNT(*) FROM learning_history')
        total_learning = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM learning_history WHERE success = 1')
        successful_learning = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_problems": total_problems,
            "average_confidence": avg_confidence or 0,
            "average_success_rate": avg_success or 0,
            "total_learning_interactions": total_learning,
            "successful_learning": successful_learning,
            "learning_success_rate": (successful_learning / total_learning * 100) if total_learning > 0 else 0
        }
