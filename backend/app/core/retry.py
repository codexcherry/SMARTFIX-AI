import asyncio
import time
import logging
from typing import Any, Callable, Optional, Dict, List
from functools import wraps
from datetime import datetime, timedelta
import random
from enum import Enum

from .config import settings

logger = logging.getLogger(__name__)

class RetryStrategy(Enum):
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Circuit is open, failing fast
    HALF_OPEN = "half_open"  # Testing if service is back

class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_retries: int = settings.MAX_RETRIES,
        base_delay: float = settings.RETRY_DELAY,
        max_delay: float = 60.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        jitter: bool = True,
        backoff_factor: float = 2.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.strategy = strategy
        self.jitter = jitter
        self.backoff_factor = backoff_factor

class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
    
    def can_execute(self) -> bool:
        """Check if operation can be executed"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    def on_success(self):
        """Handle successful execution"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 2:  # Require 2 successes to close
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info("Circuit breaker closed - service recovered")
    
    def on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
        
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker reopened after failure in half-open state")

class RetryManager:
    """Manages retry logic and circuit breakers"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_configs: Dict[str, RetryConfig] = {}
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]
    
    def get_retry_config(self, service_name: str) -> RetryConfig:
        """Get retry configuration for service"""
        if service_name not in self.retry_configs:
            self.retry_configs[service_name] = RetryConfig()
        return self.retry_configs[service_name]
    
    def calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate delay for retry attempt"""
        if config.strategy == RetryStrategy.FIXED:
            delay = config.base_delay
        elif config.strategy == RetryStrategy.LINEAR:
            delay = config.base_delay * attempt
        else:  # Exponential
            delay = config.base_delay * (config.backoff_factor ** (attempt - 1))
        
        # Apply jitter to prevent thundering herd
        if config.jitter:
            jitter = random.uniform(0, 0.1 * delay)
            delay += jitter
        
        return min(delay, config.max_delay)

# Global retry manager
retry_manager = RetryManager()

def retry_with_circuit_breaker(
    service_name: str,
    max_retries: Optional[int] = None,
    base_delay: Optional[float] = None,
    strategy: Optional[RetryStrategy] = None,
    exceptions: tuple = (Exception,)
):
    """Decorator for retry with circuit breaker pattern"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            circuit_breaker = retry_manager.get_circuit_breaker(service_name)
            config = retry_manager.get_retry_config(service_name)
            
            # Override config if provided
            if max_retries is not None:
                config.max_retries = max_retries
            if base_delay is not None:
                config.base_delay = base_delay
            if strategy is not None:
                config.strategy = strategy
            
            # Check circuit breaker
            if not circuit_breaker.can_execute():
                raise Exception(f"Circuit breaker is open for {service_name}")
            
            last_exception = None
            
            for attempt in range(1, config.max_retries + 2):  # +2 for initial attempt
                try:
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    # Success - update circuit breaker
                    circuit_breaker.on_success()
                    return result
                
                except exceptions as e:
                    last_exception = e
                    circuit_breaker.on_failure()
                    
                    if attempt <= config.max_retries:
                        delay = retry_manager.calculate_delay(attempt, config)
                        logger.warning(
                            f"Attempt {attempt} failed for {service_name}: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"All {config.max_retries + 1} attempts failed for {service_name}: {e}"
                        )
                        break
            
            # All retries exhausted
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            circuit_breaker = retry_manager.get_circuit_breaker(service_name)
            config = retry_manager.get_retry_config(service_name)
            
            # Override config if provided
            if max_retries is not None:
                config.max_retries = max_retries
            if base_delay is not None:
                config.base_delay = base_delay
            if strategy is not None:
                config.strategy = strategy
            
            # Check circuit breaker
            if not circuit_breaker.can_execute():
                raise Exception(f"Circuit breaker is open for {service_name}")
            
            last_exception = None
            
            for attempt in range(1, config.max_retries + 2):  # +2 for initial attempt
                try:
                    result = func(*args, **kwargs)
                    
                    # Success - update circuit breaker
                    circuit_breaker.on_success()
                    return result
                
                except exceptions as e:
                    last_exception = e
                    circuit_breaker.on_failure()
                    
                    if attempt <= config.max_retries:
                        delay = retry_manager.calculate_delay(attempt, config)
                        logger.warning(
                            f"Attempt {attempt} failed for {service_name}: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {config.max_retries + 1} attempts failed for {service_name}: {e}"
                        )
                        break
            
            # All retries exhausted
            raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Predefined retry decorators for common services
def retry_ai_service(func: Callable) -> Callable:
    """Retry decorator for AI service calls"""
    return retry_with_circuit_breaker(
        "ai_service",
        max_retries=3,
        base_delay=1.0,
        strategy=RetryStrategy.EXPONENTIAL,
        exceptions=(Exception,)
    )(func)

def retry_external_api(func: Callable) -> Callable:
    """Retry decorator for external API calls"""
    return retry_with_circuit_breaker(
        "external_api",
        max_retries=2,
        base_delay=2.0,
        strategy=RetryStrategy.EXPONENTIAL,
        exceptions=(Exception,)
    )(func)

def retry_database(func: Callable) -> Callable:
    """Retry decorator for database operations"""
    return retry_with_circuit_breaker(
        "database",
        max_retries=3,
        base_delay=0.5,
        strategy=RetryStrategy.LINEAR,
        exceptions=(Exception,)
    )(func)

# Utility functions
def get_circuit_breaker_status(service_name: str) -> Dict[str, Any]:
    """Get circuit breaker status for a service"""
    circuit_breaker = retry_manager.get_circuit_breaker(service_name)
    return {
        "service": service_name,
        "state": circuit_breaker.state.value,
        "failure_count": circuit_breaker.failure_count,
        "success_count": circuit_breaker.success_count,
        "last_failure_time": circuit_breaker.last_failure_time,
        "can_execute": circuit_breaker.can_execute()
    }

def reset_circuit_breaker(service_name: str):
    """Reset circuit breaker for a service"""
    if service_name in retry_manager.circuit_breakers:
        circuit_breaker = retry_manager.circuit_breakers[service_name]
        circuit_breaker.state = CircuitState.CLOSED
        circuit_breaker.failure_count = 0
        circuit_breaker.success_count = 0
        circuit_breaker.last_failure_time = None
        logger.info(f"Circuit breaker reset for {service_name}")

def get_all_circuit_breaker_status() -> Dict[str, Dict[str, Any]]:
    """Get status of all circuit breakers"""
    return {
        service_name: get_circuit_breaker_status(service_name)
        for service_name in retry_manager.circuit_breakers.keys()
    }
