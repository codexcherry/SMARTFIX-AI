import redis
import json
import pickle
from typing import Any, Optional, Union, Dict, List
from datetime import datetime, timedelta
import logging
from functools import wraps
import hashlib

from .config import settings

logger = logging.getLogger(__name__)

class CacheManager:
    """Redis-based cache manager with fallback to in-memory cache"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self.use_redis = False
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection"""
        # Always use in-memory cache to avoid Redis connection issues
        self.use_redis = False
        logger.info("Using in-memory cache (Redis disabled for compatibility)")
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments"""
        key_parts = [prefix]
        
        # Add args
        for arg in args:
            key_parts.append(str(arg))
        
        # Add kwargs (sorted for consistency)
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
        
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set cache value"""
        try:
            if self.use_redis:
                serialized_value = pickle.dumps(value)
                return self.redis_client.setex(key, expire or 3600, serialized_value)
            else:
                self.memory_cache[key] = {
                    'value': value,
                    'expires_at': datetime.utcnow() + timedelta(seconds=expire or 3600)
                }
                return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache value"""
        try:
            if self.use_redis:
                value = self.redis_client.get(key)
                if value:
                    return pickle.loads(value)
                return None
            else:
                cache_entry = self.memory_cache.get(key)
                if cache_entry and cache_entry['expires_at'] > datetime.utcnow():
                    return cache_entry['value']
                elif cache_entry:
                    # Remove expired entry
                    del self.memory_cache[key]
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete cache value"""
        try:
            if self.use_redis:
                return bool(self.redis_client.delete(key))
            else:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                    return True
                return False
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            if self.use_redis:
                return bool(self.redis_client.exists(key))
            else:
                cache_entry = self.memory_cache.get(key)
                return cache_entry and cache_entry['expires_at'] > datetime.utcnow()
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key"""
        try:
            if self.use_redis:
                return bool(self.redis_client.expire(key, seconds))
            else:
                cache_entry = self.memory_cache.get(key)
                if cache_entry:
                    cache_entry['expires_at'] = datetime.utcnow() + timedelta(seconds=seconds)
                    return True
                return False
        except Exception as e:
            logger.error(f"Cache expire error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            if self.use_redis:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                # Simple pattern matching for memory cache
                deleted_count = 0
                keys_to_delete = []
                for key in self.memory_cache.keys():
                    if pattern.replace('*', '') in key:
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    del self.memory_cache[key]
                    deleted_count += 1
                
                return deleted_count
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if self.use_redis:
                info = self.redis_client.info()
                return {
                    'type': 'redis',
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory_human': info.get('used_memory_human', '0B'),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'total_commands_processed': info.get('total_commands_processed', 0)
                }
            else:
                return {
                    'type': 'memory',
                    'total_keys': len(self.memory_cache),
                    'active_keys': len([k for k, v in self.memory_cache.items() 
                                      if v['expires_at'] > datetime.utcnow()])
                }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {'type': 'unknown', 'error': str(e)}

# Global cache instance
cache_manager = CacheManager()

def cached(prefix: str, expire: int = 3600):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, expire)
            logger.debug(f"Cache miss for key: {cache_key}, stored result")
            
            return result
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern: str):
    """Decorator to invalidate cache after function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            cache_manager.clear_pattern(pattern)
            logger.debug(f"Invalidated cache pattern: {pattern}")
            return result
        return wrapper
    return decorator

# Cache key constants
class CacheKeys:
    USER_PROFILE = "user:profile"
    QUERY_RESULT = "query:result"
    BRAIN_MEMORY = "brain:memory"
    SYSTEM_METRICS = "system:metrics"
    AI_MODEL_RESPONSE = "ai:response"
    SESSION_DATA = "session:data"

# Specific cache functions
def cache_user_profile(user_id: str, profile_data: Dict[str, Any], expire: int = 3600):
    """Cache user profile data"""
    key = f"{CacheKeys.USER_PROFILE}:{user_id}"
    return cache_manager.set(key, profile_data, expire)

def get_cached_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Get cached user profile"""
    key = f"{CacheKeys.USER_PROFILE}:{user_id}"
    return cache_manager.get(key)

def cache_query_result(query_hash: str, result: Dict[str, Any], expire: int = 1800):
    """Cache query processing result"""
    key = f"{CacheKeys.QUERY_RESULT}:{query_hash}"
    return cache_manager.set(key, result, expire)

def get_cached_query_result(query_hash: str) -> Optional[Dict[str, Any]]:
    """Get cached query result"""
    key = f"{CacheKeys.QUERY_RESULT}:{query_hash}"
    return cache_manager.get(key)

def cache_ai_response(prompt_hash: str, response: Dict[str, Any], expire: int = 3600):
    """Cache AI model response"""
    key = f"{CacheKeys.AI_MODEL_RESPONSE}:{prompt_hash}"
    return cache_manager.set(key, response, expire)

def get_cached_ai_response(prompt_hash: str) -> Optional[Dict[str, Any]]:
    """Get cached AI response"""
    key = f"{CacheKeys.AI_MODEL_RESPONSE}:{prompt_hash}"
    return cache_manager.get(key)

def invalidate_user_cache(user_id: str):
    """Invalidate all cache entries for a user"""
    patterns = [
        f"{CacheKeys.USER_PROFILE}:{user_id}",
        f"{CacheKeys.QUERY_RESULT}:*",
        f"{CacheKeys.SESSION_DATA}:{user_id}"
    ]
    for pattern in patterns:
        cache_manager.clear_pattern(pattern)

def invalidate_query_cache():
    """Invalidate all query-related cache"""
    cache_manager.clear_pattern(f"{CacheKeys.QUERY_RESULT}:*")

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return cache_manager.get_stats()
