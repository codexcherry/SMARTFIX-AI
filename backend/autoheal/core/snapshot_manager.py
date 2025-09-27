"""
OS Snapshot Manager

Lightweight OS snapshot system for rollback points
"""

import asyncio
import logging
import os
import json
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class SnapshotMetadata:
    """Metadata for OS snapshots"""
    snapshot_id: str
    timestamp: datetime
    system_version: str
    file_count: int
    snapshot_size: int
    is_valid: bool
    description: str
    checksum: str

class OSSnapshotManager:
    """
    Manages OS snapshots for system rollback functionality
    """
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.snapshots_dir = f"./snapshots/{device_id}"
        self.metadata_file = os.path.join(self.snapshots_dir, "metadata.json")
        self.is_initialized = False
        
        # Snapshot configuration
        self.max_snapshots = 10
        self.snapshot_retention_days = 30
        self.critical_paths = [
            "/system",
            "/vendor",
            "/product",
            "/odm"
        ]
    
    async def initialize(self):
        """Initialize the snapshot manager"""
        try:
            logger.info("Initializing OS Snapshot Manager")
            
            # Create snapshots directory
            os.makedirs(self.snapshots_dir, exist_ok=True)
            
            # Load existing metadata
            await self._load_metadata()
            
            # Clean up old snapshots
            await self.cleanup_old_snapshots(self.snapshot_retention_days)
            
            self.is_initialized = True
            logger.info("OS Snapshot Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OS Snapshot Manager: {e}")
            raise
    
    async def _load_metadata(self):
        """Load snapshot metadata from file"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
                    self.snapshots = {
                        snapshot_id: SnapshotMetadata(**snapshot_data)
                        for snapshot_id, snapshot_data in metadata.items()
                    }
            else:
                self.snapshots = {}
            
            logger.info(f"Loaded {len(self.snapshots)} snapshots")
            
        except Exception as e:
            logger.error(f"Error loading snapshot metadata: {e}")
            self.snapshots = {}
    
    async def _save_metadata(self):
        """Save snapshot metadata to file"""
        try:
            metadata = {
                snapshot_id: {
                    **asdict(snapshot),
                    'timestamp': snapshot.timestamp.isoformat()
                }
                for snapshot_id, snapshot in self.snapshots.items()
            }
            
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error saving snapshot metadata: {e}")
    
    async def create_snapshot(self, description: str = "Manual snapshot") -> Dict[str, Any]:
        """Create a new OS snapshot"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            snapshot_id = self._generate_snapshot_id()
            snapshot_dir = os.path.join(self.snapshots_dir, snapshot_id)
            
            logger.info(f"Creating snapshot: {snapshot_id}")
            
            # Create snapshot directory
            os.makedirs(snapshot_dir, exist_ok=True)
            
            # Get system information
            system_version = await self._get_system_version()
            
            # Create snapshot of critical paths
            file_count = 0
            snapshot_size = 0
            
            for path in self.critical_paths:
                if os.path.exists(path):
                    path_snapshot_dir = os.path.join(snapshot_dir, path.lstrip('/'))
                    os.makedirs(path_snapshot_dir, exist_ok=True)
                    
                    count, size = await self._copy_directory(path, path_snapshot_dir)
                    file_count += count
                    snapshot_size += size
            
            # Calculate checksum
            checksum = await self._calculate_snapshot_checksum(snapshot_dir)
            
            # Create metadata
            metadata = SnapshotMetadata(
                snapshot_id=snapshot_id,
                timestamp=datetime.now(),
                system_version=system_version,
                file_count=file_count,
                snapshot_size=snapshot_size,
                is_valid=True,
                description=description,
                checksum=checksum
            )
            
            # Save metadata
            self.snapshots[snapshot_id] = metadata
            await self._save_metadata()
            
            # Clean up old snapshots if needed
            if len(self.snapshots) > self.max_snapshots:
                await self._cleanup_oldest_snapshots()
            
            logger.info(f"Snapshot created successfully: {snapshot_id}")
            
            return {
                "success": True,
                "snapshot_id": snapshot_id,
                "snapshot_size": snapshot_size,
                "file_count": file_count,
                "system_version": system_version,
                "method": "snapshot_manager"
            }
            
        except Exception as e:
            logger.error(f"Error creating snapshot: {e}")
            return {"success": False, "error": str(e)}
    
    async def rollback_to_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """Rollback system to a specific snapshot"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if snapshot_id not in self.snapshots:
                return {"success": False, "error": f"Snapshot {snapshot_id} not found"}
            
            snapshot = self.snapshots[snapshot_id]
            if not snapshot.is_valid:
                return {"success": False, "error": f"Snapshot {snapshot_id} is invalid"}
            
            logger.info(f"Rolling back to snapshot: {snapshot_id}")
            
            snapshot_dir = os.path.join(self.snapshots_dir, snapshot_id)
            
            # Verify snapshot integrity
            if not await self._verify_snapshot_integrity(snapshot_dir, snapshot.checksum):
                return {"success": False, "error": "Snapshot integrity verification failed"}
            
            # Create backup of current state before rollback
            backup_snapshot_id = await self.create_snapshot("Pre-rollback backup")
            if not backup_snapshot_id.get("success"):
                logger.warning("Failed to create pre-rollback backup")
            
            # Perform rollback
            rollback_start = datetime.now()
            
            for path in self.critical_paths:
                if os.path.exists(path):
                    path_snapshot_dir = os.path.join(snapshot_dir, path.lstrip('/'))
                    if os.path.exists(path_snapshot_dir):
                        await self._restore_directory(path_snapshot_dir, path)
            
            rollback_time = (datetime.now() - rollback_start).total_seconds()
            
            logger.info(f"Rollback completed in {rollback_time:.2f} seconds")
            
            return {
                "success": True,
                "snapshot_id": snapshot_id,
                "rollback_time": rollback_time,
                "backup_snapshot_id": backup_snapshot_id.get("snapshot_id"),
                "method": "snapshot_manager"
            }
            
        except Exception as e:
            logger.error(f"Error rolling back to snapshot: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_snapshots(self) -> List[Dict[str, Any]]:
        """Get list of available snapshots"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            snapshots = []
            for snapshot_id, snapshot in self.snapshots.items():
                snapshots.append({
                    "snapshot_id": snapshot_id,
                    "timestamp": snapshot.timestamp.isoformat(),
                    "system_version": snapshot.system_version,
                    "file_count": snapshot.file_count,
                    "snapshot_size": snapshot.snapshot_size,
                    "is_valid": snapshot.is_valid,
                    "description": snapshot.description
                })
            
            # Sort by timestamp (newest first)
            snapshots.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return snapshots
            
        except Exception as e:
            logger.error(f"Error getting snapshots: {e}")
            return []
    
    async def delete_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """Delete a specific snapshot"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if snapshot_id not in self.snapshots:
                return {"success": False, "error": f"Snapshot {snapshot_id} not found"}
            
            snapshot_dir = os.path.join(self.snapshots_dir, snapshot_id)
            
            # Delete snapshot directory
            if os.path.exists(snapshot_dir):
                shutil.rmtree(snapshot_dir)
            
            # Remove from metadata
            del self.snapshots[snapshot_id]
            await self._save_metadata()
            
            logger.info(f"Snapshot deleted: {snapshot_id}")
            
            return {
                "success": True,
                "snapshot_id": snapshot_id,
                "method": "snapshot_manager"
            }
            
        except Exception as e:
            logger.error(f"Error deleting snapshot: {e}")
            return {"success": False, "error": str(e)}
    
    async def cleanup_old_snapshots(self, retention_days: int) -> Dict[str, Any]:
        """Clean up snapshots older than retention period"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            deleted_count = 0
            
            snapshots_to_delete = []
            for snapshot_id, snapshot in self.snapshots.items():
                if snapshot.timestamp < cutoff_date:
                    snapshots_to_delete.append(snapshot_id)
            
            for snapshot_id in snapshots_to_delete:
                result = await self.delete_snapshot(snapshot_id)
                if result.get("success"):
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old snapshots")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "retention_days": retention_days,
                "method": "snapshot_manager"
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old snapshots: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_snapshot_id(self) -> str:
        """Generate a unique snapshot ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"snapshot_{timestamp}_{self.device_id[:8]}"
    
    async def _get_system_version(self) -> str:
        """Get current system version"""
        try:
            # This would typically read from system properties
            return "Android 14 / One UI 6.0"
        except Exception:
            return "Unknown"
    
    async def _copy_directory(self, src: str, dst: str) -> tuple[int, int]:
        """Copy directory and return file count and total size"""
        file_count = 0
        total_size = 0
        
        try:
            for root, dirs, files in os.walk(src):
                for file in files:
                    src_file = os.path.join(root, file)
                    rel_path = os.path.relpath(src_file, src)
                    dst_file = os.path.join(dst, rel_path)
                    
                    # Create destination directory
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(src_file, dst_file)
                    
                    file_count += 1
                    total_size += os.path.getsize(src_file)
                    
        except Exception as e:
            logger.error(f"Error copying directory {src}: {e}")
        
        return file_count, total_size
    
    async def _restore_directory(self, src: str, dst: str):
        """Restore directory from snapshot"""
        try:
            for root, dirs, files in os.walk(src):
                for file in files:
                    src_file = os.path.join(root, file)
                    rel_path = os.path.relpath(src_file, src)
                    dst_file = os.path.join(dst, rel_path)
                    
                    # Create destination directory
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(src_file, dst_file)
                    
        except Exception as e:
            logger.error(f"Error restoring directory {src}: {e}")
    
    async def _calculate_snapshot_checksum(self, snapshot_dir: str) -> str:
        """Calculate checksum for snapshot integrity verification"""
        try:
            hasher = hashlib.sha256()
            
            for root, dirs, files in os.walk(snapshot_dir):
                for file in sorted(files):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'rb') as f:
                        hasher.update(f.read())
            
            return hasher.hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculating snapshot checksum: {e}")
            return ""
    
    async def _verify_snapshot_integrity(self, snapshot_dir: str, expected_checksum: str) -> bool:
        """Verify snapshot integrity using checksum"""
        try:
            if not expected_checksum:
                return True  # Skip verification if no checksum
            
            actual_checksum = await self._calculate_snapshot_checksum(snapshot_dir)
            return actual_checksum == expected_checksum
            
        except Exception as e:
            logger.error(f"Error verifying snapshot integrity: {e}")
            return False
    
    async def _cleanup_oldest_snapshots(self):
        """Clean up oldest snapshots to maintain max count"""
        try:
            if len(self.snapshots) <= self.max_snapshots:
                return
            
            # Sort snapshots by timestamp
            sorted_snapshots = sorted(
                self.snapshots.items(),
                key=lambda x: x[1].timestamp
            )
            
            # Delete oldest snapshots
            snapshots_to_delete = len(self.snapshots) - self.max_snapshots
            for i in range(snapshots_to_delete):
                snapshot_id = sorted_snapshots[i][0]
                await self.delete_snapshot(snapshot_id)
                
        except Exception as e:
            logger.error(f"Error cleaning up oldest snapshots: {e}")
    
    async def shutdown(self):
        """Shutdown the snapshot manager"""
        logger.info("Shutting down OS Snapshot Manager")
        self.is_initialized = False
        logger.info("OS Snapshot Manager shutdown complete")
